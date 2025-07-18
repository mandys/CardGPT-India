"""
Chat API endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from models import ChatRequest, ChatResponse, QueryEnhanceRequest, QueryEnhanceResponse, DocumentSource, UsageInfo
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

def get_services():
    """Get services from app state"""
    # This will be properly implemented when services are available
    from main import app_state
    return app_state

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, services=Depends(get_services)):
    """Main chat endpoint for processing user queries"""
    
    try:
        # Get services
        llm_service = services.get("llm_service")
        retriever_service = services.get("retriever_service")
        query_enhancer_service = services.get("query_enhancer_service")
        
        if not all([llm_service, retriever_service, query_enhancer_service]):
            raise HTTPException(status_code=503, detail="Services not available")
        
        # Check if this is a generic comparison query
        if query_enhancer_service.is_generic_comparison_query(request.message):
            available_cards = query_enhancer_service.get_available_cards()
            card_selection_prompt = f"""I noticed you're asking for a comparison without specifying which cards to compare. 

To provide you with the most accurate and focused comparison, please select 2-3 cards from our available options:

**Available Cards:**
{chr(10).join([f"• {card}" for card in available_cards])}

Which specific cards would you like me to compare for your query: "{request.message}"?

This approach will give you more precise results and save processing time."""
            
            return ChatResponse(
                answer=card_selection_prompt,
                sources=[],
                embedding_usage=UsageInfo(tokens=0, cost=0.0, model="none"),
                llm_usage=UsageInfo(tokens=0, cost=0.0, model="card-selection"),
                total_cost=0.0,
                enhanced_question=request.message,
                metadata={"requires_card_selection": True, "available_cards": available_cards, "original_query": request.message}
            )
        
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
        
        return ChatResponse(
            answer=result["answer"],
            sources=[DocumentSource(**doc) for doc in result["documents"]],
            embedding_usage=UsageInfo(**result["embedding_usage"]),
            llm_usage=UsageInfo(**result["llm_usage"]),
            total_cost=result["total_cost"],
            enhanced_question=result["enhanced_question"],
            metadata=result["metadata"]
        )
        
    except Exception as e:
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
        # Enhance the search query with relevant keywords for better document retrieval
        if any(keyword in question.lower() for keyword in ["hotel", "flight", "travel"]):
            question += " rewards earning rate points miles travel hotel flight"
        elif "insurance" in question.lower():
            question += " capping per statement cycle 5000 reward points MCC 6300 5960"
    
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