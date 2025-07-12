"""
Supavec Clone - Main Streamlit Application
RAG-powered Credit Card Assistant for Indian Credit Card Data
"""

import streamlit as st
import os
import logging
from typing import List, Dict, Any

# Import our custom services
from src.embedder import EmbeddingService
from src.llm import LLMService
from src.retriever import DocumentRetriever
from src.query_enhancer import QueryEnhancer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Streamlit page
st.set_page_config(
    page_title="Credit Card Assistant",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "retriever" not in st.session_state:
    st.session_state.retriever = None
if "embedder" not in st.session_state:
    st.session_state.embedder = None
if "llm" not in st.session_state:
    st.session_state.llm = None
if "process_last_message" not in st.session_state:
    st.session_state.process_last_message = False


@st.cache_resource
def initialize_services():
    """Initialize all services with proper caching"""
    # Get OpenAI API key
    api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("OpenAI API key not found. Please set it in Streamlit secrets or environment variables.")
        st.stop()
    
    # Get Gemini API key (optional)
    gemini_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
    
    # Initialize services
    embedder = EmbeddingService(api_key)
    llm = LLMService(api_key, gemini_key)
    retriever = DocumentRetriever()
    query_enhancer = QueryEnhancer()
    
    return embedder, llm, retriever, query_enhancer


@st.cache_data
def load_and_process_data(_retriever, _embedder):
    """Load documents and generate embeddings with caching"""
    with st.spinner("Initializing AI assistant..."):
        # Load documents
        documents = _retriever.load_documents_from_json("data")
        
        # Generate embeddings
        embeddings, usage = _embedder.generate_batch_embeddings(documents)
        
        # Store in retriever
        _retriever.store_documents_and_embeddings(documents, embeddings)
        
        return _retriever.get_available_cards(), usage


def process_query(
    question: str, 
    query_mode: str, 
    selected_cards: List[str], 
    top_k: int, 
    selected_model: str,
    retriever: DocumentRetriever,
    embedder: EmbeddingService,
    llm: LLMService,
    query_enhancer: QueryEnhancer
) -> Dict[str, Any]:
    """Process a user query and return results"""
    
    # Enhance query with category detection
    enhanced_question, metadata = query_enhancer.enhance_query(question)
    
    # Log category detection if found
    if metadata['category_detected']:
        logger.info(f"Category detected: {metadata['category_detected']} for question: {question[:50]}...")
    
    # Generate query embedding (use original question for embedding to maintain search accuracy)
    query_embedding, embedding_usage = embedder.generate_single_embedding(question)
    
    # Determine search filters
    card_filter = None
    if query_mode == "Specific Card" and selected_cards:
        card_filter = selected_cards[0]
    elif query_mode == "Compare Cards" and len(selected_cards) >= 2:
        # For comparison, we'll search across all selected cards
        pass
    
    # Apply keyword boosting for spend-related queries
    boost_keywords = []
    if any(keyword in question.lower() for keyword in ['spend', 'earn', 'miles', 'points', 'yearly', 'annual']):
        boost_keywords = ['reward', 'milestone']
    
    # Check if question implies comparison (both cards, compare, etc.)
    comparison_keywords = ['both cards', 'compare', 'better', 'which card', 'icici and atlas', 'atlas and icici']
    is_comparison_question = any(keyword in question.lower() for keyword in comparison_keywords)
    
    # Search for relevant documents
    relevant_docs = retriever.search_similar_documents(
        query_embedding=query_embedding,
        top_k=top_k,
        card_filter=card_filter,
        boost_keywords=boost_keywords
    )
    
    # Filter for comparison mode or auto-detected comparison questions
    if query_mode == "Compare Cards" and len(selected_cards) >= 2:
        relevant_docs = [doc for doc in relevant_docs if doc['cardName'] in selected_cards]
    elif is_comparison_question and query_mode == "General Query":
        # For general queries that are actually comparisons, ensure we get docs from both cards
        card_names = set([doc['cardName'] for doc in relevant_docs])
        if len(card_names) < 2:
            # If we only got docs from one card, boost the search to include both
            relevant_docs = retriever.search_similar_documents(
                query_embedding=query_embedding,
                top_k=top_k * 2,  # Double the search to ensure both cards
                card_filter=None,
                boost_keywords=boost_keywords
            )
    
    # Smart model selection for complex calculations
    is_complex_calculation = (
        metadata.get('is_calculation_query', False) and 
        (any(word in question.lower() for word in ['yearly', 'annual', '7.5l', '750000', 'split', 'distribution']) or
         metadata.get('spend_amount') and float(metadata.get('spend_amount', '0').replace(',', '')) > 500000)
    )
    
    # Auto-upgrade to better models for complex calculations
    model_to_use = selected_model
    if is_complex_calculation and selected_model == "gpt-3.5-turbo":
        # Auto-upgrade to Gemini Pro if available, otherwise GPT-4
        if llm.gemini_available:
            model_to_use = "gemini-1.5-pro"
        else:
            model_to_use = "gpt-4"
        logger.info(f"Auto-upgraded to {model_to_use} for complex calculation: {question[:50]}...")
    
    # Generate answer using enhanced question
    card_context = selected_cards[0] if query_mode == "Specific Card" and selected_cards else None
    answer, llm_usage = llm.generate_answer(
        question=enhanced_question,  # Use enhanced question for LLM
        context_documents=relevant_docs,
        card_name=card_context,
        model_choice=model_to_use
    )
    
    # Calculate total cost
    total_cost = embedding_usage["cost"] + llm_usage["cost"]
    
    return {
        "answer": answer,
        "documents": relevant_docs,
        "embedding_usage": embedding_usage,
        "llm_usage": llm_usage,
        "total_cost": total_cost
    }


def process_and_display_query(prompt, query_mode, selected_cards, top_k, selected_model, retriever, embedder, llm, query_enhancer):
    """Process a query and display the results"""
    try:
        # Process the query
        result = process_query(
            question=prompt,
            query_mode=query_mode,
            selected_cards=selected_cards,
            top_k=top_k,
            selected_model=selected_model,
            retriever=retriever,
            embedder=embedder,
            llm=llm,
            query_enhancer=query_enhancer
        )
        
        # Display answer
        st.markdown(result["answer"])
        
        # Display usage metrics
        with st.expander("💰 Token Usage & Cost"):
            col1, col2 = st.columns(2)
            with col1:
                st.metric("🔍 Query Embedding", 
                        f"{result['embedding_usage']['tokens']} tokens", 
                        f"${result['embedding_usage']['cost']:.6f}")
            with col2:
                model_name = result['llm_usage'].get('model', 'unknown')
                st.metric(f"🤖 {model_name}", 
                        f"{result['llm_usage'].get('total_tokens', 0)} tokens", 
                        f"${result['llm_usage'].get('cost', 0):.4f}")
            
            st.metric("💸 **Total Cost**", f"${result['total_cost']:.4f}", 
                    help="This is the cost for this single query")
            
            if result['llm_usage'].get('total_tokens', 0) > 0:
                st.write(f"📊 {result['llm_usage'].get('model', 'unknown')} Details: "
                       f"{result['llm_usage']['input_tokens']} input + "
                       f"{result['llm_usage']['output_tokens']} output tokens")
        
        # Display sources
        if result["documents"]:
            with st.expander("📚 Sources"):
                for i, doc in enumerate(result["documents"]):
                    st.write(f"**{i+1}. {doc['cardName']} - {doc['section']}** "
                           f"(Similarity: {doc.get('similarity', 0):.3f})")
                    st.write(doc['content'])
                    st.divider()
        
        # Add assistant response to chat
        assistant_message = {
            "role": "assistant",
            "content": result["answer"],
            "sources": result["documents"],
            "usage": {
                "embedding": result["embedding_usage"],
                "llm": result["llm_usage"],
                "total_cost": result["total_cost"]
            }
        }
        st.session_state.messages.append(assistant_message)
        
    except Exception as e:
        error_msg = f"An error occurred: {str(e)}"
        st.error(error_msg)
        st.session_state.messages.append({"role": "assistant", "content": error_msg})


def main():
    """Main application function"""
    
    # Initialize services
    embedder, llm, retriever, query_enhancer = initialize_services()
    
    # Store in session state
    st.session_state.embedder = embedder
    st.session_state.llm = llm
    st.session_state.retriever = retriever
    st.session_state.query_enhancer = query_enhancer
    
    # Load and process data
    available_cards, _ = load_and_process_data(retriever, embedder)
    
    # Main UI
    st.title("💳 Credit Card Assistant")
    st.markdown("Ask questions about Indian credit card terms and conditions")
    
    # Sidebar configuration
    with st.sidebar:
        st.header("🎯 Query Settings")
        st.info(f"📊 {len(available_cards)} credit cards loaded")
        
        st.divider()
        
        # Query Mode Selection
        st.header("🎯 Query Mode")
        query_mode = st.selectbox(
            "Select query mode:",
            ["General Query", "Specific Card", "Compare Cards"]
        )
        
        # Card selection based on mode
        selected_cards = []
        if query_mode == "Specific Card":
            selected_card = st.selectbox("Select a card:", available_cards)
            selected_cards = [selected_card]
        elif query_mode == "Compare Cards":
            selected_cards = st.multiselect(
                "Select cards to compare:",
                available_cards,
                default=available_cards[:2] if len(available_cards) >= 2 else []
            )
        
        # Advanced settings
        st.header("⚙️ Advanced Settings")
        top_k = st.slider("Number of results (top_k)", 1, 10, 4, 
                         help="More results = higher cost but better accuracy for calculations")
        
        # Model selection for cost optimization
        st.subheader("🤖 Model Selection")
        
        # Check if Gemini is available
        gemini_available = st.session_state.llm.gemini_available if hasattr(st.session_state, 'llm') else False
        
        model_options = ["gpt-3.5-turbo", "gpt-4"]
        if gemini_available:
            model_options.extend(["gemini-1.5-flash", "gemini-1.5-pro"])
        
        # Set default to Gemini Flash if available, otherwise GPT-3.5
        default_index = 0
        if gemini_available and "gemini-1.5-flash" in model_options:
            default_index = model_options.index("gemini-1.5-flash")
        
        selected_model = st.selectbox(
            "Choose AI model:",
            model_options,
            index=default_index,
            help="GPT-3.5: $0.002, GPT-4: $0.06, Gemini Flash: $0.0003 (20x cheaper!), Gemini Pro: $0.005"
        )
        
        # Show cost comparison
        cost_info = {
            "gpt-3.5-turbo": "$0.002 per query",
            "gpt-4": "$0.06 per query", 
            "gemini-1.5-flash": "$0.0003 per query (20x cheaper!)",
            "gemini-1.5-pro": "$0.005 per query"
        }
        
        if selected_model in cost_info:
            st.info(f"💰 Expected cost: {cost_info[selected_model]}")
        
        # Available cards display
        st.header("📋 Available Cards")
        for card in available_cards:
            st.write(f"• {card}")
        
        # Session cost tracking
        st.header("💰 Session Costs")
        session_cost = sum([msg.get("usage", {}).get("total_cost", 0) for msg in st.session_state.messages])
        if session_cost > 0:
            st.metric("Total Session Cost", f"${session_cost:.4f}")
            st.write(f"📊 Queries: {len([m for m in st.session_state.messages if m['role'] == 'assistant'])}")
        else:
            st.write("No queries yet")
        
        # Clear chat button
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()
    
    # Main chat interface
    st.header("💬 Ask Your Questions")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "usage" in message:
                with st.expander("💰 Cost Breakdown"):
                    usage = message["usage"]
                    st.write(f"💸 **Total Cost**: ${usage['total_cost']:.4f}")
                    st.write(f"🔍 Embedding: {usage['embedding']['tokens']} tokens (${usage['embedding']['cost']:.6f})")
                    st.write(f"🤖 {usage['llm'].get('model', 'unknown')}: {usage['llm'].get('total_tokens', 0)} tokens (${usage['llm'].get('cost', 0):.4f})")
            if "sources" in message:
                with st.expander("📚 Sources"):
                    for i, source in enumerate(message["sources"]):
                        st.write(f"**{i+1}. {source['cardName']} - {source['section']}** (Similarity: {source.get('similarity', 0):.3f})")
                        st.write(source['content'])
                        st.divider()
    
    # Chat input
    if prompt := st.chat_input("Ask about credit card terms and conditions..."):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                process_and_display_query(prompt, query_mode, selected_cards, top_k, selected_model, retriever, embedder, llm, query_enhancer)
    
    # Check if there's a new user message that needs processing (from example buttons)
    if (hasattr(st.session_state, 'process_last_message') and 
        st.session_state.process_last_message and 
        st.session_state.messages and 
        st.session_state.messages[-1]["role"] == "user"):
        
        prompt = st.session_state.messages[-1]["content"]
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                process_and_display_query(prompt, query_mode, selected_cards, top_k, selected_model, retriever, embedder, llm, query_enhancer)
        
        # Clear the flag
        st.session_state.process_last_message = False
    
    # Example questions
    if not st.session_state.messages:
        st.header("💡 Example Questions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("General Questions")
            example_questions = [
                "What are the annual fees for credit cards?",
                "Compare reward rates between cards",
                "What are the airport lounge access benefits?",
                "What are the eligibility requirements for credit cards?"
            ]
            
            for question in example_questions:
                if st.button(question, key=f"general_{question}"):
                    # Add to chat and trigger processing
                    st.session_state.messages.append({"role": "user", "content": question})
                    # Set a flag to process the question
                    st.session_state.process_last_message = True
                    st.rerun()
        
        with col2:
            st.subheader("Card-Specific Questions")
            card_questions = [
                "What are the welcome benefits for Axis Atlas?",
                "What are the rewards and fees for utility payments on ICICI EPM?",
                "What are the rewards and fees for fuel purchases on Axis Atlas?",
                "What travel benefits does Axis Atlas offer?"
            ]
            
            for question in card_questions:
                if st.button(question, key=f"card_{question}"):
                    # Add to chat and trigger processing
                    st.session_state.messages.append({"role": "user", "content": question})
                    # Set a flag to process the question
                    st.session_state.process_last_message = True
                    st.rerun()
    
    # Footer
    st.divider()
    st.markdown("---")
    st.markdown("💳 **Credit Card Assistant** - Built by @maharajamandy | Powered by OpenAI")


if __name__ == "__main__":
    main()