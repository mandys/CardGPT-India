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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Streamlit page
st.set_page_config(
    page_title="Credit Card RAG Assistant",
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


@st.cache_resource
def initialize_services():
    """Initialize all services with proper caching"""
    # Get OpenAI API key
    api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("OpenAI API key not found. Please set it in Streamlit secrets or environment variables.")
        st.stop()
    
    # Initialize services
    embedder = EmbeddingService(api_key)
    llm = LLMService(api_key)
    retriever = DocumentRetriever()
    
    return embedder, llm, retriever


@st.cache_data
def load_and_process_data(_retriever, _embedder):
    """Load documents and generate embeddings with caching"""
    with st.spinner("Loading credit card data..."):
        # Load documents
        documents = _retriever.load_documents_from_json("data")
        st.write(f"📄 Loaded {len(documents)} documents")
        
        # Generate embeddings
        st.write("🔄 Generating embeddings (this may take 30-60 seconds)...")
        embeddings, usage = _embedder.generate_batch_embeddings(documents)
        
        # Store in retriever
        _retriever.store_documents_and_embeddings(documents, embeddings)
        
        st.success(f"✅ Ready! Generated embeddings for {usage['successful_embeddings']} documents")
        st.write(f"💰 Embedding cost: ${usage['total_cost']:.4f}")
        
        return _retriever.get_available_cards(), usage


def process_query(
    question: str, 
    query_mode: str, 
    selected_cards: List[str], 
    top_k: int, 
    use_cheaper_model: bool,
    retriever: DocumentRetriever,
    embedder: EmbeddingService,
    llm: LLMService
) -> Dict[str, Any]:
    """Process a user query and return results"""
    
    # Generate query embedding
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
    
    # Search for relevant documents
    relevant_docs = retriever.search_similar_documents(
        query_embedding=query_embedding,
        top_k=top_k,
        card_filter=card_filter,
        boost_keywords=boost_keywords
    )
    
    # Filter for comparison mode
    if query_mode == "Compare Cards" and len(selected_cards) >= 2:
        relevant_docs = [doc for doc in relevant_docs if doc['cardName'] in selected_cards]
    
    # Generate answer
    card_context = selected_cards[0] if query_mode == "Specific Card" and selected_cards else None
    answer, llm_usage = llm.generate_answer(
        question=question,
        context_documents=relevant_docs,
        card_name=card_context,
        use_gpt4=not use_cheaper_model
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


def main():
    """Main application function"""
    
    # Initialize services
    embedder, llm, retriever = initialize_services()
    
    # Store in session state
    st.session_state.embedder = embedder
    st.session_state.llm = llm
    st.session_state.retriever = retriever
    
    # Load and process data
    available_cards, _ = load_and_process_data(retriever, embedder)
    
    # Main UI
    st.title("💳 Credit Card RAG Assistant")
    st.markdown("Ask questions about Indian credit card terms and conditions")
    
    # Sidebar configuration
    with st.sidebar:
        st.header("🔧 Configuration")
        st.success("✅ Standalone Mode Active")
        st.info(f"Loaded documents from {len(available_cards)} cards")
        
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
        top_k = st.slider("Number of results (top_k)", 1, 10, 7, 
                         help="More results = higher cost but better accuracy for calculations")
        
        # Model selection for cost optimization
        st.subheader("💰 Cost Optimization")
        use_cheaper_model = st.checkbox("Use GPT-3.5-turbo (10x cheaper)", 
                                       help="GPT-3.5-turbo costs ~$0.01-0.03 per query vs GPT-4's $0.10-0.30")
        
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
    st.header("💬 Chat Interface")
    
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
                try:
                    # Process the query
                    result = process_query(
                        question=prompt,
                        query_mode=query_mode,
                        selected_cards=selected_cards,
                        top_k=top_k,
                        use_cheaper_model=use_cheaper_model,
                        retriever=retriever,
                        embedder=embedder,
                        llm=llm
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
    
    # Example questions
    if not st.session_state.messages:
        st.header("💡 Example Questions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("General Questions")
            example_questions = [
                "What are the interest rates for credit cards?",
                "Compare cash withdrawal fees between cards",
                "What surcharge fees apply to international transactions?",
                "What are the minimum payment requirements?"
            ]
            
            for question in example_questions:
                if st.button(question, key=f"general_{question}"):
                    st.session_state.messages.append({"role": "user", "content": question})
                    st.rerun()
        
        with col2:
            st.subheader("Card-Specific Questions")
            card_questions = [
                "For a yearly spend of 7.5L on Atlas, how many miles i earn?",
                "What are the fuel surcharge waivers?",
                "How does the reward points system work?",
                "What are the overlimit charges?"
            ]
            
            for question in card_questions:
                if st.button(question, key=f"card_{question}"):
                    st.session_state.messages.append({"role": "user", "content": question})
                    st.rerun()
    
    # Footer
    st.divider()
    st.markdown("---")
    st.markdown("🚀 **Supavec Clone** - Modular RAG-powered Credit Card Assistant | Built with Streamlit")


if __name__ == "__main__":
    main()