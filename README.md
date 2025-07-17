# Credit Card Assistant

A modern full-stack AI assistant for querying Indian credit card terms and conditions. Get instant answers about rewards, fees, eligibility, and more using natural language queries with a professional React interface.

## Features

- **Modern Full-Stack**: React + TypeScript frontend with FastAPI backend
- **Responsive Design**: Mobile-first with collapsible sidebar and bottom navigation
- **Multiple UI Options**: React (current), Streamlit (legacy), Gradio (legacy)
- **Enterprise Search**: Google Vertex AI Search for fast, accurate document retrieval
- **Multi-Model AI**: Choose from GPT-4, GPT-3.5, or Gemini 1.5 (Flash/Pro) 
- **Ultra-Low Cost**: Gemini Flash costs 20x less than GPT-3.5 (~$0.0003/query)
- **Smart Calculations**: Automatically handles complex reward calculations with milestones
- **Multi-Card Support**: Query individual cards or compare multiple cards
- **Category-Aware**: Correctly handles hotel/flight vs general spending rates
- **Real-Time Costs**: Live token usage and cost tracking
- **Professional UI**: Modern React interface with complete UI control

## Supported Cards

- **Axis Atlas**: Premium miles card with accelerated earning rates
- **ICICI EPM**: Reward points card with category-based earning
- **HSBC Premier**: Miles card with comprehensive travel benefits

## Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key (required)
- Gemini API key (optional, for ultra-low cost queries)
- Google Cloud credentials (required for Vertex AI Search)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/credit-card-assistant.git
   cd credit-card-assistant
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   export GEMINI_API_KEY="your-gemini-key-here"  # Optional but recommended
   export GOOGLE_CLOUD_PROJECT="your-project-id"
   export VERTEX_AI_LOCATION="global"
   export VERTEX_AI_DATA_STORE_ID="your-data-store-id"
   ```

4. **Authenticate with Google Cloud**
   ```bash
   gcloud auth application-default login
   ```

5. **Run the application**
   
   **Option A: React + FastAPI (Recommended)**
   ```bash
   # Terminal 1: Start backend
   cd backend
   ./start_backend.sh
   
   # Terminal 2: Start frontend
   cd cardgpt-ui
   ./start_frontend.sh
   ```
   Available at `http://localhost:3000` (React frontend)
   API docs at `http://localhost:8000/docs` (FastAPI backend)
   
   **Option B: Streamlit (Legacy)**
   ```bash
   streamlit run app.py
   ```
   Available at `http://localhost:8501`
   
   **Option C: Gradio (Legacy)**
   ```bash
   python app_gradio.py
   # Or use the start script
   ./start_gradio.sh
   ```
   Available at `http://localhost:7860`

## Usage

### Query Examples

**General Questions:**
- "What are the annual fees for credit cards?"
- "Compare reward rates between cards"
- "What are the airport lounge access benefits?"

**Calculations:**
- "How many miles do I earn on ₹2 lakh flight spend with Axis Atlas?"
- "What rewards for ₹50K utility spend on ICICI EPM?"
- "Compare cash withdrawal fees between cards"

**Specific Features:**
- "What are the welcome benefits for Axis Atlas?"
- "Are utilities capped for HSBC Premier card?"
- "What are the joining benefits of HSBC Premier?"

### Query Modes

1. **General Query**: Ask questions about any credit card
2. **Specific Card**: Focus on a particular card
3. **Compare Cards**: Compare multiple cards side-by-side

## Architecture

The application uses a modular architecture with the following components:

