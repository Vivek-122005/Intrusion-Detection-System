#!/bin/bash

# Script to restart Flask server with proper CORS configuration

echo "🛑 Stopping Flask server on port 5000..."

# Find and kill Flask processes
FLASK_PIDS=$(lsof -ti:5000 2>/dev/null)

if [ -z "$FLASK_PIDS" ]; then
    echo "   ℹ️  No Flask process found on port 5000"
else
    echo "   Found Flask processes: $FLASK_PIDS"
    for PID in $FLASK_PIDS; do
        echo "   Killing process $PID..."
        kill -9 $PID 2>/dev/null
    done
    sleep 1
    echo "   ✅ Flask processes stopped"
fi

echo ""
echo "🚀 Starting Flask server..."
cd "$(dirname "$0")/backend"

# Start Flask in background and capture output
python3 app.py > /tmp/flask_output.log 2>&1 &
FLASK_PID=$!

echo "   Flask started with PID: $FLASK_PID"
echo "   Waiting for Flask to initialize..."
sleep 3

# Check if Flask started successfully
if ps -p $FLASK_PID > /dev/null; then
    echo "   ✅ Flask is running"
    
    # Test CORS
    echo ""
    echo "🧪 Testing CORS configuration..."
    CORS_TEST=$(curl -s -H "Origin: http://localhost:3000" http://localhost:5000/api/health -w "\nHTTP_STATUS:%{http_code}" 2>&1 | tail -1)
    
    if echo "$CORS_TEST" | grep -q "HTTP_STATUS:200"; then
        echo "   ✅ CORS is working! Health endpoint returns 200"
    else
        echo "   ⚠️  CORS test failed. Check Flask output:"
        echo "   tail -f /tmp/flask_output.log"
    fi
else
    echo "   ❌ Flask failed to start. Check logs:"
    echo "   cat /tmp/flask_output.log"
fi

echo ""
echo "📋 Next steps:"
echo "   1. Check Flask output: tail -f /tmp/flask_output.log"
echo "   2. Test in browser: http://localhost:3000"
echo "   3. Check browser console for CORS errors"

