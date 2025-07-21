#!/bin/bash

# Start script for React Frontend
echo "🚀 Starting Credit Card Assistant React Frontend..."
echo ""

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
else
    echo "📦 Dependencies already installed"
fi

echo ""
echo "✅ Frontend Configuration:"
echo "   🌐 Frontend URL: http://localhost:3000"
echo "   🔗 Backend URL: http://localhost:8000"
echo "   📱 Mobile-friendly responsive design"
echo "   🎨 Tailwind CSS styling"
echo "   ⚡ TypeScript support"
echo ""

echo "🔥 Starting React development server..."
npm start