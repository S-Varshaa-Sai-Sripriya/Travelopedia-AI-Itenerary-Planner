#!/bin/bash

# Quick Test Script for Flight Display
# Uses virtual environment and tests the flight data structure

echo "🧪 Testing Flight Display with Virtual Environment"
echo "=================================================="
echo ""

# Activate virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

echo "🔧 Activating virtual environment..."
source venv/bin/activate

echo "✅ Virtual environment activated"
echo ""

# Run the test
echo "🚀 Running flight display test..."
echo ""
python3 test_flight_display.py

echo ""
echo "=================================================="
echo "✅ Test complete!"
echo ""
echo "To run the full application:"
echo "  ./run.sh"
echo ""
echo "To manually activate virtual environment:"
echo "  source venv/bin/activate"
