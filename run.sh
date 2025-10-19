#!/bin/bash

# Travelopedia Quick Launch Script
# Makes it easy for others to run the application

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║         🌍 TRAVELOPEDIA - AI TRAVEL PLANNER 🌍              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python $(python3 --version) detected"
echo ""

# Check if running in virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    # Check if venv exists
    if [ -d "venv" ]; then
        echo "🔧 Activating virtual environment..."
        source venv/bin/activate
    else
        echo "� Creating virtual environment..."
        python3 -m venv venv
        source venv/bin/activate
        echo "✅ Virtual environment created"
    fi
    echo ""
fi

# Check if dependencies are installed
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip3 install -r requirements.txt
    echo "✅ Dependencies installed"
    echo ""
else
    echo "✅ Dependencies already installed"
    echo ""
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating template..."
    cat > .env << 'EOF'
# Weather API (FREE - Recommended)
OPENWEATHER_API_KEY=your_openweather_key_here

# Activities APIs (Optional)
YELP_API_KEY=your_yelp_key_here

# Flight & Hotel APIs (Optional - will use mock data if not provided)
AVIATIONSTACK_API_KEY=your_aviationstack_key_here
RAPIDAPI_KEY=your_rapidapi_key_here
EOF
    echo "✅ .env template created"
    echo "📝 Edit .env file and add your API keys"
    echo "   Get free keys from:"
    echo "   - OpenWeatherMap: https://openweathermap.org/api"
    echo "   - Yelp: https://www.yelp.com/developers"
    echo ""
    echo "⚡ TIP: System works with mock data too - you can test without API keys!"
    echo ""
fi

# Create necessary directories
mkdir -p output/itineraries
mkdir -p output/feedback
mkdir -p logs

echo "═══════════════════════════════════════════════════════════════"
echo "Choose what to run:"
echo "═══════════════════════════════════════════════════════════════"
echo "1. 🌐 Web UI (Streamlit) - Recommended"
echo "2. 🖥️  Backend Test (CLI)"
echo "3. 🧪 API Tests"
echo "4. 🔍 Workflow Analysis"
echo "5. 🆕 Test New Features"
echo "6. 👋 Exit"
echo "═══════════════════════════════════════════════════════════════"
echo ""
read -p "Enter your choice (1-6): " choice

case $choice in
    1)
        echo ""
        echo "🌐 Starting Streamlit Web UI..."
        echo "═══════════════════════════════════════════════════════════════"
        echo "📍 Open your browser to: http://localhost:8501"
        echo "💡 Press Ctrl+C to stop the server"
        echo "═══════════════════════════════════════════════════════════════"
        echo ""
        streamlit run frontend/app.py --server.port 8501 --server.address localhost
        ;;
    2)
        echo ""
        echo "🖥️  Running backend test..."
        echo "═══════════════════════════════════════════════════════════════"
        echo ""
        python3 backend/main.py
        echo ""
        echo "✅ Backend test complete!"
        echo "📁 Check output/itineraries/ for generated files"
        ;;
    3)
        echo ""
        echo "🧪 Running API tests..."
        echo "═══════════════════════════════════════════════════════════════"
        echo ""
        python3 tests/test_apis.py
        echo ""
        echo "✅ API tests complete!"
        ;;
    4)
        echo ""
        echo "🔍 Running workflow analysis..."
        echo "═══════════════════════════════════════════════════════════════"
        echo ""
        python3 tests/test_workflow.py
        echo ""
        echo "✅ Workflow analysis complete!"
        ;;
    5)
        echo ""
        echo "🆕 Testing new features..."
        echo "═══════════════════════════════════════════════════════════════"
        echo ""
        python3 tests/test_new_features.py
        echo ""
        echo "✅ Feature tests complete!"
        ;;
    6)
        echo ""
        echo "👋 Goodbye! Happy travel planning!"
        echo ""
        exit 0
        ;;
    *)
        echo ""
        echo "❌ Invalid choice. Please run again and select 1-6."
        exit 1
        ;;
esac

# Deactivate venv on exit (if we activated it)
if [ -n "$VIRTUAL_ENV" ]; then
    deactivate
fi
