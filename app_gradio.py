"""
Credit Card Assistant - Gradio Implementation
Clean, reliable UI with full control and no quirks
"""
import gradio as gr
import os
import logging
from typing import List, Dict, Any, Tuple
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our existing services
from src.llm import LLMService
from src.vertex_retriever import VertexRetriever
from src.query_enhancer import QueryEnhancer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global services
llm_service = None
retriever_service = None
query_enhancer_service = None

def initialize_services():
    """Initialize all backend services"""
    global llm_service, retriever_service, query_enhancer_service
    
    # Get API keys
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    gemini_key = os.getenv("GEMINI_API_KEY")
    
    # Get Google Cloud config
    gcp_project_id = os.getenv("GCP_PROJECT_ID")
    gcp_location = os.getenv("GCP_LOCATION", "global")
    gcp_data_store_id = os.getenv("GCP_DATA_STORE_ID")
    
    if not gcp_project_id or not gcp_data_store_id:
        raise ValueError("GCP_PROJECT_ID and GCP_DATA_STORE_ID required")
    
    # Initialize services
    retriever_service = VertexRetriever(gcp_project_id, gcp_location, gcp_data_store_id)
    llm_service = LLMService(api_key, gemini_key)
    query_enhancer_service = QueryEnhancer()
    
    logger.info("✅ All services initialized successfully")

def process_query(
    question: str,
    query_mode: str,
    card_filter: str,
    top_k: int,
    selected_model: str
) -> Dict[str, Any]:
    """Process user query - same logic as before"""
    
    # Enhance query
    enhanced_question, metadata = query_enhancer_service.enhance_query(question)
    
    # No separate embedding costs for Vertex AI
    embedding_usage = {"tokens": 0, "cost": 0, "model": "vertex-ai-search"}
    
    # Determine search filters
    search_card_filter = None
    if query_mode == "Specific Card" and card_filter and card_filter != "None":
        search_card_filter = card_filter
    elif metadata.get('card_detected'):
        search_card_filter = metadata['card_detected']
    
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

def chat_response(message: str, history: List[Dict], model: str, query_mode: str, card_filter: str, top_k: int):
    """Handle chat response with proper error handling"""
    try:
        # Process the query
        result = process_query(message, query_mode, card_filter, top_k, model)
        
        # Format response
        response = result["answer"]
        
        # Add to history
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": response})
        
        # Format cost breakdown
        cost_md = f"""**💰 Cost Breakdown:**
- 🔍 Search: {result['embedding_usage']['tokens']} tokens (${result['embedding_usage']['cost']:.6f})
- 🤖 {result['llm_usage'].get('model', 'unknown')}: {result['llm_usage'].get('total_tokens', 0)} tokens (${result['llm_usage'].get('cost', 0):.4f})
- 💸 **Total Cost**: ${result['total_cost']:.4f}

**Model Performance:**
- Input tokens: {result['llm_usage'].get('input_tokens', 0)}
- Output tokens: {result['llm_usage'].get('output_tokens', 0)}
- Total tokens: {result['llm_usage'].get('total_tokens', 0)}"""
        
        # Format sources
        sources_md = "**📚 Document Sources:**\n\n"
        if result["documents"]:
            for i, doc in enumerate(result["documents"], 1):
                sources_md += f"{i}. **{doc['cardName']}** – {doc['section']}\n"
                sources_md += f"   Similarity: {doc.get('similarity', 0):.3f}\n"
                preview = doc['content'][:300] + "…" if len(doc['content']) > 300 else doc['content']
                sources_md += f"   Preview: {preview}\n\n"
        else:
            sources_md += "No sources found."
        
        return history, "", cost_md, sources_md
        
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        logger.error(f"Chat error: {str(e)}", exc_info=True)
        
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": error_msg})
        
        return history, "", "No cost data due to error", "No sources due to error"

