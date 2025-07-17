# Credit Card Assistant - React + FastAPI Architecture

## Overview
Modern full-stack implementation with React frontend and FastAPI backend, providing complete UI control and professional design with Tailwind CSS.

## Architecture

```
├── backend/                    # FastAPI Backend
│   ├── api/                   # API endpoints
│   │   ├── chat.py           # Chat endpoints
│   │   ├── config.py         # Configuration endpoints
│   │   └── health.py         # Health check
│   ├── services/             # Business logic
│   │   ├── llm.py           # Multi-model LLM service
│   │   ├── vertex_retriever.py # Vertex AI Search
│   │   ├── query_enhancer.py   # Query preprocessing
│   │   └── calculator.py       # Reward calculations
│   ├── main.py              # FastAPI app entry point
│   ├── models.py            # Pydantic schemas
│   ├── requirements.txt     # Python dependencies
│   └── start_backend.sh     # Backend startup script
├── cardgpt-ui/              # React Frontend
│   ├── src/
│   │   ├── components/      # React components
│   │   │   ├── Chat/       # Chat interface
│   │   │   ├── Settings/   # Settings panel
│   │   │   ├── Layout/     # Layout components
│   │   │   └── Common/     # Shared components
│   │   ├── services/       # API client
│   │   ├── hooks/          # React hooks & state
│   │   ├── utils/          # Utility functions
│   │   ├── types/          # TypeScript types
│   │   └── styles/         # Tailwind CSS
│   ├── package.json        # Node.js dependencies
│   └── start_frontend.sh   # Frontend startup script
└── README_REACT_FASTAPI.md # This file
```

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 18+
- OpenAI API key
- Google Cloud credentials (for Vertex AI)
- Gemini API key (optional, for ultra-low cost)

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys and Google Cloud config

# Start backend server
./start_backend.sh
# Or manually: uvicorn main:app --reload
```

Backend will be available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/api/health

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd cardgpt-ui

# Install dependencies
npm install

# Start development server
./start_frontend.sh
# Or manually: npm start
```

Frontend will be available at:
- App: http://localhost:3000

## Features

### Backend (FastAPI)
- **Multi-Model Support**: GPT-4, GPT-3.5, Gemini Flash, Gemini Pro
- **Vertex AI Search**: Enterprise-grade document retrieval
- **Smart Query Enhancement**: Automatic category detection
- **Cost Tracking**: Real-time token usage and cost monitoring
- **Health Monitoring**: Connection and service status checks
- **Auto-Documentation**: OpenAPI/Swagger docs at `/docs`

### Frontend (React + TypeScript)
- **Modern UI**: Clean, responsive design with Tailwind CSS
- **Real-time Chat**: Smooth chat interface with typing indicators
- **Settings Panel**: Model selection, query modes, filters
- **Cost Dashboard**: Live cost tracking and efficiency ratings
- **Error Handling**: Graceful error states and retry mechanisms
- **Mobile Responsive**: Works on all device sizes

## API Endpoints

### Chat Endpoints
- `POST /api/chat` - Send chat message
- `POST /api/query/enhance` - Enhance query (optional)

### Configuration
- `GET /api/config` - Get API configuration
- `GET /api/models` - Get available models
- `GET /api/cards` - Get supported cards

### Health
- `GET /api/health` - Health check
- `GET /` - API info

## Environment Variables

### Backend (.env)
```bash
# Required
OPENAI_API_KEY=your_openai_api_key
GOOGLE_CLOUD_PROJECT=your_gcp_project_id
VERTEX_AI_DATA_STORE_ID=your_data_store_id

# Optional
GEMINI_API_KEY=your_gemini_api_key
VERTEX_AI_LOCATION=global
```

### Frontend
Uses proxy configuration in package.json to connect to backend.

## Development

### Backend Development
```bash
cd backend
source venv/bin/activate

# Run with hot reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run tests (if available)
pytest

# Code formatting
black .
flake8 .
```

### Frontend Development
```bash
cd cardgpt-ui

# Start development server
npm start

# Build for production
npm run build

# Run tests
npm test

# Type checking
npm run type-check  # If available
```

## Deployment

### Backend Deployment
```bash
# Install production dependencies
pip install -r requirements.txt

# Start with production server
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Frontend Deployment
```bash
# Build for production
npm run build

# Deploy to static hosting (Vercel, Netlify, etc.)
# Update API base URL in production
```

## Model Costs

| Model | Cost per 1K Input | Cost per 1K Output | Best For |
|-------|-------------------|--------------------|---------| 
| **Gemini Flash** | $0.000075 | $0.0003 | Simple queries |
| **Gemini Pro** | $0.00125 | $0.005 | Complex calculations |
| **GPT-3.5** | $0.0015 | $0.002 | General queries |
| **GPT-4** | $0.03 | $0.06 | Premium accuracy |

## Performance Optimizations

### Backend
- **Connection pooling** for database/API connections
- **Caching** for repeated queries
- **Async processing** for concurrent requests
- **Error handling** with proper HTTP status codes

### Frontend
- **React Query** for API caching and state management
- **Zustand** for lightweight state management
- **Code splitting** for reduced bundle size
- **Optimistic updates** for better UX

## Troubleshooting

### Backend Issues
```bash
# Check logs
tail -f backend.log

# Test API directly
curl http://localhost:8000/api/health

# Check environment
python -c "import os; print(os.getenv('OPENAI_API_KEY')[:10] + '...')"
```

### Frontend Issues
```bash
# Check build
npm run build

# Test API connection
curl http://localhost:3000/api/health

# Clear cache
npm start -- --reset-cache
```

### Common Issues
1. **CORS errors**: Check CORS configuration in main.py
2. **API connection**: Verify backend is running on port 8000
3. **Missing dependencies**: Run `pip install -r requirements.txt` and `npm install`
4. **Environment variables**: Check .env file exists and is properly configured

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review API documentation at http://localhost:8000/docs
3. Check logs for error messages
4. Open an issue on GitHub

---

**🚀 Built with React + FastAPI for maximum performance and flexibility!**