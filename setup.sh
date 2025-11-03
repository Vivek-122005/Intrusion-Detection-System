#!/bin/bash

echo "🚀 Setting up IDS Project..."

# Backend setup
echo "📦 Setting up backend..."
cd backend
python3 -m venv venv 2>/dev/null || echo "Virtual environment already exists"
source venv/bin/activate || echo "Activate venv manually: source venv/bin/activate"
pip install -r requirements.txt
cd ..

# Frontend setup
echo "📦 Setting up frontend..."
cd frontend
npm install
cd ..

echo "✅ Setup complete!"
echo ""
echo "To start the application:"
echo "1. Backend: cd backend && source venv/bin/activate && python app.py"
echo "2. Frontend: cd frontend && npm start"
echo ""
echo "Make sure to train the model first using main.ipynb!"

