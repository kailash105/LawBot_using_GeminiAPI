#!/bin/bash

echo "🚀 Setting up IPC Crime Analyzer..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js v16 or higher."
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Node.js and Python are installed"

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
npm install

if [ $? -eq 0 ]; then
    echo "✅ Frontend dependencies installed successfully"
else
    echo "❌ Failed to install frontend dependencies"
    exit 1
fi

# Install backend dependencies
echo "🐍 Installing backend dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Backend dependencies installed successfully"
else
    echo "❌ Failed to install backend dependencies"
    exit 1
fi

# Create logs directory
mkdir -p logs

echo "🎉 Setup completed successfully!"
echo ""
echo "To start the application:"
echo "1. Start the backend: python3 app.py (runs on port 5001)"
echo "2. Start the frontend: npm run dev"
echo "3. Open http://localhost:3000 in your browser"
echo ""
echo "Happy coding! 🚀"
