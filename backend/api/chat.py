"""
Chat API endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from models import ChatRequest, ChatResponse, QueryEnhanceRequest, QueryEnhanceResponse, DocumentSource, UsageInfo
import logging
import time

logger = logging.getLogger(__name__)

router = APIRouter()

def get_services():
    """Get services from app state"""
    # This will be properly implemented when services are available
    from main import app_state
    return app_state

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, http_request: Request, services=Depends(get_services)):
    """Main chat endpoint for processing user queries"""
    
    start_time = time.time()
    session_id = None
    
    try:
        # Get services
        llm_service = services.get("llm_service")
        retriever_service = services.get("retriever_service")
        query_enhancer_service = services.get("query_enhancer_service")
        query_logger = services.get("query_logger")
        
        if not all([llm_service, retriever_service, query_enhancer_service]):
            raise HTTPException(status_code=503, detail="Services not available")
        
        # Log query if logging is enabled
        if query_logger and query_logger.config.enabled:
            session_id = await log_query(query_logger, request, http_request)
        
        # Card selector removed - process all queries directly
        
        # Check if we should suggest follow-up questions for generic queries
        enhanced_query, initial_metadata = query_enhancer_service.enhance_query(request.message)
        
        if initial_metadata.get('suggest_followup', False):
            # For generic queries, we can either suggest follow-ups OR provide a comprehensive answer
            # Let's provide comprehensive answer with suggested follow-ups in metadata
            followup_questions = query_enhancer_service.get_followup_questions(request.message)
            
            # Process the query normally but add follow-up questions to metadata
            result = await process_query(
                question=request.message,
                query_mode=request.query_mode,
                card_filter=request.card_filter,
                top_k=request.top_k,
                selected_model=request.model,
                llm_service=llm_service,
                retriever_service=retriever_service,
                query_enhancer_service=query_enhancer_service
            )
            
            # Add follow-up questions to metadata
            result["metadata"]["followup_questions"] = followup_questions
            result["metadata"]["query_type"] = "generic_recommendation"
            
            # Enhance the answer with a note about follow-up questions
            if followup_questions:
                result["answer"] += f"\n\n**💡 For more personalized recommendations, consider these details:**\n"
                for i, q in enumerate(followup_questions, 1):
                    result["answer"] += f"{i}. {q}\n"
        else:
            # Process query using the same logic as the existing apps
            result = await process_query(
                question=request.message,
                query_mode=request.query_mode,
                card_filter=request.card_filter,
                top_k=request.top_k,
                selected_model=request.model,
                llm_service=llm_service,
                retriever_service=retriever_service,
                query_enhancer_service=query_enhancer_service
            )
        
        response = ChatResponse(
            answer=result["answer"],
            sources=[DocumentSource(**doc) for doc in result["documents"]],
            embedding_usage=UsageInfo(**result["embedding_usage"]),
            llm_usage=UsageInfo(**result["llm_usage"]),
            total_cost=result["total_cost"],
            enhanced_question=result["enhanced_question"],
            metadata=result["metadata"]
        )
        
        # Log response metrics
        if query_logger and session_id:
            await log_response(query_logger, session_id, start_time, 200, result)
            
        return response
        
    except Exception as e:
        # Log error response if we have session_id
        if query_logger and session_id:
            try:
                await log_response(query_logger, session_id, start_time, 500, {})
            except:
                pass  # Don't let logging failures break error handling
        
        logger.error(f"Chat endpoint error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

async def process_query(
    question: str,
    query_mode: str,
    card_filter: str,
    top_k: int,
    selected_model: str,
    llm_service,
    retriever_service,
    query_enhancer_service
):
    """Process user query - same logic as existing apps"""
    
    # Enhance query
    enhanced_question, metadata = query_enhancer_service.enhance_query(question)
    
    # No separate embedding costs for Vertex AI
    embedding_usage = {"tokens": 0, "cost": 0, "model": "vertex-ai-search"}
    
    # Determine search filters and handle multiple cards in comparison queries
    search_card_filter = None
    if query_mode == "Specific Card" and card_filter and card_filter != "None":
        search_card_filter = card_filter
    elif metadata.get('card_detected'):
        search_card_filter = metadata['card_detected']
    
    # For comparison queries mentioning multiple cards, search without filter to get all cards
    if "compare" in question.lower() and any(card in question.lower() for card in ["atlas", "icici", "epm", "hsbc", "premier"]):
        search_card_filter = None  # Search all cards for comparison
        
        # Boost search with actual card names for better document retrieval
        card_names_to_boost = []
        question_lower = question.lower()
        if any(pattern in question_lower for pattern in ["axis", "atlas"]):
            card_names_to_boost.append("Axis Bank Atlas Credit Card")
        if any(pattern in question_lower for pattern in ["icici", "epm", "emeralde"]):
            card_names_to_boost.append("ICICI Bank Emeralde Private Metal Credit Card")
        if any(pattern in question_lower for pattern in ["hsbc", "premier"]):
            card_names_to_boost.append("HSBC Premier Credit Card")
            
        # Add card names to search query for better retrieval
        if card_names_to_boost:
            question += f" {' '.join(card_names_to_boost)}"
            
        # Add card-specific reward terminology for better search targeting
        question_lower = question.lower()
        if any(pattern in question_lower for pattern in ["axis", "atlas"]):
            question += " EDGE Miles earning rate"
        if any(pattern in question_lower for pattern in ["icici", "epm"]):
            question += " Reward Points earning rate"
        if any(pattern in question_lower for pattern in ["hsbc", "premier"]):
            question += " Reward points earning rate"
        
        # Enhance the search query with relevant keywords for better document retrieval
        if any(keyword in question.lower() for keyword in ["hotel", "flight", "travel"]):
            question += " rewards earning rate points miles travel hotel flight"
        elif "insurance" in question.lower():
            question += " capping per statement cycle 5000 reward points MCC 6300 5960"
    
    # Enhance search for calculation queries to include milestone data
    if metadata.get('is_calculation_query', False):
        question += " milestone spend threshold bonus benefits"
    
    # Search documents
    relevant_docs = retriever_service.search_similar_documents(
        query_text=question,
        top_k=top_k,
        card_filter=search_card_filter,
        use_mmr=True
    )
    
    # Smart model selection for complex calculations
    is_complex_calculation = (
        metadata.get('is_calculation_query', False) and 
        any(word in question.lower() for word in ['yearly', 'annual', '7.5l', '750000'])
    )
    
    model_to_use = selected_model
    if is_complex_calculation and selected_model == "gpt-3.5-turbo":
        model_to_use = "gemini-1.5-pro" if llm_service.gemini_available else "gpt-4"
    
    # Generate answer
    card_context = card_filter if query_mode == "Specific Card" and card_filter != "None" else None
    answer, llm_usage = llm_service.generate_answer(
        question=enhanced_question,
        context_documents=relevant_docs,
        card_name=card_context,
        model_choice=model_to_use
    )
    
    total_cost = embedding_usage["cost"] + llm_usage["cost"]
    
    return {
        "answer": answer,
        "documents": relevant_docs,
        "embedding_usage": embedding_usage,
        "llm_usage": llm_usage,
        "total_cost": total_cost,
        "enhanced_question": enhanced_question,
        "metadata": metadata
    }

@router.post("/query/enhance", response_model=QueryEnhanceResponse)
async def enhance_query_endpoint(request: QueryEnhanceRequest, services=Depends(get_services)):
    """Enhance user query (optional endpoint for debugging)"""
    
    try:
        query_enhancer_service = services.get("query_enhancer_service")
        
        if not query_enhancer_service:
            raise HTTPException(status_code=503, detail="Query enhancer service not available")
        
        enhanced_query, metadata = query_enhancer_service.enhance_query(request.query)
        
        return QueryEnhanceResponse(
            enhanced_query=enhanced_query,
            metadata=metadata
        )
        
    except Exception as e:
        logger.error(f"Query enhance endpoint error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Helper functions for query logging

async def log_query(query_logger, request: ChatRequest, http_request: Request) -> str:
    """Log the incoming query"""
    try:
        import sys
        sys.path.append('..')
        from logging_models.logging_models import QueryLogData
        
        # Extract user context
        user_ip = get_client_ip(http_request)
        user_agent = http_request.headers.get("user-agent", "")
        
        # Create log data
        query_data = QueryLogData(
            query_text=request.message,
            selected_model=request.model,
            query_mode=request.query_mode,
            card_filter=request.card_filter,
            top_k=request.top_k,
            user_ip=user_ip,
            user_agent=user_agent
        )
        
        session_id = await query_logger.log_query(query_data)
        return session_id
        
    except Exception as e:
        logger.error(f"Failed to log query: {e}")
        return "unknown-session"

async def log_response(query_logger, session_id: str, start_time: float, status_code: int, result: dict):
    """Log the response metrics"""
    try:
        import sys
        sys.path.append('..')
        from logging_models.logging_models import ResponseLogData
        
        execution_time_ms = int((time.time() - start_time) * 1000)
        llm_usage = result.get("llm_usage", {})
        
        response_data = ResponseLogData(
            response_status=status_code,
            execution_time_ms=execution_time_ms,
            llm_tokens_used=llm_usage.get("tokens", llm_usage.get("total_tokens", 0)),
            llm_cost=llm_usage.get("cost", 0.0),
            search_results_count=len(result.get("documents", []))
        )
        
        await query_logger.log_response(session_id, response_data)
        
    except Exception as e:
        logger.error(f"Failed to log response: {e}")

def get_client_ip(request: Request) -> str:
    """Extract client IP address from request"""
    # Check for forwarded headers (for reverse proxies)
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip
    
    # Fallback to direct client
    return request.client.host if request.client else "unknown"