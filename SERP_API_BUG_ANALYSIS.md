# CRITICAL BUG IDENTIFIED: SERP API Round-Trip Response

## Problem
SERP API's Google Flights response for **round-trip flights** only includes the **OUTBOUND** flight segments in the `flights` array. The return flight segments are NOT included.

## Evidence

### Request:
```
type: 1 (Round trip)
outbound_date: 2025-11-20
return_date: 2025-11-24
departure_id: JFK
arrival_id: DEL
```

### Response:
```json
{
  "type": "Round trip",
  "price": 4199,  ← This is round-trip price
  "flights": [
    {"departure_airport": {"id": "JFK"}, "arrival_airport": {"id": "FCO"}},
    {"departure_airport": {"id": "FCO"}, "arrival_airport": {"id": "DEL"}}
  ]  ← Only outbound flights!
}
```

**Missing:** Return flight segments (DEL → ... → JFK)

## Root Cause
SERP API's `best_flights` and `other_flights` arrays for round-trip queries **do not include return flight details** in the segments. They only show:
- Round-trip price
- Outbound flight details
- **NO return flight details**

## Solutions

### Option 1: Make Two Separate One-Way API Calls (RECOMMENDED)
```python
# Call 1: Outbound (JFK → DEL on 2025-11-20)
outbound_params = {
    'type': 2,  # One-way
    'departure_id': 'JFK',
    'arrival_id': 'DEL',
    'outbound_date': '2025-11-20'
}

# Call 2: Return (DEL → JFK on 2025-11-24)
return_params = {
    'type': 2,  # One-way
    'departure_id': 'DEL',
    'arrival_id': 'JFK',
    'outbound_date': '2025-11-24'
}

# Combine the two to create complete round-trip
```

**Pros:**
- ✅ Get complete flight details for both legs
- ✅ Can show exact return flight info
- ✅ More flexible for multi-city trips

**Cons:**
- ⚠️ Uses 2 API credits instead of 1
- ⚠️ Need to match/pair flights reasonably

### Option 2: Use SERP API's Booking Token
Some SERP API responses include a `departure_token` which can be used to get full trip details, but this requires additional API calls.

### Option 3: Accept Limitation and Show Estimate
Show outbound flights from API, and note that return flight details will be similar (same airline, similar route in reverse).

**Pros:**
- ✅ Uses only 1 API call
- ✅ Faster response

**Cons:**
- ❌ Not showing actual return flight details
- ❌ User doesn't see complete picture

## Recommended Fix

**Implement Option 1:**

1. Modify `_fetch_serpapi_flights()` to make TWO separate calls
2. First call: outbound flights (origin → destination)
3. Second call: return flights (destination → origin)
4. Match them by price/airline/timing
5. Create complete round-trip flight objects

## Implementation Plan

```python
async def _fetch_serpapi_flights(...):
    # Fetch outbound flights
    outbound_flights = await self._fetch_one_way_flights(
        origin, destination, start_date, passengers, budget
    )
    
    # Fetch return flights
    return_flights = await self._fetch_one_way_flights(
        destination, origin, end_date, passengers, budget
    )
    
    # Pair them intelligently
    round_trips = self._pair_flights(outbound_flights, return_flights)
    
    return round_trips
```

## Current Status

❌ **BUG CONFIRMED**: Return flights are NOT being shown because SERP API doesn't provide them in round-trip responses.

✅ **Fix Required**: Change to separate one-way API calls for outbound and return.

## Impact

- Users only see outbound journey (JFK → ZRH → DEL)
- Users DO NOT see return journey (DEL → ZRH → JFK)
- This explains the user's report exactly!
