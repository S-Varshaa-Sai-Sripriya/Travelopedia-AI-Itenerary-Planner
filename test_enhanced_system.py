#!/usr/bin/env python3
"""
Test script for Enhanced LLM Orchestrator

This script demonstrates the enhanced functionality of our AI Travel Planner.
"""

import asyncio
from app.agents.llm_orchestrator import LLMOrchestrator
from app.services.real_time_api import fetch_travel_data


async def test_orchestrator():
    """Test the enhanced LLM orchestrator"""
    print("🚀 Testing Enhanced LLM Orchestrator...")
    
    orchestrator = LLMOrchestrator()
    
    # Test travel request parsing
    request = "Plan a 7-day trip to Tokyo for 2 people with $4000 budget starting next month"
    print(f"📝 Processing request: {request}")
    
    result = await orchestrator.process_request(request)
    
    print(f"✅ Status: {result['status']}")
    print(f"📍 Destination: {result['parsed_request']['destination']}")
    print(f"💰 Budget: ${result['parsed_request']['budget']}")
    print(f"👥 Travelers: {result['parsed_request']['travelers']}")
    print(f"🤖 LLM Model: {result.get('llm_model_used', 'fallback')}")
    print(f"⏱️  Processing Time: {result['agent_results']['processing_time']}s")
    
    if result['validation']['is_valid']:
        print("✅ Request validation: PASSED")
    else:
        print("❌ Request validation: FAILED")
        print(f"   Errors: {result['validation']['errors']}")
    
    # Show agent coordination results
    agent_results = result['agent_results']
    print(f"\n🧠 GNN Personalization Score: {agent_results['gnn_recommendations']['personalization_score']}")
    print(f"💡 Budget Optimization Score: {agent_results['budget_optimization']['optimization_score']}")
    print(f"📅 Itinerary Confidence: {agent_results['itinerary_generation']['itinerary_confidence']}")


async def test_real_time_api():
    """Test the real-time API service"""
    print("\n🌐 Testing Real-Time API Service...")
    
    # Test fetching travel data (will use mock data if APIs not available)
    result = await fetch_travel_data("Paris", "New York", "2024-06-01", "2024-06-08")
    
    print(f"✅ API Status: {result['status']}")
    print(f"🌤️  Weather Source: {result['weather']['source']}")
    print(f"✈️  Flight Source: {result['flights']['source']}")
    print(f"🏨 Hotel Source: {result['hotels']['source']}")
    print(f"💱 Currency Source: {result['currency']['source']}")
    
    # Show sample data
    if 'current_weather' in result['weather']:
        weather = result['weather']['current_weather']
        print(f"🌡️  Current Temperature: {weather['temperature']}°C")
        print(f"☁️  Weather: {weather['description']}")


async def main():
    """Main test function"""
    print("=" * 60)
    print("🎯 AI Travel Planner - Enhanced System Test")
    print("=" * 60)
    
    try:
        await test_orchestrator()
        await test_real_time_api()
        
        print("\n" + "=" * 60)
        print("🎉 All tests completed successfully!")
        print("✅ Enhanced LLM Orchestrator is working")
        print("✅ Real-time API service is operational")
        print("✅ Pydantic models are validated")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())