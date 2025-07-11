import streamlit as st
import requests
import json
from typing import Dict, List, Any
import time

# Configure Streamlit page
st.set_page_config(
    page_title="Credit Card RAG Assistant",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = st.secrets.get("API_BASE_URL", "http://localhost:3000/api")

def check_api_health() -> bool:
    """Check if the API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def get_available_cards() -> List[str]:
    """Get list of available credit cards"""
    try:
        response = requests.get(f"{API_BASE_URL}/cards", timeout=10)
        if response.status_code == 200:
            return response.json().get("cards", [])
    except:
        pass
    return []

def query_all_cards(question: str, top_k: int = 5) -> Dict[str, Any]:
    """Query all credit cards"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/query",
            json={"question": question, "topK": top_k},
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        return {"error": str(e)}
    return {"error": "Failed to get response"}

def query_specific_card(card_name: str, question: str, top_k: int = 5) -> Dict[str, Any]:
    """Query specific credit card"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/query/{card_name}",
            json={"question": question, "topK": top_k},
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        return {"error": str(e)}
    return {"error": "Failed to get response"}

def compare_cards(cards: List[str], question: str) -> Dict[str, Any]:
    """Compare multiple credit cards"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/compare",
            json={"question": question, "cards": cards},
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        return {"error": str(e)}
    return {"error": "Failed to get response"}

def vector_search(query: str, top_k: int = 5, threshold: float = 0.3) -> Dict[str, Any]:
    """Perform vector search"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/search",
            json={"query": query, "topK": top_k, "threshold": threshold},
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        return {"error": str(e)}
    return {"error": "Failed to get response"}

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "available_cards" not in st.session_state:
    st.session_state.available_cards = []

# Main UI
st.title("💳 Credit Card RAG Assistant")
st.markdown("Ask questions about Indian credit card terms and conditions")

# Sidebar
with st.sidebar:
    st.header("🔧 Configuration")
    
    # Check API status
    api_status = check_api_health()
    if api_status:
        st.success("✅ API Connected")
        # Get available cards
        if not st.session_state.available_cards:
            st.session_state.available_cards = get_available_cards()
    else:
        st.error("❌ API Disconnected")
        st.warning("Make sure to run: `npm run dev` in your project directory")
    
    st.divider()
    
    # Query Mode Selection
    st.header("🎯 Query Mode")
    query_mode = st.selectbox(
        "Select query mode:",
        ["General Query", "Specific Card", "Compare Cards", "Vector Search"]
    )
    
    # Card selection based on mode
    selected_cards = []
    if query_mode == "Specific Card" and st.session_state.available_cards:
        selected_card = st.selectbox(
            "Select a card:",
            st.session_state.available_cards
        )
        selected_cards = [selected_card]
    elif query_mode == "Compare Cards" and st.session_state.available_cards:
        selected_cards = st.multiselect(
            "Select cards to compare:",
            st.session_state.available_cards,
            default=st.session_state.available_cards[:2] if len(st.session_state.available_cards) >= 2 else []
        )
    
    # Advanced settings
    st.header("⚙️ Advanced Settings")
    top_k = st.slider("Number of results (top_k)", 1, 10, 5)
    
    if query_mode == "Vector Search":
        threshold = st.slider("Similarity threshold", 0.0, 1.0, 0.3, 0.1)
    
    # Available cards display
    if st.session_state.available_cards:
        st.header("📋 Available Cards")
        for card in st.session_state.available_cards:
            st.write(f"• {card}")
    
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
        if "sources" in message:
            with st.expander("📚 Sources"):
                for i, source in enumerate(message["sources"]):
                    st.write(f"**{i+1}. {source['cardName']} - {source['section']}**")
                    st.write(source['content'])
                    st.divider()

# Chat input
if prompt := st.chat_input("Ask about credit card terms and conditions..."):
    if not api_status:
        st.error("API is not connected. Please start the backend server first.")
        st.stop()
    
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Call appropriate API based on query mode
                if query_mode == "General Query":
                    result = query_all_cards(prompt, top_k)
                elif query_mode == "Specific Card" and selected_cards:
                    result = query_specific_card(selected_cards[0], prompt, top_k)
                elif query_mode == "Compare Cards" and len(selected_cards) >= 2:
                    result = compare_cards(selected_cards, prompt)
                elif query_mode == "Vector Search":
                    result = vector_search(prompt, top_k, threshold)
                else:
                    result = {"error": "Please select appropriate options in the sidebar"}
                
                if "error" in result:
                    st.error(f"Error: {result['error']}")
                    response_text = f"Sorry, I encountered an error: {result['error']}"
                    sources = []
                elif query_mode == "Vector Search":
                    response_text = f"Found {len(result.get('results', []))} relevant results:"
                    sources = result.get('results', [])
                    for i, res in enumerate(sources):
                        st.write(f"**{i+1}. {res['cardName']} - {res['section']}** (Score: {res['score']:.3f})")
                        st.write(res['content'])
                        st.divider()
                else:
                    response_text = result.get('answer', 'No answer provided')
                    sources = result.get('sources', [])
                    
                    if sources:
                        with st.expander("📚 Sources"):
                            for i, source in enumerate(sources):
                                st.write(f"**{i+1}. {source['cardName']} - {source['section']}**")
                                st.write(source['content'])
                                st.divider()
                
                if query_mode != "Vector Search":
                    st.markdown(response_text)
                
                # Add assistant response to chat
                assistant_message = {
                    "role": "assistant", 
                    "content": response_text
                }
                if sources:
                    assistant_message["sources"] = sources
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
            "What are the fuel surcharge waivers?",
            "How does the reward points system work?",
            "What are the overlimit charges?",
            "What fees apply to EMI conversions?"
        ]
        
        for question in card_questions:
            if st.button(question, key=f"card_{question}"):
                st.session_state.messages.append({"role": "user", "content": question})
                st.rerun()

# Footer
st.divider()
st.markdown("---")
st.markdown("🚀 **Supavec Clone** - RAG-powered Credit Card Assistant | Built with Streamlit")