```
├── backend/                    # FastAPI Backend
│   ├── main.py                # FastAPI app entry point
│   ├── models.py              # Pydantic schemas
│   ├── api/                   # API endpoints
│   │   ├── chat.py           # Chat endpoints
│   │   ├── config.py         # Configuration
│   │   └── health.py         # Health check
│   ├── services/             # Business logic
│   │   ├── llm.py           # Multi-model LLM service (GPT-4/3.5, Gemini)
│   │   ├── vertex_retriever.py # Google Vertex AI Search integration
│   │   ├── query_enhancer.py   # Smart query preprocessing
│   │   └── calculator.py       # Precise reward calculations
│   ├── requirements.txt      # Python dependencies
│   └── start_backend.sh      # Backend startup script
├── cardgpt-ui/               # React Frontend
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── services/        # API client
│   │   ├── hooks/          # React hooks & state
│   │   └── styles/         # Tailwind CSS
│   ├── package.json        # Node.js dependencies
│   └── start_frontend.sh   # Frontend startup script
├── app.py                   # Streamlit application (legacy)
├── app_gradio.py           # Gradio UI (legacy)
├── data/                   # Credit card JSON files
└── README_REACT_FASTAPI.md # Full documentation
```

### Key Components

- **React Frontend**: Modern TypeScript React app with Tailwind CSS
- **FastAPI Backend**: RESTful API with automatic documentation
- **Vertex AI Search**: Enterprise-grade search with Google's managed infrastructure
- **Multi-Model LLM**: Choose optimal model based on query complexity and cost
- **Query Enhancement**: Automatic category detection and preprocessing
- **Smart Calculator**: Precise calculations for rewards, milestones, and fees
- **Responsive Design**: Mobile-first with collapsible sidebar and bottom navigation

## Model Costs

| Model | Cost per Query | Best For | Speed |
|-------|---------------|----------|-------|
| **Gemini 1.5 Flash** | **$0.0003** | Simple queries | ⚡ Fast |
| **GPT-3.5-turbo** | $0.002 | General queries | 🚀 Fast |
| **Gemini 1.5 Pro** | $0.005 | Complex calculations | ⚡ Fast |
| **GPT-4** | $0.06 | Premium accuracy | 🐌 Slow |

**💡 Recommendation**: Use Gemini Flash as default (20x cheaper than GPT-3.5!)

## Google Cloud Setup

### 1. Create Vertex AI Search Data Store

1. Go to [Vertex AI Search Console](https://console.cloud.google.com/ai/search)
2. Create new data store
3. Choose **Structured data (JSONL)** as data type
4. Upload your credit card data in JSONL format

### 2. Configure Schema

Mark the following fields in your data store:
- `cardName`: **Filterable** (for card-specific queries)
- `jsonData`: **Retrievable** (main content)
- `section`: **Retrievable** (metadata)

### 3. Environment Configuration

Add to your `.streamlit/secrets.toml`:
```toml
GOOGLE_CLOUD_PROJECT = "your-project-id"
VERTEX_AI_LOCATION = "global"
VERTEX_AI_DATA_STORE_ID = "your-data-store-id"
OPENAI_API_KEY = "your-openai-key"
GEMINI_API_KEY = "your-gemini-key"
```

## Deployment

### Streamlit Cloud

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Add API keys to Streamlit secrets
5. Deploy!

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run Streamlit version
streamlit run app.py

# Run Gradio version (recommended)
python app_gradio.py

# Test different models
# Both apps auto-detect available models and show cost comparisons
```

## Adding New Credit Cards

1. Create a JSON file in the `/data` directory following the existing structure
2. Include sections for:
   - `common_terms`: Interest rates, fees, policies
   - `card`: Specific rewards, milestones, benefits
3. Upload the data to your Vertex AI Search data store
4. Restart the application

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
streamlit run app.py

# Check code quality
python -m py_compile app.py
```

## Performance

- **Search Response**: 2-5 seconds (enterprise-optimized)
- **Model Response**: 1-10 seconds (depending on model choice)
- **Zero Maintenance**: Google's managed infrastructure handles scaling
- **High Availability**: Enterprise-grade reliability

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Credits

**Built by:** [@maharajamandy](https://x.com/maharajamandy) & [@jockaayush](https://x.com/jockaayush)  
**Powered by:** OpenAI + Google Gemini + Vertex AI Search  
**Framework:** Streamlit + Gradio + Python  

---

*Get instant answers about Indian credit card terms and conditions with the power of AI!*