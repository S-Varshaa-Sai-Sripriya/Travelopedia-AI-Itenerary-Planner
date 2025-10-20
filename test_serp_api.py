#!/usr/bin/env python3
"""
SERP API Flight Test - Direct test of SERP API for JFK to DEL
"""

import os
import sys
import asyncio
import aiohttp
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_serp_api(origin="JFK", destination="DEL", start_date="2025-11-20", end_date="2025-11-24"):
    """Test SERP API directly for flight data."""
    
    serpapi_key = os.getenv('SERPAPI_API_KEY')
    
    if not serpapi_key:
        print("❌ ERROR: SERPAPI_API_KEY not found in .env file")
        return
    
    print("=" * 80)
    print(f"Testing SERP API Google Flights: {origin} → {destination}")
    print(f"Outbound: {start_date} | Return: {end_date}")
    print("=" * 80)
    print()
    
    url = "https://serpapi.com/search.json"
    
    params = {
        'engine': 'google_flights',
        'api_key': serpapi_key,
        'departure_id': origin,
        'arrival_id': destination,
        'outbound_date': start_date,
        'return_date': end_date,
        'currency': 'USD',
        'hl': 'en',
        'adults': 2,
        'travel_class': 2,  # Economy
        'type': 1  # Round trip
    }
    
    print("📤 Request Parameters:")
    for key, value in params.items():
        if key != 'api_key':
            print(f"  {key}: {value}")
    print()
    
    try:
        async with aiohttp.ClientSession() as session:
            print("⏳ Calling SERP API...")
            async with session.get(url, params=params, timeout=60) as response:
                print(f"📥 Response Status: {response.status}")
                print()
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Check response structure
                    print("📊 Response Structure:")
                    print(f"  Keys in response: {list(data.keys())}")
                    print()
                    
                    # Check for errors
                    if 'error' in data:
                        print(f"❌ API Error: {data['error']}")
                        return
                    
                    # Check for flights
                    best_flights = data.get('best_flights', [])
                    other_flights = data.get('other_flights', [])
                    
                    print(f"✈️  Best Flights: {len(best_flights)}")
                    print(f"✈️  Other Flights: {len(other_flights)}")
                    print(f"✈️  Total Flights: {len(best_flights) + len(other_flights)}")
                    print()
                    
                    if best_flights:
                        print("✅ Sample Flight Data:")
                        flight = best_flights[0]
                        print(f"  Price: ${flight.get('price', 'N/A')}")
                        print(f"  Airline: {flight.get('flights', [{}])[0].get('airline', 'N/A')}")
                        print(f"  Flight segments: {len(flight.get('flights', []))}")
                        print()
                    
                    if not best_flights and not other_flights:
                        print("⚠️  NO FLIGHTS FOUND")
                        print()
                        print("Possible reasons:")
                        print("  1. Route not available on selected dates")
                        print("  2. SERP API doesn't have data for this route")
                        print("  3. Try different dates or airports")
                        print("  4. Some international routes may not be available")
                        print()
                        
                        # Show search parameters
                        if 'search_parameters' in data:
                            print("🔍 Search Parameters Used by API:")
                            for key, value in data['search_parameters'].items():
                                print(f"  {key}: {value}")
                            print()
                        
                        # Show alternative suggestions if available
                        if 'search_metadata' in data:
                            print("📝 Search Metadata:")
                            print(f"  Status: {data['search_metadata'].get('status', 'N/A')}")
                            print(f"  Total time taken: {data['search_metadata'].get('total_time_taken', 'N/A')}s")
                            print()
                    
                else:
                    error_text = await response.text()
                    print(f"❌ HTTP Error {response.status}")
                    print(f"Response: {error_text[:500]}")
                    
    except asyncio.TimeoutError:
        print("❌ Request timed out after 60 seconds")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Parse command line arguments
    origin = sys.argv[1] if len(sys.argv) > 1 else "JFK"
    destination = sys.argv[2] if len(sys.argv) > 2 else "DEL"
    start_date = sys.argv[3] if len(sys.argv) > 3 else "2025-11-20"
    end_date = sys.argv[4] if len(sys.argv) > 4 else "2025-11-24"
    
    print()
    print("🧪 SERP API Flight Test Tool")
    print()
    print("Usage:")
    print(f"  {sys.argv[0]} [origin] [destination] [start_date] [end_date]")
    print()
    print("Example:")
    print(f"  {sys.argv[0]} JFK LAX 2025-11-20 2025-11-24")
    print()
    
    asyncio.run(test_serp_api(origin, destination, start_date, end_date))
