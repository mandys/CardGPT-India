#!/bin/bash

# Start script for FastAPI Backend
echo "🚀 Starting Credit Card Assistant FastAPI Backend..."
echo ""

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
else
    echo "⚠️  No virtual environment found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Check environment variables
echo "🔍 Checking environment variables..."
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OPENAI_API_KEY not set. Please set it in your .env file."
fi

if [ -z "$GOOGLE_CLOUD_PROJECT" ]; then
    echo "⚠️  GOOGLE_CLOUD_PROJECT not set. Please set it in your .env file."
fi

if [ -z "$VERTEX_AI_DATA_STORE_ID" ]; then
    echo "⚠️  VERTEX_AI_DATA_STORE_ID not set. Please set it in your .env file."
fi

echo ""
echo "✅ Backend Configuration:"
echo "   🌐 API URL: http://localhost:8000"
echo "   📖 API Docs: http://localhost:8000/docs"
echo "   🏥 Health Check: http://localhost:8000/api/health"
echo ""

# Start the FastAPI server
echo "🔥 Starting FastAPI server..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload