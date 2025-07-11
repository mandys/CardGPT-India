import streamlit as st
import openai
import json
import os
from typing import Dict, List, Any
import numpy as np
from pathlib import Path

# Configure Streamlit page
st.set_page_config(
    page_title="Credit Card RAG Assistant",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize OpenAI client
@st.cache_resource
def init_openai_client():
    """Initialize OpenAI client"""
    api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("OpenAI API key not found. Please set it in Streamlit secrets or environment variables.")
        st.stop()
    return openai.OpenAI(api_key=api_key)

@st.cache_data
def load_credit_card_data():
    """Load credit card data from JSON files"""
    data_dir = Path("data")
    if not data_dir.exists():
        st.error("Data directory not found. Please ensure the 'data' folder exists with credit card JSON files.")
        st.stop()
    
    json_files = list(data_dir.glob("*.json"))
    
    documents = []
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                card_data = json.load(f)
                card_name = json_file.stem.replace('-', ' ').title()
                
                # Process common_terms
                common_terms = card_data.get("common_terms", {})
                
                for section, data in common_terms.items():
                    content = format_section_content(section, data)
                    documents.append({
                        "id": f"{card_name}_common_{section}",
                        "cardName": card_name,
                        "content": content,
                        "section": f"common_terms_{section}",
                        "metadata": {
                            "section": f"common_terms_{section}",
                            "cardType": card_name
                        }
                    })
                
                # Process card-specific data (rewards, benefits, etc.)
                card_info = card_data.get("card", {})
                if card_info:
                    # Process each major section in card info
                    for section, data in card_info.items():
                        if isinstance(data, dict) and section not in ["id", "name", "bank", "category", "network", "launch_date"]:
                            content = format_section_content(section, data)
                            documents.append({
                                "id": f"{card_name}_card_{section}",
                                "cardName": card_name,
                                "content": content,
                                "section": section,
                                "metadata": {
                                    "section": section,
                                    "cardType": card_name
                                }
                            })
                        elif section in ["fees", "rewards", "reward_capping", "milestones", "insurance"]:
                            # These are important sections even if not dict
                            content = format_section_content(section, data)
                            documents.append({
                                "id": f"{card_name}_card_{section}",
                                "cardName": card_name,
                                "content": content,
                                "section": section,
                                "metadata": {
                                    "section": section,
                                    "cardType": card_name
                                }
                            })
        except Exception as e:
            st.error(f"Error loading {json_file}: {str(e)}")
    return documents

def format_section_content(section: str, data: Any) -> str:
    """Format section content for better readability"""
    section_title = section.replace('_', ' ').title()
    content = f"{section_title}:\n"
    
    if isinstance(data, dict):
        for key, value in data.items():
            key_formatted = key.replace('_', ' ').title()
            if isinstance(value, dict):
                content += f"  {key_formatted}:\n"
                for sub_key, sub_value in value.items():
                    sub_key_formatted = sub_key.replace('_', ' ').title()
                    if isinstance(sub_value, (list, dict)):
                        content += f"    {sub_key_formatted}: {json.dumps(sub_value, indent=2)}\n"
                    else:
                        content += f"    {sub_key_formatted}: {sub_value}\n"
            elif isinstance(value, list):
                content += f"  {key_formatted}: {', '.join(map(str, value))}\n"
            else:
                content += f"  {key_formatted}: {value}\n"
    elif isinstance(data, list):
        content += f"  {', '.join(map(str, data))}\n"
    else:
        content += f"  {data}\n"
    
    return content

@st.cache_data
def generate_embeddings(documents: List[Dict], _client):
    """Generate embeddings for all documents"""
    embeddings = []
    for doc in documents:
        try:
            response = _client.embeddings.create(
                model="text-embedding-3-small",
                input=doc["content"]
            )
            embeddings.append(response.data[0].embedding)
        except Exception as e:
            st.error(f"Error generating embedding for {doc['id']}: {str(e)}")
            embeddings.append(None)
    return embeddings

def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Calculate cosine similarity between two vectors"""
    a_np = np.array(a)
    b_np = np.array(b)
    return np.dot(a_np, b_np) / (np.linalg.norm(a_np) * np.linalg.norm(b_np))

def search_documents(query: str, documents: List[Dict], embeddings: List[List[float]], client, top_k: int = 5) -> tuple[List[Dict], Dict]:
    """Search documents using vector similarity"""
    try:
        # Generate query embedding
        query_response = client.embeddings.create(
            model="text-embedding-3-small",
            input=query
        )
        query_embedding = query_response.data[0].embedding
        
        # Track embedding usage
        embedding_usage = {
            "tokens": query_response.usage.total_tokens,
            "cost": query_response.usage.total_tokens * 0.00002 / 1000  # $0.00002 per 1K tokens
        }
        
        # Calculate similarities
        similarities = []
        for i, doc_embedding in enumerate(embeddings):
            if doc_embedding is not None:
                similarity = cosine_similarity(query_embedding, doc_embedding)
                
                # Boost for spend-related queries that might need both rewards and milestones
                doc = documents[i]
                if any(keyword in query.lower() for keyword in ['spend', 'earn', 'miles', 'points', 'yearly', 'annual']):
                    if any(section in doc['section'].lower() for section in ['reward', 'milestone']):
                        similarity += 0.1  # Small boost to ensure we get both types of documents
                
                similarities.append((similarity, i))
        
        # Sort by similarity and return top results
        similarities.sort(reverse=True)
        results = []
        
        for similarity, idx in similarities[:top_k]:
            doc = documents[idx].copy()
            doc["similarity"] = similarity
            results.append(doc)
        
        return results, embedding_usage
    except Exception as e:
        st.error(f"Error in search: {str(e)}")
        return [], {"tokens": 0, "cost": 0}

def generate_answer(question: str, relevant_docs: List[Dict], client, card_name: str = None, use_gpt4: bool = True) -> tuple[str, Dict]:
    """Generate answer using OpenAI GPT"""
    if not relevant_docs:
        return "I couldn't find relevant information to answer your question. Please try rephrasing your query.", {"tokens": 0, "cost": 0}
    
    context = "\n\n---\n\n".join([
        f"Card: {doc['cardName']}\nSection: {doc['section']}\nContent: {doc['content']}"
        for doc in relevant_docs
    ])
    
    system_prompt = """You are an expert assistant helping users understand Indian credit card terms and conditions.
    
    IMPORTANT: When calculating total rewards/miles for a spend amount, you MUST consider BOTH:
    1. Base earning rate (points/miles per ₹100 spent)
    2. Milestone bonuses (additional points/miles at specific spending thresholds)
    
    Always show your calculations step by step when dealing with spend-based questions.
    
    Please provide accurate, helpful answers based on the provided context. If the context doesn't contain enough information to answer the question, say so clearly.
    
    Format your response in a clear, easy-to-understand way. Use bullet points or numbered lists when appropriate.
    Include specific details like fees, interest rates, and conditions when relevant.
    """
    
    if card_name:
        system_prompt += f"\nFocus on information about the {card_name} card."
    
    user_prompt = f"""Based on the following credit card information, please answer this question: "{question}"

    Context:
    {context}

    IMPORTANT: If the question involves calculating total rewards/miles for a spending amount:
    1. First calculate base rewards: (spend amount ÷ 100) × earning rate
    2. Then identify applicable milestone bonuses from the spending amount
    3. Add base rewards + milestone bonuses for the total
    4. Show each step clearly in your answer

    Please provide a comprehensive answer based on the information provided."""
    
    # Model and pricing selection
    model = "gpt-4" if use_gpt4 else "gpt-3.5-turbo"
    input_cost_per_k = 0.03 if use_gpt4 else 0.0015  # GPT-4: $0.03, GPT-3.5: $0.0015
    output_cost_per_k = 0.06 if use_gpt4 else 0.002  # GPT-4: $0.06, GPT-3.5: $0.002
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=1000,
            temperature=0.1
        )
        
        # Calculate costs
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        total_cost = (input_tokens * input_cost_per_k / 1000) + (output_tokens * output_cost_per_k / 1000)
        
        usage = {
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": response.usage.total_tokens,
            "cost": total_cost
        }
        
        return response.choices[0].message.content, usage
    except Exception as e:
        return f"Error generating answer: {str(e)}", {"tokens": 0, "cost": 0}

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "documents" not in st.session_state:
    st.session_state.documents = None
if "embeddings" not in st.session_state:
    st.session_state.embeddings = None

# Initialize OpenAI client
client = init_openai_client()

# Load data
with st.spinner("Loading credit card data..."):
    if st.session_state.documents is None:
        st.session_state.documents = load_credit_card_data()
    
    if st.session_state.embeddings is None:
        st.session_state.embeddings = generate_embeddings(st.session_state.documents, client)

# Get available cards
available_cards = list(set([doc["cardName"] for doc in st.session_state.documents]))

# Main UI
st.title("💳 Credit Card RAG Assistant")
st.markdown("Ask questions about Indian credit card terms and conditions")

# Sidebar
with st.sidebar:
    st.header("🔧 Configuration")
    st.success("✅ Standalone Mode Active")
    st.info(f"Loaded {len(st.session_state.documents)} documents from {len(available_cards)} cards")
    
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
    top_k = st.slider("Number of results (top_k)", 1, 10, 7, help="More results = higher cost but better accuracy for calculations")
    
    # Model selection for cost optimization
    st.subheader("💰 Cost Optimization")
    use_cheaper_model = st.checkbox("Use GPT-3.5-turbo (10x cheaper)", help="GPT-3.5-turbo costs ~$0.01-0.03 per query vs GPT-4's $0.10-0.30")
    
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
                st.write(f"🤖 GPT-4: {usage['gpt'].get('total_tokens', 0)} tokens (${usage['gpt'].get('cost', 0):.4f})")
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
                # Filter documents based on query mode
                filtered_docs = st.session_state.documents
                filtered_embeddings = st.session_state.embeddings
                
                if query_mode == "Specific Card" and selected_cards:
                    card_name = selected_cards[0]
                    indices = [i for i, doc in enumerate(st.session_state.documents) if doc["cardName"] == card_name]
                    filtered_docs = [st.session_state.documents[i] for i in indices]
                    filtered_embeddings = [st.session_state.embeddings[i] for i in indices]
                elif query_mode == "Compare Cards" and len(selected_cards) >= 2:
                    indices = [i for i, doc in enumerate(st.session_state.documents) if doc["cardName"] in selected_cards]
                    filtered_docs = [st.session_state.documents[i] for i in indices]
                    filtered_embeddings = [st.session_state.embeddings[i] for i in indices]
                
                # Search relevant documents
                relevant_docs, embedding_usage = search_documents(prompt, filtered_docs, filtered_embeddings, client, top_k)
                
                # Generate answer
                card_context = selected_cards[0] if query_mode == "Specific Card" and selected_cards else None
                answer, gpt_usage = generate_answer(prompt, relevant_docs, client, card_context, use_gpt4=not use_cheaper_model)
                
                # Calculate total cost
                total_cost = embedding_usage["cost"] + gpt_usage["cost"]
                
                # Display answer
                st.markdown(answer)
                
                # Display usage metrics
                with st.expander("💰 Token Usage & Cost"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("🔍 Query Embedding", f"{embedding_usage['tokens']} tokens", f"${embedding_usage['cost']:.6f}")
                    with col2:
                        model_name = gpt_usage.get('model', 'gpt-4')
                        st.metric(f"🤖 {model_name}", f"{gpt_usage.get('total_tokens', 0)} tokens", f"${gpt_usage.get('cost', 0):.4f}")
                    
                    st.metric("💸 **Total Cost**", f"${total_cost:.4f}", help="This is the cost for this single query")
                    
                    if gpt_usage.get('total_tokens', 0) > 0:
                        st.write(f"📊 {gpt_usage.get('model', 'gpt-4')} Details: {gpt_usage['input_tokens']} input + {gpt_usage['output_tokens']} output tokens")
                
                # Display sources
                if relevant_docs:
                    with st.expander("📚 Sources"):
                        for i, doc in enumerate(relevant_docs):
                            st.write(f"**{i+1}. {doc['cardName']} - {doc['section']}** (Similarity: {doc.get('similarity', 0):.3f})")
                            st.write(doc['content'])
                            st.divider()
                
                # Add assistant response to chat
                assistant_message = {
                    "role": "assistant",
                    "content": answer,
                    "sources": relevant_docs,
                    "usage": {"embedding": embedding_usage, "gpt": gpt_usage, "total_cost": total_cost}
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
st.markdown("🚀 **Supavec Clone** - Standalone RAG-powered Credit Card Assistant | Built with Streamlit")