def create_interface():
    """Create the main Gradio interface"""
    
    with gr.Blocks(title="💳 Credit Card Assistant", theme=gr.themes.Soft()) as demo:
        gr.Markdown("# 💳 Credit Card Assistant")
        gr.Markdown("Ask questions about Indian credit card terms and conditions using AI")
        
        with gr.Row():
            # Left sidebar - Settings
            with gr.Column(scale=1):
                gr.Markdown("## ⚙️ Settings")
                
                model_dropdown = gr.Dropdown(
                    choices=["gemini-1.5-pro", "gemini-1.5-flash", "gpt-3.5-turbo", "gpt-4"],
                    value="gemini-1.5-pro",
                    label="🤖 AI Model",
                    info="Gemini Pro recommended for best balance"
                )
                
                query_mode = gr.Radio(
                    choices=["General Query", "Specific Card", "Compare Cards"],
                    value="General Query",
                    label="🎯 Query Mode"
                )
                
                card_filter = gr.Dropdown(
                    choices=["None", "Axis Atlas", "ICICI EPM", "HSBC Premier"],
                    value="None",
                    label="💳 Card Filter",
                    info="Only for Specific Card mode"
                )
                
                top_k_slider = gr.Slider(
                    minimum=1,
                    maximum=15,
                    value=7,
                    step=1,
                    label="🔍 Search Results",
                    info="More results = better accuracy, higher cost"
                )
                
                gr.Markdown("## 💡 Example Questions")
                example_btn1 = gr.Button("What are the annual fees for credit cards?", size="sm")
                example_btn2 = gr.Button("Compare reward rates between cards", size="sm")
                example_btn3 = gr.Button("What are the welcome benefits for Axis Atlas?", size="sm")
                example_btn4 = gr.Button("How many miles do I earn on ₹2 lakh flight spend?", size="sm")
                
            # Right side - Chat
            with gr.Column(scale=3):
                chatbot = gr.Chatbot(
                    label="Chat",
                    height=500,
                    type="messages",
                    placeholder="Ask me anything about credit cards..."
                )
                
                msg = gr.Textbox(
                    label="Your Message",
                    placeholder="Type your question here...",
                    lines=2
                )
                
                with gr.Row():
                    submit_btn = gr.Button("Send", variant="primary")
                    clear_btn = gr.Button("Clear Chat")
                
                # Collapsible sections for cost and sources
                with gr.Accordion("💰 Cost Breakdown", open=False):
                    cost_display = gr.Markdown("No query yet")
                
                with gr.Accordion("📚 Document Sources", open=False):
                    sources_display = gr.Markdown("No sources yet")
        
        # Event handlers
        def clear_chat():
            return [], "", "No query yet", "No sources yet"
        
        def set_example(example_text):
            return example_text
        
        # Connect events
        submit_btn.click(
            chat_response,
            [msg, chatbot, model_dropdown, query_mode, card_filter, top_k_slider],
            [chatbot, msg, cost_display, sources_display]
        )
        
        msg.submit(
            chat_response,
            [msg, chatbot, model_dropdown, query_mode, card_filter, top_k_slider],
            [chatbot, msg, cost_display, sources_display]
        )
        
        clear_btn.click(clear_chat, outputs=[chatbot, msg, cost_display, sources_display])
        
        # Example button events
        example_btn1.click(lambda: "What are the annual fees for credit cards?", outputs=msg)
        example_btn2.click(lambda: "Compare reward rates between cards", outputs=msg)
        example_btn3.click(lambda: "What are the welcome benefits for Axis Atlas?", outputs=msg)
        example_btn4.click(lambda: "How many miles do I earn on ₹2 lakh flight spend?", outputs=msg)
    
    return demo

def main():
    """Main application entry point"""
    try:
        # Initialize services
        print("🚀 Initializing Credit Card Assistant...")
        initialize_services()
        
        # Create and launch interface
        demo = create_interface()
        
        print("✅ Starting Gradio interface...")
        print("📋 Available at: http://localhost:7860")
        print("🎯 Features:")
        print("   - Settings panel with model selection")
        print("   - Clickable example questions")
        print("   - Collapsible cost and sources")
        print("   - Clean chat interface")
        print("   - No quirks or API issues!")
        
        demo.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False,
            debug=True,
            show_error=True
        )
        
    except Exception as e:
        print(f"❌ Failed to start application: {str(e)}")
        print("Check your environment variables and try again.")

if __name__ == "__main__":
    main()