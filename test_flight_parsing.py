#!/usr/bin/env python3
"""
Test SERP API flight parsing - Shows how flights are split into outbound/return
"""

import os
import sys
import asyncio
import aiohttp
from dotenv import load_dotenv

load_dotenv()

async def test_flight_parsing():
    """Test how SERP API flights are parsed into outbound and return."""
    
    serpapi_key = os.getenv('SERPAPI_API_KEY')
    
    if not serpapi_key:
        print("❌ ERROR: SERPAPI_API_KEY not found in .env file")
        return
    
    origin = "JFK"
    destination = "DEL"  # or BOM
    start_date = "2025-11-20"
    end_date = "2025-11-24"
    
    print("=" * 80)
    print(f"Testing Flight Parsing: {origin} → {destination}")
    print(f"Dates: {start_date} (out) / {end_date} (return)")
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
        'adults': 2,
        'travel_class': 2,
        'type': 1
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            print("⏳ Fetching flights from SERP API...")
            async with session.get(url, params=params, timeout=60) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    best_flights = data.get('best_flights', [])
                    other_flights = data.get('other_flights', [])
                    all_flights = best_flights + other_flights
                    
                    print(f"✅ Found {len(all_flights)} flights")
                    print()
                    
                    if not all_flights:
                        print("❌ No flights returned")
                        return
                    
                    # Test parsing logic on first flight
                    flight = all_flights[0]
                    flights_list = flight.get('flights', [])
                    
                    print("=" * 80)
                    print(f"ANALYZING FIRST FLIGHT (Price: ${flight.get('price', 0)})")
                    print("=" * 80)
                    print()
                    
                    print(f"Total Flight Segments: {len(flights_list)}")
                    print()
                    
                    # Show all segments
                    for i, segment in enumerate(flights_list, 1):
                        dep_id = segment.get('departure_airport', {}).get('id', 'N/A')
                        dep_name = segment.get('departure_airport', {}).get('name', 'N/A')
                        arr_id = segment.get('arrival_airport', {}).get('id', 'N/A')
                        arr_name = segment.get('arrival_airport', {}).get('name', 'N/A')
                        airline = segment.get('airline', 'N/A')
                        flight_num = segment.get('flight_number', 'N/A')
                        
                        print(f"Segment {i}: {airline} {flight_num}")
                        print(f"  {dep_id} ({dep_name[:30]}...)")
                        print(f"  → {arr_id} ({arr_name[:30]}...)")
                        print()
                    
                    # Test splitting logic
                    print("=" * 80)
                    print("TESTING SPLIT LOGIC")
                    print("=" * 80)
                    print()
                    
                    outbound_flights = []
                    return_flights = []
                    
                    collecting_outbound = True
                    for i, segment in enumerate(flights_list):
                        arrival_id = segment.get('arrival_airport', {}).get('id', '')
                        
                        if collecting_outbound:
                            outbound_flights.append(segment)
                            # Check if we've reached destination
                            if destination.upper() in arrival_id.upper():
                                collecting_outbound = False
                                print(f"✓ Switched to return at segment {i+1} (arrived at {destination})")
                        else:
                            return_flights.append(segment)
                    
                    print()
                    print(f"RESULT:")
                    print(f"  Outbound segments: {len(outbound_flights)}")
                    print(f"  Return segments: {len(return_flights)}")
                    print()
                    
                    if not return_flights:
                        print("⚠️  WARNING: NO RETURN FLIGHTS DETECTED!")
                        print("   Using fallback 50/50 split...")
                        mid = len(flights_list) // 2
                        outbound_flights = flights_list[:mid]
                        return_flights = flights_list[mid:]
                        print(f"   New split: {len(outbound_flights)} outbound, {len(return_flights)} return")
                        print()
                    
                    # Show outbound route
                    print("=" * 80)
                    print("🛫 OUTBOUND ROUTE")
                    print("=" * 80)
                    if outbound_flights:
                        first = outbound_flights[0]
                        last = outbound_flights[-1]
                        print(f"From: {first.get('departure_airport', {}).get('id', 'N/A')}")
                        print(f"To: {last.get('arrival_airport', {}).get('id', 'N/A')}")
                        print(f"Segments: {len(outbound_flights)}")
                        print(f"Stops: {len(outbound_flights) - 1}")
                        if len(outbound_flights) > 1:
                            print(f"Layovers:")
                            for seg in outbound_flights[:-1]:
                                layover = seg.get('arrival_airport', {}).get('id', 'N/A')
                                print(f"  - {layover}")
                    else:
                        print("❌ NO OUTBOUND DATA")
                    print()
                    
                    # Show return route
                    print("=" * 80)
                    print("🛬 RETURN ROUTE")
                    print("=" * 80)
                    if return_flights:
                        first = return_flights[0]
                        last = return_flights[-1]
                        print(f"From: {first.get('departure_airport', {}).get('id', 'N/A')}")
                        print(f"To: {last.get('arrival_airport', {}).get('id', 'N/A')}")
                        print(f"Segments: {len(return_flights)}")
                        print(f"Stops: {len(return_flights) - 1}")
                        if len(return_flights) > 1:
                            print(f"Layovers:")
                            for seg in return_flights[:-1]:
                                layover = seg.get('arrival_airport', {}).get('id', 'N/A')
                                print(f"  - {layover}")
                    else:
                        print("❌ NO RETURN DATA - THIS IS THE BUG!")
                    print()
                    
                else:
                    print(f"❌ HTTP Error {response.status}")
                    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_flight_parsing())
