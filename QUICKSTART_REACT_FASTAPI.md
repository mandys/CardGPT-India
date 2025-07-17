# Quick Start Guide - React + FastAPI Architecture

## 🚀 Get Started in 3 Minutes

### Step 1: Set up Backend

```bash
# 1. Navigate to backend directory
cd backend

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env file with your API keys (see below)

# 5. Start backend
./start_backend.sh
```

### Step 2: Set up Frontend

```bash
# 1. Open new terminal and navigate to frontend
cd cardgpt-ui

# 2. Install dependencies
npm install

# 3. Start frontend
./start_frontend.sh
```

### Step 3: Open Application

- **Frontend**: http://localhost:3000 (main application)
- **Backend API**: http://localhost:8000 (API server)
- **API Docs**: http://localhost:8000/docs (interactive documentation)

## 🔑 Required Environment Variables

Edit `backend/.env` file:

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_CLOUD_PROJECT=your_gcp_project_id
VERTEX_AI_DATA_STORE_ID=your_vertex_ai_data_store_id

# Optional (for ultra-low cost)
GEMINI_API_KEY=your_gemini_api_key_here
VERTEX_AI_LOCATION=global
```

## 🧪 Test Your Setup

```bash
# Test backend
cd backend
python test_api.py

# Test frontend
cd cardgpt-ui
npm start  # Should open browser automatically
```

## 🎯 Key Features

### ✅ What Works Now
- **Modern React UI** with Tailwind CSS
- **FastAPI backend** with auto-documentation
- **Multi-model support** (GPT-4, GPT-3.5, Gemini Flash, Gemini Pro)
- **Real-time chat** with typing indicators
- **Cost tracking** with live updates
- **Smart query enhancement** with category detection
- **Error handling** with graceful fallbacks
- **Mobile responsive** design

### 🔄 Architecture Benefits
- **Complete UI control** - no Streamlit/Gradio quirks
- **Professional design** - modern, clean interface
- **Scalable** - easy to add new features
- **Maintainable** - clear separation of concerns
- **Deployable** - can deploy frontend/backend separately

## 📱 Usage

1. **Select Model**: Choose from available AI models in settings
2. **Set Query Mode**: General, Specific Card, or Compare Cards
3. **Ask Questions**: Type naturally or use example questions
4. **View Results**: Get answers with cost breakdown and sources

## 🛠️ Troubleshooting

### Backend Issues
```bash
# Check if backend is running
curl http://localhost:8000/api/health

# Check logs
tail -f backend.log

# Restart backend
./start_backend.sh
```

### Frontend Issues
```bash
# Check if frontend is running
curl http://localhost:3000

# Clear cache and restart
rm -rf node_modules package-lock.json
npm install
npm start
```

### Common Problems
- **CORS errors**: Make sure backend is running first
- **API connection**: Verify backend URL in frontend
- **Missing dependencies**: Run install commands again
- **Environment variables**: Check .env file exists and is correct

## 📈 Performance Tips

- **Use Gemini Flash** for fastest, cheapest queries ($0.0003 per query)
- **Adjust search results** (top_k) based on accuracy needs
- **Enable caching** for repeated queries
- **Monitor costs** with the built-in cost tracker

## 🎨 Customization

### Frontend Styling
- Edit `cardgpt-ui/src/styles/globals.css` for global styles
- Modify `cardgpt-ui/tailwind.config.js` for theme customization
- Update components in `cardgpt-ui/src/components/` for UI changes

### Backend Configuration
- Add new endpoints in `backend/api/`
- Modify business logic in `backend/services/`
- Update API models in `backend/models.py`

## 📚 Next Steps

1. **Deploy to production** (see README_REACT_FASTAPI.md)
2. **Add authentication** (user accounts)
3. **Implement caching** (Redis/Memcached)
4. **Add monitoring** (metrics, logging)
5. **Extend features** (file uploads, export, etc.)

## 🆘 Need Help?

- Check the full documentation: `README_REACT_FASTAPI.md`
- Test API endpoints: `backend/test_api.py`
- View API documentation: http://localhost:8000/docs
- Check console logs for errors

---

**🎉 You now have a modern, professional credit card assistant with full UI control!**