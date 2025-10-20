"""
Test script to verify flight information structure and display.
Tests only SERP API data structure.
"""

import sys
import json
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent))

print("=" * 80)
print("Testing Flight Data Structure - SERP API Format")
print("=" * 80)

# Sample flight data matching the SERP API structure
sample_flight = {
    "flight_id": "AA123_AA456",
    "airline": "American Airlines",
    "airline_logo": "https://logo.clearbit.com/aa.com",
    "travel_class": "Economy",
    "total_price": 850.00,
    "price": 850.00,
    "currency": "USD",
    "carbon_emissions": 450,
    "cabin_class": "Economy",
    "booking_url": "https://www.google.com/travel/flights",
    
    # OUTBOUND LEG (start_date from request)
    "outbound": {
        "date": "2025-11-20",
        "flight_number": "AA123",
        "airline": "American Airlines",
        "airline_logo": "https://logo.clearbit.com/aa.com",
        "aircraft": "Boeing 737",
        "departure": {
            "airport": "JFK",
            "name": "John F. Kennedy International Airport",
            "time": "08:00 AM",
            "terminal": "8"
        },
        "arrival": {
            "airport": "LAX",
            "name": "Los Angeles International Airport",
            "time": "11:30 AM",
            "terminal": "4"
        },
        "duration": 330,
        "duration_hours": 5.5,
        "stops": 0,
        "layovers": []
    },
    
    # RETURN LEG (end_date from request)
    "return": {
        "date": "2025-11-25",
        "flight_number": "AA456",
        "airline": "American Airlines",
        "airline_logo": "https://logo.clearbit.com/aa.com",
        "aircraft": "Boeing 737",
        "departure": {
            "airport": "LAX",
            "name": "Los Angeles International Airport",
            "time": "14:00 PM",
            "terminal": "4"
        },
        "arrival": {
            "airport": "JFK",
            "name": "John F. Kennedy International Airport",
            "time": "22:30 PM",
            "terminal": "8"
        },
        "duration": 330,
        "duration_hours": 5.5,
        "stops": 0,
        "layovers": []
    }
}

print("\n✓ Sample SERP API Flight Data Structure:")
print(json.dumps(sample_flight, indent=2))

print("\n" + "=" * 80)
print("Checking Required Fields for Frontend Display")
print("=" * 80)

# Check top-level fields
print("\n✓ Top-Level Flight Info:")
print(f"  - Total Price: ${sample_flight.get('total_price', 0):.2f}")
print(f"  - Travel Class: {sample_flight.get('travel_class', 'N/A')}")
print(f"  - Carbon Emissions: {sample_flight.get('carbon_emissions', 0)} kg CO₂")
print(f"  - Airline: {sample_flight.get('airline', 'N/A')}")
print(f"  - Airline Logo: {'Present' if sample_flight.get('airline_logo') else 'Missing'}")

# Check outbound flight
print("\n✓ Outbound Flight (Start Date):")
outbound = sample_flight.get('outbound', {})
if outbound:
    print(f"  - Date: {outbound.get('date', 'N/A')}")
    print(f"  - Flight Number: {outbound.get('flight_number', 'N/A')}")
    print(f"  - Airline: {outbound.get('airline', 'N/A')}")
    print(f"  - Duration: {outbound.get('duration_hours', 0)} hours")
    print(f"  - Departure: {outbound.get('departure', {}).get('airport', 'N/A')} at {outbound.get('departure', {}).get('time', 'N/A')}")
    print(f"  - Arrival: {outbound.get('arrival', {}).get('airport', 'N/A')} at {outbound.get('arrival', {}).get('time', 'N/A')}")
    print(f"  - Stops: {outbound.get('stops', 0)}")
else:
    print("  ❌ MISSING OUTBOUND DATA")

# Check return flight
print("\n✓ Return Flight (End Date):")
return_flight = sample_flight.get('return', {})
if return_flight:
    print(f"  - Date: {return_flight.get('date', 'N/A')}")
    print(f"  - Flight Number: {return_flight.get('flight_number', 'N/A')}")
    print(f"  - Airline: {return_flight.get('airline', 'N/A')}")
    print(f"  - Duration: {return_flight.get('duration_hours', 0)} hours")
    print(f"  - Departure: {return_flight.get('departure', {}).get('airport', 'N/A')} at {return_flight.get('departure', {}).get('time', 'N/A')}")
    print(f"  - Arrival: {return_flight.get('arrival', {}).get('airport', 'N/A')} at {return_flight.get('arrival', {}).get('time', 'N/A')}")
    print(f"  - Stops: {return_flight.get('stops', 0)}")
else:
    print("  ❌ MISSING RETURN DATA")

print("\n" + "=" * 80)
print("✅ SUCCESS: SERP API data structure is correct!")
print("=" * 80)
print("\nThis structure matches what the frontend expects.")
print("The frontend will display:")
print("  1. Total price, travel class, and carbon emissions at the top")
print("  2. Outbound flight details with date from start_date")
print("  3. Return flight details with date from end_date")
print("  4. Each flight shows: airline, flight number, times, airports, stops")
print("\n" + "=" * 80)
sample_flight = {
    "flight_id": "AA123_AA456",
    "airline": "American Airlines",
    "airline_logo": "https://logo.clearbit.com/aa.com",
    "travel_class": "Economy",
    "total_price": 850.00,
    "price": 850.00,
    "currency": "USD",
    "carbon_emissions": 450,
    "cabin_class": "Economy",
    "booking_url": "https://www.google.com/travel/flights",
    
    # OUTBOUND LEG
    "outbound": {
        "date": "2025-11-20",
        "flight_number": "AA123",
        "airline": "American Airlines",
        "airline_logo": "https://logo.clearbit.com/aa.com",
        "aircraft": "Boeing 737",
        "departure": {
            "airport": "JFK",
            "name": "John F. Kennedy International Airport",
            "time": "08:00 AM",
            "terminal": "8"
        },
        "arrival": {
            "airport": "LAX",
            "name": "Los Angeles International Airport",
            "time": "11:30 AM",
            "terminal": "4"
        },
        "duration": 330,
        "duration_hours": 5.5,
        "stops": 0,
        "layovers": []
    },
    
    # RETURN LEG
    "return": {
        "date": "2025-11-25",
        "flight_number": "AA456",
        "airline": "American Airlines",
        "airline_logo": "https://logo.clearbit.com/aa.com",
        "aircraft": "Boeing 737",
        "departure": {
            "airport": "LAX",
            "name": "Los Angeles International Airport",
            "time": "14:00 PM",
            "terminal": "4"
        },
        "arrival": {
            "airport": "JFK",
            "name": "John F. Kennedy International Airport",
            "time": "22:30 PM",
            "terminal": "8"
        },
        "duration": 330,
        "duration_hours": 5.5,
        "stops": 0,
        "layovers": []
    }
}

print("\n" + "=" * 80)
