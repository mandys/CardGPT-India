"""
Chat Streaming API endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, Request, BackgroundTasks, Header
from fastapi.responses import StreamingResponse
from models import ChatStreamRequest, StreamChunk
import logging
import time
import json
from typing import Optional

logger = logging.getLogger(__name__)
router = APIRouter()

# Global storage for streaming response data (session_id -> response_data)
streaming_responses = {}

def get_services():
    """Get services from app state"""
    from main import app_state
    return app_state

def get_session_id(request: Request, chat_request = None) -> str:
    """Extract session ID from request"""
    # First try to get from request body (used by streaming chat)
    if chat_request and hasattr(chat_request, 'session_id') and chat_request.session_id:
        return chat_request.session_id
    
    # Fallback to header
    session_id = request.headers.get('x-session-id')
    if not session_id:
        # Generate a default session ID if not provided
        session_id = f"session_{int(time.time())}"
    return session_id

async def get_user_preferences(request: Request, authorization: Optional[str] = None, chat_request = None):
    """Get user preferences from either authenticated user or session"""
    logger.info(f"🔍 [CHAT_PREFS] Getting user preferences - Auth: {'Present' if authorization else 'None'}")
    try:
        from main import app_state
        preference_service = app_state.get("preference_service")
        
        logger.info(f"🔍 [CHAT_PREFS] Services - Preference: {'Present' if preference_service else 'None'}")
        
        if not preference_service:
            logger.warning("⚠️ [CHAT_PREFS] No preference service available")
            return None
            
        # Use session preferences (Clerk authentication is handled on frontend)
        # For now, all preferences are session-based until we integrate Clerk user IDs
        session_id = get_session_id(request, chat_request)
        logger.info(f"🔍 [CHAT_PREFS] Getting session preferences for session: {session_id}")
        prefs = preference_service.get_session_preferences(session_id)
        logger.info(f"🔍 [CHAT_PREFS] Retrieved session preferences: {prefs}")
        return prefs
        
    except Exception as e:
        logger.error(f"❌ [CHAT_PREFS] Failed to get user preferences: {str(e)}", exc_info=True)
        return None

@router.post("/chat/stream")
async def chat_stream_endpoint(
    request: ChatStreamRequest, 
    http_request: Request, 
    background_tasks: BackgroundTasks, 
    services=Depends(get_services),
    authorization: Optional[str] = Header(None)
):
    """Streaming chat endpoint for real-time responses"""
    
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
        
        # Get user preferences
        user_preferences_obj = await get_user_preferences(http_request, authorization, request)
        # Convert Pydantic model to dictionary for LLM service
        user_preferences = user_preferences_obj.model_dump() if user_preferences_obj else None
        print(f"🔍 [STREAM] Retrieved user preferences: {user_preferences}")
        print(f"🔍 [STREAM] Authorization header passed: {'Present' if authorization else 'None'}")
        
        # Log query if logging is enabled (use same session ID for consistency)
        if query_logger and query_logger.config.enabled:
            session_id = await log_query_stream(query_logger, request, http_request)
        else:
            # Ensure we have a session ID even when logging is disabled
            session_id = get_session_id(http_request, request)
        
        # Card selector removed - process all queries directly for better user experience
        
        # Use search-focused query enhancement (no user preferences in search)
        enhanced_search_query, initial_metadata = query_enhancer_service.enhance_search_query(request.message)
        followup_questions = []  # Followup questions feature removed in simplified version
        
        # Process streaming query
        def generate_stream():
            try:
                # Process query using the same logic as regular chat  
                yield from process_query_stream(
                    question=request.message,
                    query_mode=request.query_mode,
                    card_filter=request.card_filter,
                    top_k=request.top_k,
                    selected_model=request.model,
                    llm_service=llm_service,
                    retriever_service=retriever_service,
                    query_enhancer_service=query_enhancer_service,
                    start_time=start_time,
                    session_id=session_id,
                    query_logger=query_logger,
                    followup_questions=followup_questions,
                    user_preferences=user_preferences,
                    pre_enhanced_query=enhanced_search_query,
                    pre_metadata=initial_metadata
                )
            except Exception as e:
                logger.error(f"Stream generation error: {str(e)}", exc_info=True)
                error_chunk = StreamChunk(
                    type="error",
                    content=f"Error: {str(e)}"
                )
                yield f"data: {error_chunk.model_dump_json()}\n\n"
                yield "data: [DONE]\n\n"
        
        # Add background task to log response after streaming completes
        if query_logger and session_id:
            background_tasks.add_task(log_streaming_response, query_logger, session_id, start_time)
        
        return StreamingResponse(
            generate_stream(), 
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/plain; charset=utf-8"
            }
        )
        
    except Exception as e:
        logger.error(f"Chat stream endpoint error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

def process_query_stream(
    question: str,
    query_mode: str,
    card_filter: str,
    top_k: int,
    selected_model: str,
    llm_service,
    retriever_service,
    query_enhancer_service,
    start_time: float,
    session_id: str,
    query_logger,
    followup_questions: list = None,
    user_preferences=None,
    pre_enhanced_query: str = None,
    pre_metadata: dict = None
):
    """Process streaming user query"""
    
    try:
        logger.info(f"Starting stream processing for: {question}")
        
        # Send initial status
        status_chunk = StreamChunk(
            type="status",
            content="Searching..."
        )
        yield f"data: {status_chunk.model_dump_json()}\n\n"
        
        # Use pre-enhanced query if available, otherwise enhance now
        if pre_enhanced_query and pre_metadata:
            enhanced_search_query, metadata = pre_enhanced_query, pre_metadata
            logger.info(f"Using pre-enhanced search query: {enhanced_search_query[:100]}...")
        else:
            # Use search-focused enhancement (no user preferences in search query)
            enhanced_search_query, metadata = query_enhancer_service.enhance_search_query(question)
        
        # Determine search filters and handle multiple cards in comparison queries
        search_card_filter = None
        if query_mode == "Specific Card" and card_filter and card_filter != "None":
            search_card_filter = card_filter
        elif metadata.get('card_detected'):
            search_card_filter = metadata['card_detected']
        
        # For comparison queries, remove card filter to get comprehensive results
        if metadata.get('is_comparison') or metadata.get('direct_comparison'):
            search_card_filter = None  # Search all cards for comparison
            logger.info(f"Detected comparison query - removing card filter for comprehensive search")
        
        # Use the enhanced query from query enhancer directly
        final_search_query = enhanced_search_query
        # Send search status
        search_status_chunk = StreamChunk(
            type="status",
            content="Processing..."
        )
        yield f"data: {search_status_chunk.model_dump_json()}\n\n"
        
        # Use default top_k - let semantic search work naturally
        search_top_k = top_k
        
        # Search documents
        logger.info(f"Searching documents with FINAL query: {final_search_query}")
        logger.info(f"Original query was: {question}")
        logger.info(f"QueryEnhancer output was: {enhanced_search_query}")
        relevant_docs = retriever_service.search_similar_documents(
            query_text=final_search_query,
            top_k=search_top_k,
            card_filter=search_card_filter,
            use_mmr=True
        )
        logger.info(f"Found {len(relevant_docs)} relevant documents")
        
        # Smart model selection for complex calculations
        is_complex_calculation = (
            metadata.get('is_calculation_query', False) and 
            any(word in question.lower() for word in ['yearly', 'annual', '7.5l', '750000'])
        )
        
        model_to_use = selected_model
        if is_complex_calculation and selected_model == "gpt-3.5-turbo":
            model_to_use = "gemini-1.5-pro" if llm_service.gemini_available else "gpt-4"
        
        # Generate streaming answer
        card_context = card_filter if query_mode == "Specific Card" and card_filter != "None" else None
        
        # Send generation status
        gen_status_chunk = StreamChunk(
            type="status", 
            content="Generating..."
        )
        yield f"data: {gen_status_chunk.model_dump_json()}\n\n"
        
        logger.info(f"Starting LLM streaming with model: {model_to_use}")
        
        # Enhanced Gemini optimizations are now integrated into the main LLM service
        # The regular LLM flow will use optimized prompts automatically
        logger.info(f"🎯 [LLM_CONTEXT] === PASSING TO LLM ===")
        logger.info(f"🎯 [LLM_CONTEXT] Original question: '{question}'")
        logger.info(f"🎯 [LLM_CONTEXT] User preferences: {user_preferences}")
        logger.info(f"🎯 [LLM_CONTEXT] User preferences will be integrated into LLM system prompt for personalization")
        
        for chunk_text, is_final, usage_info in llm_service.generate_answer_stream(
            question=question,  # Use original question, not search query
            context_documents=relevant_docs,
            card_name=card_context,
            model_choice=model_to_use,
            user_preferences=user_preferences
        ):
            logger.debug(f"Received chunk: is_final={is_final}, text_length={len(chunk_text) if chunk_text else 0}")
            if is_final:
                # Final chunk with complete information
                embedding_usage = {"tokens": 0, "cost": 0, "model": "vertex-ai-search"}
                total_cost = embedding_usage["cost"] + usage_info.get("cost", 0.0)
                
                # Add follow-up questions to the response if available
                final_content = chunk_text if chunk_text else None
                if followup_questions and final_content:
                    final_content += f"\n\n**💡 For more personalized recommendations, consider these details:**\n"
                    for i, q in enumerate(followup_questions, 1):
                        final_content += f"{i}. {q}\n"
                
                # Add follow-up questions to metadata
                final_metadata = metadata.copy() if metadata else {}
                if followup_questions:
                    final_metadata["followup_questions"] = followup_questions
                    final_metadata["query_type"] = "generic_recommendation"
                
                # CRITICAL: Add original query to metadata for frontend ambiguity detection
                final_metadata["original_query"] = question
                
                # Add user preference info to enhanced search query for debugging visibility
                debug_enhanced_question = enhanced_search_query
                
                final_chunk = StreamChunk(
                    type="complete",
                    content=final_content,
                    sources=[{
                        "cardName": doc.get("cardName", ""),
                        "section": doc.get("section", ""), 
                        "content": doc.get("content", ""),
                        "similarity": doc.get("similarity", 0.0)
                    } for doc in relevant_docs],
                    embedding_usage={
                        "tokens": embedding_usage["tokens"],
                        "cost": embedding_usage["cost"],
                        "model": embedding_usage["model"]
                    },
                    llm_usage={
                        "tokens": usage_info.get("total_tokens", 0),
                        "cost": usage_info.get("cost", 0.0),
                        "model": usage_info.get("model", "unknown"),
                        "input_tokens": usage_info.get("input_tokens"),
                        "output_tokens": usage_info.get("output_tokens"),
                        "total_tokens": usage_info.get("total_tokens", 0)
                    },
                    total_cost=total_cost,
                    enhanced_question=debug_enhanced_question,
                    metadata=final_metadata
                )
                
                yield f"data: {final_chunk.model_dump_json()}\n\n"
                
                # Store final result for logging outside generator
                if session_id:
                    streaming_responses[session_id] = {
                        "llm_usage": {
                            "tokens": usage_info.get("total_tokens", 0),
                            "total_tokens": usage_info.get("total_tokens", 0),
                            "cost": usage_info.get("cost", 0.0)
                        },
                        "documents": relevant_docs,
                        "status": 200
                    }
                logger.info(f"Streaming completed - tokens: {usage_info.get('total_tokens', 0)}, cost: {usage_info.get('cost', 0.0)}")
                
                break
            else:
                # Regular chunk
                if chunk_text:  # Only send non-empty chunks
                    chunk = StreamChunk(
                        type="chunk",
                        content=chunk_text
                    )
                    yield f"data: {chunk.model_dump_json()}\n\n"
        
        # Signal completion
        yield "data: [DONE]\n\n"
        
    except Exception as e:
        logger.error(f"Process query stream error: {str(e)}", exc_info=True)
        error_chunk = StreamChunk(
            type="error",
            content=f"Error processing query: {str(e)}"
        )
        yield f"data: {error_chunk.model_dump_json()}\n\n"
        yield "data: [DONE]\n\n"

# Helper functions for streaming query logging

async def log_query_stream(query_logger, request: ChatStreamRequest, http_request: Request) -> str:
    """Log the incoming streaming query"""
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
        logger.error(f"Failed to log streaming query: {e}")
        return "unknown-session"

async def log_streaming_response(query_logger, session_id: str, start_time: float):
    """Background task to log streaming response after completion"""
    import asyncio
    import time as time_module
    
    # Wait a bit for the stream to complete and store response data
    await asyncio.sleep(2)
    
    try:
        # Get stored response data
        response_data = streaming_responses.get(session_id)
        if not response_data:
            logger.warning(f"No response data found for session {session_id}")
            return
        
        # Calculate execution time
        execution_time_ms = int((time_module.time() - start_time) * 1000)
        
        # Import required models
        import sys
        sys.path.append('..')
        from logging_models.logging_models import ResponseLogData
        
        llm_usage = response_data.get("llm_usage", {})
        
        log_data = ResponseLogData(
            response_status=response_data.get("status", 200),
            execution_time_ms=execution_time_ms,
            llm_tokens_used=llm_usage.get("tokens", llm_usage.get("total_tokens", 0)),
            llm_cost=llm_usage.get("cost", 0.0),
            search_results_count=len(response_data.get("documents", []))
        )
        
        await query_logger.log_response(session_id, log_data)
        
        # Clean up stored data
        streaming_responses.pop(session_id, None)
        
        logger.info(f"Successfully logged streaming response for session {session_id}")
        
    except Exception as e:
        logger.error(f"Failed to log streaming response for session {session_id}: {e}")
        # Clean up on error
        streaming_responses.pop(session_id, None)

async def log_response_stream(query_logger, session_id: str, start_time: float, status_code: int, result: dict):
    """Log the streaming response metrics (legacy function)"""
    try:
        import sys
        import time
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
        logger.error(f"Failed to log streaming response: {e}")

def is_current_info_query(query: str) -> bool:
    """Detect if query asks for current/latest information"""
    current_keywords = [
        'latest', 'current', 'new', 'recent', 'today', 'this month', 
        'this year', '2024', '2025', 'now', 'currently', 'updated',
        'offer', 'promotion', 'bonus', 'deal', 'announcement',
        'devaluation', 'change', 'launch', 'launched'
    ]
    
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in current_keywords)

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