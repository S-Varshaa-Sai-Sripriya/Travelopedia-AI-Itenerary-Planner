"""
API Manager for real-time and mock data integration.
Handles flights, hotels, weather, and activities data retrieval.
"""

import os
import random
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import yaml
from dotenv import load_dotenv
from backend.utils.logger import get_logger

# Load environment variables
load_dotenv()

logger = get_logger(__name__)


class APIManager:
    """Manages API calls for travel data with mock fallback."""
    
    def __init__(self, config_path: str = "backend/utils/config.yaml"):
        """Initialize API manager with configuration."""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        self.api_config = self.config['apis']
        
        # Load API keys from environment
        self.openweather_key = os.getenv('OPENWEATHER_API_KEY')
        self.aviationstack_key = os.getenv('AVIATIONSTACK_API_KEY')
        self.rapidapi_key = os.getenv('RAPIDAPI_KEY')
        self.foursquare_key = os.getenv('FOURSQUARE_API_KEY')
        self.yelp_key = os.getenv('YELP_API_KEY')
        
        logger.info("API Manager initialized with real API keys")
    
    async def fetch_flights(
        self,
        origin: str,
        destination: str,
        start_date: str,
        end_date: str,
        passengers: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Fetch flight options.
        
        Args:
            origin: Origin city/airport
            destination: Destination city/airport
            start_date: Departure date (YYYY-MM-DD)
            end_date: Return date (YYYY-MM-DD)
            passengers: Number of passengers
            
        Returns:
            List of flight options
        """
        logger.info(f"Fetching flights: {origin} → {destination}")
        
        if self.api_config['flight']['enabled']:
            # Real API integration would go here
            logger.debug("Using real flight API")
            return await self._fetch_real_flights(origin, destination, start_date, end_date, passengers)
        else:
            logger.debug("Using mock flight data")
            return self._generate_mock_flights(origin, destination, start_date, end_date, passengers)
    
    async def fetch_hotels(
        self,
        destination: str,
        check_in: str,
        check_out: str,
        guests: int = 1,
        min_rating: float = 3.0
    ) -> List[Dict[str, Any]]:
        """
        Fetch hotel options.
        
        Args:
            destination: Destination city
            check_in: Check-in date (YYYY-MM-DD)
            check_out: Check-out date (YYYY-MM-DD)
            guests: Number of guests
            min_rating: Minimum hotel rating
            
        Returns:
            List of hotel options
        """
        logger.info(f"Fetching hotels in {destination}")
        
        if self.api_config['hotel']['enabled']:
            logger.debug("Using real hotel API")
            return await self._fetch_real_hotels(destination, check_in, check_out, guests, min_rating)
        else:
            logger.debug("Using mock hotel data")
            return self._generate_mock_hotels(destination, check_in, check_out, guests, min_rating)
    
    async def fetch_weather(
        self,
        destination: str,
        date: str
    ) -> Dict[str, Any]:
        """
        Fetch weather forecast.
        
        Args:
            destination: Destination city
            date: Date for forecast (YYYY-MM-DD)
            
        Returns:
            Weather information
        """
        logger.info(f"Fetching weather for {destination} on {date}")
        
        if self.api_config['weather']['enabled']:
            logger.debug("Using real weather API")
            return await self._fetch_real_weather(destination, date)
        else:
            logger.debug("Using mock weather data")
            return self._generate_mock_weather(destination, date)
    
    def _generate_mock_flights(
        self,
        origin: str,
        destination: str,
        start_date: str,
        end_date: str,
        passengers: int
    ) -> List[Dict[str, Any]]:
        """Generate mock flight data."""
        airlines = ["United", "Delta", "American Airlines", "Emirates", "Singapore Airlines", "Lufthansa"]
        aircraft = ["Boeing 737", "Airbus A320", "Boeing 787", "Airbus A350"]
        
        base_price = random.randint(300, 1500)
        
        flights = []
        for i in range(3):
            price_multiplier = 1 + (i * 0.2)
            flights.append({
                "flight_id": f"FL{random.randint(1000, 9999)}",
                "airline": random.choice(airlines),
                "aircraft": random.choice(aircraft),
                "outbound": {
                    "departure": {
                        "airport": origin,
                        "time": f"{start_date}T08:00:00Z",
                        "terminal": f"T{random.randint(1, 4)}"
                    },
                    "arrival": {
                        "airport": destination,
                        "time": f"{start_date}T16:00:00Z",
                        "terminal": f"T{random.randint(1, 4)}"
                    },
                    "duration_hours": random.randint(6, 18),
                    "stops": random.randint(0, 2)
                },
                "return": {
                    "departure": {
                        "airport": destination,
                        "time": f"{end_date}T10:00:00Z",
                        "terminal": f"T{random.randint(1, 4)}"
                    },
                    "arrival": {
                        "airport": origin,
                        "time": f"{end_date}T18:00:00Z",
                        "terminal": f"T{random.randint(1, 4)}"
                    },
                    "duration_hours": random.randint(6, 18),
                    "stops": random.randint(0, 2)
                },
                "price": round(base_price * price_multiplier * passengers, 2),
                "currency": "USD",
                "cabin_class": ["Economy", "Premium Economy", "Business"][i] if i < 3 else "Economy",
                "baggage_allowance": f"{20 + (i * 10)}kg",
                "amenities": ["WiFi", "Meals", "Entertainment", "Power Outlets"][: 2 + i],
                "carbon_emissions": round(random.uniform(200, 800), 2),
                "booking_url": f"https://example.com/book/{random.randint(10000, 99999)}"
            })
        
        return flights
    
    def _generate_mock_hotels(
        self,
        destination: str,
        check_in: str,
        check_out: str,
        guests: int,
        min_rating: float
    ) -> List[Dict[str, Any]]:
        """Generate mock hotel data."""
        hotel_types = ["Resort", "Hotel", "Boutique Hotel", "Villa", "Hostel"]
        hotel_names = [
            "Paradise Resort", "Grand Palace Hotel", "Sunset Villa",
            "Ocean View Resort", "Mountain Lodge", "Urban Boutique",
            "Coastal Retreat", "City Center Hotel", "Luxury Suites"
        ]
        
        amenities_pool = [
            "Free WiFi", "Swimming Pool", "Spa", "Gym", "Restaurant",
            "Bar", "Room Service", "Airport Shuttle", "Parking",
            "Beach Access", "Business Center", "Concierge"
        ]
        
        check_in_dt = datetime.strptime(check_in, "%Y-%m-%d")
        check_out_dt = datetime.strptime(check_out, "%Y-%m-%d")
        nights = (check_out_dt - check_in_dt).days
        
        hotels = []
        for i in range(5):
            rating = round(random.uniform(max(min_rating, 3.5), 5.0), 1)
            price_per_night = random.randint(80, 500) * (rating / 3.5)
            
            hotels.append({
                "hotel_id": f"HTL{random.randint(1000, 9999)}",
                "name": random.choice(hotel_names),
                "type": random.choice(hotel_types),
                "rating": rating,
                "review_count": random.randint(100, 5000),
                "location": {
                    "address": f"{random.randint(1, 999)} {destination} Street",
                    "city": destination,
                    "distance_to_center": round(random.uniform(0.5, 10), 1),
                    "coordinates": {
                        "lat": round(random.uniform(-90, 90), 6),
                        "lng": round(random.uniform(-180, 180), 6)
                    }
                },
                "price": {
                    "per_night": round(price_per_night, 2),
                    "total": round(price_per_night * nights, 2),
                    "currency": "USD",
                    "includes_tax": True
                },
                "room_type": ["Standard Room", "Deluxe Room", "Suite", "Executive Suite"][min(i, 3)],
                "amenities": random.sample(amenities_pool, k=random.randint(4, 8)),
                "policies": {
                    "check_in": "14:00",
                    "check_out": "11:00",
                    "cancellation": "Free cancellation until 24h before check-in"
                },
                "images": [
                    f"https://example.com/images/hotel{i}_{j}.jpg" for j in range(3)
                ],
                "booking_url": f"https://example.com/book/hotel/{random.randint(10000, 99999)}"
            })
        
        # Sort by rating
        hotels.sort(key=lambda x: x['rating'], reverse=True)
        return hotels
    
    def _generate_mock_weather(self, destination: str, date: str) -> Dict[str, Any]:
        """Generate mock weather data."""
        conditions = ["Sunny", "Partly Cloudy", "Cloudy", "Rainy", "Stormy", "Clear"]
        
        # Base temperature on month (simple approximation)
        month = int(date.split('-')[1])
        base_temp = 15 + (10 * abs(month - 7) / 7)  # Warmer in summer
        
        return {
            "date": date,
            "location": destination,
            "condition": random.choice(conditions),
            "temperature": {
                "current": round(base_temp + random.uniform(-5, 5), 1),
                "high": round(base_temp + random.uniform(5, 10), 1),
                "low": round(base_temp - random.uniform(0, 5), 1),
                "unit": "°C"
            },
            "humidity": random.randint(40, 90),
            "wind_speed": round(random.uniform(5, 30), 1),
            "precipitation_chance": random.randint(0, 100),
            "uv_index": random.randint(1, 11),
            "sunrise": "06:30 AM",
            "sunset": "18:30 PM",
            "icon": "☀️" if random.choice([True, False]) else "⛅"
        }
    
    async def _fetch_real_flights(
        self,
        origin: str,
        destination: str,
        start_date: str,
        end_date: str,
        passengers: int
    ):
        """Fetch real flight data from Aviationstack API."""
        if not self.aviationstack_key:
            logger.warning("Aviationstack API key not found, using mock data")
            return self._generate_mock_flights(origin, destination, start_date, end_date, passengers)
        
        try:
            # Aviationstack API endpoint
            url = "http://api.aviationstack.com/v1/flights"
            
            async with aiohttp.ClientSession() as session:
                # Search for outbound flights
                params = {
                    'access_key': self.aviationstack_key,
                    'dep_iata': origin,
                    'arr_iata': destination,
                    'flight_date': start_date,
                    'limit': 10
                }
                
                async with session.get(url, params=params, timeout=self.api_config['flight']['timeout']) as response:
                    if response.status == 200:
                        data = await response.json()
                        flights = self._parse_aviationstack_response(data, origin, destination, start_date, end_date, passengers)
                        
                        if flights:
                            logger.info(f"✅ Fetched {len(flights)} real flights from Aviationstack")
                            return flights
                        else:
                            logger.warning("No flights found in API response, using mock data")
                            return self._generate_mock_flights(origin, destination, start_date, end_date, passengers)
                    else:
                        logger.warning(f"Aviationstack API error {response.status}, using mock data")
                        return self._generate_mock_flights(origin, destination, start_date, end_date, passengers)
        
        except Exception as e:
            logger.error(f"Error fetching flights from Aviationstack: {e}")
            return self._generate_mock_flights(origin, destination, start_date, end_date, passengers)
    
    def _parse_aviationstack_response(self, data: Dict, origin: str, destination: str, start_date: str, end_date: str, passengers: int) -> List[Dict]:
        """Parse Aviationstack API response into our format."""
        flights = []
        
        if 'data' not in data or not data['data']:
            return []
        
        # Take up to 3 flights
        for flight_data in data['data'][:3]:
            try:
                flight_info = flight_data.get('flight', {})
                departure = flight_data.get('departure', {})
                arrival = flight_data.get('arrival', {})
                airline = flight_data.get('airline', {})
                
                # Calculate estimated price (Aviationstack doesn't provide prices in free tier)
                base_price = random.randint(300, 1500) * passengers
                
                flights.append({
                    "flight_id": flight_info.get('iata', f"FL{random.randint(1000, 9999)}"),
                    "airline": airline.get('name', 'Unknown Airline'),
                    "aircraft": flight_data.get('aircraft', {}).get('registration', 'Unknown'),
                    "outbound": {
                        "departure": {
                            "airport": departure.get('iata', origin),
                            "time": departure.get('scheduled', start_date),
                            "terminal": departure.get('terminal', 'N/A')
                        },
                        "arrival": {
                            "airport": arrival.get('iata', destination),
                            "time": arrival.get('scheduled', start_date),
                            "terminal": arrival.get('terminal', 'N/A')
                        },
                        "duration_hours": 8,  # Estimated
                        "stops": 0
                    },
                    "return": {
                        "departure": {
                            "airport": destination,
                            "time": f"{end_date}T10:00:00Z",
                            "terminal": "N/A"
                        },
                        "arrival": {
                            "airport": origin,
                            "time": f"{end_date}T18:00:00Z",
                            "terminal": "N/A"
                        },
                        "duration_hours": 8,
                        "stops": 0
                    },
                    "price": round(base_price, 2),
                    "currency": "USD",
                    "cabin_class": "Economy",
                    "baggage_allowance": "20kg",
                    "amenities": ["Meals", "Entertainment"],
                    "carbon_emissions": 450.0,
                    "booking_url": f"https://booking.com/flights"
                })
            except Exception as e:
                logger.warning(f"Error parsing flight data: {e}")
                continue
        
        return flights if flights else []
    
    async def _fetch_real_hotels(
        self,
        destination: str,
        check_in: str,
        check_out: str,
        guests: int,
        min_rating: float
    ):
        """Fetch real hotel data from Booking.com via RapidAPI."""
        if not self.rapidapi_key:
            logger.warning("RapidAPI key not found, using mock data")
            return self._generate_mock_hotels(destination, check_in, check_out, guests, min_rating)
        
        try:
            async with aiohttp.ClientSession() as session:
                # Updated: Using booking-com15 API endpoint
                search_url = "https://booking-com15.p.rapidapi.com/api/v1/hotels/searchDestination"
                headers = {
                    "X-RapidAPI-Key": self.rapidapi_key,
                    "X-RapidAPI-Host": "booking-com15.p.rapidapi.com"
                }
                
                params = {
                    "query": destination
                }
                
                async with session.get(search_url, headers=headers, params=params, timeout=self.api_config['hotel']['timeout']) as response:
                    if response.status != 200:
                        logger.warning(f"Booking.com API destination search error {response.status}, using mock data")
                        return self._generate_mock_hotels(destination, check_in, check_out, guests, min_rating)
                    
                    dest_data = await response.json()
                    
                    if not dest_data.get('data') or len(dest_data['data']) == 0:
                        logger.warning("No destinations found, using mock data")
                        return self._generate_mock_hotels(destination, check_in, check_out, guests, min_rating)
                    
                    # Get the first destination result
                    dest_id = dest_data['data'][0].get('dest_id')
                
                # Step 2: Search hotels at destination
                hotels_url = "https://booking-com15.p.rapidapi.com/api/v1/hotels/searchHotels"
                hotel_params = {
                    "dest_id": dest_id,
                    "search_type": "CITY",
                    "arrival_date": check_in,
                    "departure_date": check_out,
                    "adults": guests,
                    "room_qty": 1,
                    "page_number": 1,
                    "units": "metric",
                    "temperature_unit": "c",
                    "languagecode": "en-us",
                    "currency_code": "USD"
                }
                
                async with session.get(hotels_url, headers=headers, params=hotel_params, timeout=self.api_config['hotel']['timeout']) as response:
                    if response.status == 200:
                        data = await response.json()
                        hotels = self._parse_booking15_response(data, check_in, check_out, min_rating)
                        
                        if hotels:
                            logger.info(f"✅ Fetched {len(hotels)} real hotels from Booking.com")
                            return hotels
                        else:
                            logger.warning("No hotels found in API response, using mock data")
                            return self._generate_mock_hotels(destination, check_in, check_out, guests, min_rating)
                    else:
                        error_text = await response.text()
                        logger.warning(f"Booking.com API hotels search error {response.status}: {error_text[:200]}, using mock data")
                        return self._generate_mock_hotels(destination, check_in, check_out, guests, min_rating)
        
        except Exception as e:
            logger.error(f"Error fetching hotels from Booking.com: {e}")
            return self._generate_mock_hotels(destination, check_in, check_out, guests, min_rating)
    
    def _parse_booking15_response(self, data: Dict, check_in: str, check_out: str, min_rating: float) -> List[Dict]:
        """Parse Booking.com15 API response into our format."""
        hotels = []
        
        if 'data' not in data or 'hotels' not in data['data']:
            return []
        
        check_in_dt = datetime.strptime(check_in, "%Y-%m-%d")
        check_out_dt = datetime.strptime(check_out, "%Y-%m-%d")
        nights = (check_out_dt - check_in_dt).days
        
        for hotel_data in data['data']['hotels'][:5]:
            try:
                # Extract rating (convert from 10-scale to 5-scale)
                review_score = hotel_data.get('review_score', 0)
                rating = round(review_score / 2, 1) if review_score else 4.0
                
                if rating < min_rating:
                    continue
                
                # Extract price
                price_breakdown = hotel_data.get('price_breakdown', {})
                gross_price = float(price_breakdown.get('gross_price', {}).get('value', 100))
                price_per_night = gross_price / max(nights, 1)
                
                # Extract location
                location_data = hotel_data.get('property', {})
                
                hotels.append({
                    "hotel_id": str(hotel_data.get('hotel_id', random.randint(1000, 9999))),
                    "name": hotel_data.get('hotel_name', 'Unknown Hotel'),
                    "type": hotel_data.get('accommodation_type_name', 'Hotel'),
                    "rating": rating,
                    "review_count": hotel_data.get('review_nr', 0),
                    "location": {
                        "address": location_data.get('address', 'N/A'),
                        "city": location_data.get('city', 'Unknown'),
                        "distance_to_center": round(float(hotel_data.get('distance_to_cc', 0)), 1),
                        "coordinates": {
                            "lat": float(location_data.get('latitude', 0)),
                            "lng": float(location_data.get('longitude', 0))
                        }
                    },
                    "price": {
                        "per_night": round(price_per_night, 2),
                        "total": round(gross_price, 2),
                        "currency": price_breakdown.get('currency', 'USD'),
                        "includes_tax": True
                    },
                    "room_type": hotel_data.get('unit_configuration_label', 'Standard Room'),
                    "amenities": hotel_data.get('hotel_facilities', [])[:8],
                    "policies": {
                        "check_in": "14:00",
                        "check_out": "11:00",
                        "cancellation": "Check hotel policy"
                    },
                    "images": [hotel_data.get('main_photo_url', '')] if hotel_data.get('main_photo_url') else [],
                    "booking_url": hotel_data.get('url', 'https://booking.com')
                })
            except Exception as e:
                logger.warning(f"Error parsing hotel data: {e}")
                continue
        
        return hotels if hotels else []
    
    async def _fetch_real_weather(self, destination: str, date: str):
        """Fetch real weather data from OpenWeatherMap API."""
        if not self.openweather_key:
            logger.warning("OpenWeatherMap API key not found, using mock data")
            return self._generate_mock_weather(destination, date)
        
        try:
            async with aiohttp.ClientSession() as session:
                # Get coordinates for the destination first
                geo_url = "http://api.openweathermap.org/geo/1.0/direct"
                geo_params = {
                    'q': destination,
                    'limit': 1,
                    'appid': self.openweather_key
                }
                
                async with session.get(geo_url, params=geo_params, timeout=self.api_config['weather']['timeout']) as response:
                    if response.status != 200:
                        logger.warning(f"OpenWeatherMap Geocoding API error {response.status}")
                        return self._generate_mock_weather(destination, date)
                    
                    geo_data = await response.json()
                    if not geo_data:
                        logger.warning("Location not found, using mock data")
                        return self._generate_mock_weather(destination, date)
                    
                    lat = geo_data[0]['lat']
                    lon = geo_data[0]['lon']
                
                # Get weather forecast
                weather_url = "http://api.openweathermap.org/data/2.5/forecast"
                weather_params = {
                    'lat': lat,
                    'lon': lon,
                    'appid': self.openweather_key,
                    'units': 'metric'  # Celsius
                }
                
                async with session.get(weather_url, params=weather_params, timeout=self.api_config['weather']['timeout']) as response:
                    if response.status == 200:
                        data = await response.json()
                        weather = self._parse_openweather_response(data, destination, date)
                        logger.info(f"✅ Fetched real weather for {destination}")
                        return weather
                    else:
                        logger.warning(f"OpenWeatherMap API error {response.status}, using mock data")
                        return self._generate_mock_weather(destination, date)
        
        except Exception as e:
            logger.error(f"Error fetching weather from OpenWeatherMap: {e}")
            return self._generate_mock_weather(destination, date)
    
    def _parse_openweather_response(self, data: Dict, destination: str, date: str) -> Dict:
        """Parse OpenWeatherMap API response into our format."""
        try:
            # Get forecast for the requested date
            target_date = datetime.strptime(date, "%Y-%m-%d").date()
            
            # Find forecast closest to target date
            forecast_data = None
            for item in data.get('list', []):
                forecast_date = datetime.fromtimestamp(item['dt']).date()
                if forecast_date == target_date:
                    forecast_data = item
                    break
            
            # If no exact match, use first forecast
            if not forecast_data and data.get('list'):
                forecast_data = data['list'][0]
            
            if not forecast_data:
                return self._generate_mock_weather(destination, date)
            
            main = forecast_data.get('main', {})
            weather = forecast_data.get('weather', [{}])[0]
            wind = forecast_data.get('wind', {})
            
            # Map weather condition to emoji
            condition_icons = {
                'Clear': '☀️',
                'Clouds': '⛅',
                'Rain': '🌧️',
                'Drizzle': '🌦️',
                'Thunderstorm': '⛈️',
                'Snow': '❄️',
                'Mist': '🌫️',
                'Fog': '🌫️'
            }
            
            return {
                "date": date,
                "location": destination,
                "condition": weather.get('main', 'Clear'),
                "description": weather.get('description', 'clear sky'),
                "temperature": {
                    "current": round(main.get('temp', 20), 1),
                    "high": round(main.get('temp_max', 25), 1),
                    "low": round(main.get('temp_min', 15), 1),
                    "feels_like": round(main.get('feels_like', 20), 1),
                    "unit": "°C"
                },
                "humidity": main.get('humidity', 50),
                "wind_speed": round(wind.get('speed', 5), 1),
                "precipitation_chance": int(forecast_data.get('pop', 0) * 100),
                "uv_index": random.randint(1, 11),  # Not provided by free tier
                "sunrise": "06:30 AM",  # Would need current weather endpoint
                "sunset": "18:30 PM",
                "icon": condition_icons.get(weather.get('main'), '🌤️')
            }
        
        except Exception as e:
            logger.error(f"Error parsing weather data: {e}")
            return self._generate_mock_weather(destination, date)
    
    async def fetch_activities(
        self,
        destination: str,
        preferences: List[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Fetch activities and points of interest.
        
        Args:
            destination: Destination city
            preferences: User preferences (adventure, culture, etc.)
            limit: Maximum number of activities
            
        Returns:
            List of activities
        """
        logger.info(f"Fetching activities in {destination}")
        
        if self.api_config.get('activities', {}).get('enabled', False):
            logger.debug("Using real activities API")
            return await self._fetch_real_activities(destination, preferences, limit)
        else:
            logger.debug("Using mock activities data")
            return self._generate_mock_activities(destination, preferences, limit)
    
    async def _fetch_real_activities(
        self,
        destination: str,
        preferences: List[str],
        limit: int
    ):
        """Fetch real activities from OSM/Nominatim, Yelp, or other APIs."""
        provider = self.api_config.get('activities', {}).get('provider', 'osm_nominatim')
        
        if provider == 'osm_nominatim':
            return await self._fetch_osm_nominatim_activities(destination, preferences, limit)
        elif provider == 'yelp' and self.yelp_key:
            return await self._fetch_yelp_activities(destination, preferences, limit)
        elif provider == 'opentripmap':
            return await self._fetch_opentripmap_activities(destination, preferences, limit)
        elif provider == 'foursquare' and self.foursquare_key:
            return await self._fetch_foursquare_activities(destination, preferences, limit)
        else:
            logger.warning(f"Activities provider '{provider}' not configured, using mock data")
            return self._generate_mock_activities(destination, preferences, limit)
    
    async def _fetch_osm_nominatim_activities(
        self,
        destination: str,
        preferences: List[str],
        limit: int
    ):
        """
        Fetch activities from OpenStreetMap/Nominatim + Wikipedia.
        100% FREE - NO API KEY REQUIRED!
        """
        try:
            async with aiohttp.ClientSession() as session:
                user_agent = self.api_config.get('activities', {}).get('osm_nominatim', {}).get('user_agent', 'Travelopedia/1.0')
                headers = {'User-Agent': user_agent}
                
                # Step 1: Geocode the destination
                geocode_url = "https://nominatim.openstreetmap.org/search"
                geocode_params = {
                    'q': destination,
                    'format': 'json',
                    'limit': 1
                }
                
                await asyncio.sleep(1)  # Rate limit: 1 req/sec
                
                async with session.get(geocode_url, params=geocode_params, headers=headers, timeout=10) as response:
                    if response.status != 200:
                        logger.warning(f"Nominatim geocoding error {response.status}, using mock data")
                        return self._generate_mock_activities(destination, preferences, limit)
                    
                    geo_data = await response.json()
                    if not geo_data:
                        logger.warning("Could not geocode destination, using mock data")
                        return self._generate_mock_activities(destination, preferences, limit)
                    
                    lat = float(geo_data[0]['lat'])
                    lon = float(geo_data[0]['lon'])
                
                # Step 2: Search for POIs using Overpass API (OpenStreetMap)
                # Map preferences to OSM tags
                tag_mapping = {
                    'adventure': ['sport', 'climbing', 'diving_centre'],
                    'cultural': ['museum', 'theatre', 'art_gallery', 'historic', 'monument'],
                    'culinary': ['restaurant', 'cafe', 'bar'],
                    'nature': ['park', 'garden', 'beach', 'viewpoint', 'nature_reserve'],
                    'relaxation': ['spa', 'wellness_centre'],
                    'family_friendly': ['zoo', 'aquarium', 'theme_park', 'playground']
                }
                
                # Build list of tags based on preferences
                search_tags = []
                if preferences:
                    for pref in preferences:
                        if pref.lower() in tag_mapping:
                            search_tags.extend(tag_mapping[pref.lower()])
                
                # Default tags if none specified
                if not search_tags:
                    search_tags = ['tourism', 'museum', 'monument', 'park', 'viewpoint']
                
                # Remove duplicates
                search_tags = list(set(search_tags))[:5]  # Limit to 5 tags
                
                # Use Overpass API to search for POIs
                radius = self.api_config.get('activities', {}).get('osm_nominatim', {}).get('radius', 10000)
                
                # Build Overpass QL query
                tag_queries = []
                for tag in search_tags:
                    tag_queries.append(f'node["tourism"="{tag}"]({lat-0.1},{lon-0.1},{lat+0.1},{lon+0.1});')
                    tag_queries.append(f'node["amenity"="{tag}"]({lat-0.1},{lon-0.1},{lat+0.1},{lon+0.1});')
                    tag_queries.append(f'node["leisure"="{tag}"]({lat-0.1},{lon-0.1},{lat+0.1},{lon+0.1});')
                
                overpass_query = f"""
                [out:json][timeout:25];
                (
                  node["tourism"]({lat-0.05},{lon-0.05},{lat+0.05},{lon+0.05});
                  node["amenity"~"museum|theatre|arts_centre|cinema"]({lat-0.05},{lon-0.05},{lat+0.05},{lon+0.05});
                  node["leisure"~"park|garden|beach_resort"]({lat-0.05},{lon-0.05},{lat+0.05},{lon+0.05});
                  node["historic"]({lat-0.05},{lon-0.05},{lat+0.05},{lon+0.05});
                );
                out body;
                >;
                out skel qt;
                """
                
                await asyncio.sleep(1)  # Rate limit
                
                overpass_url = "https://overpass-api.de/api/interpreter"
                async with session.post(overpass_url, data={'data': overpass_query}, headers=headers, timeout=30) as response:
                    if response.status != 200:
                        logger.warning(f"Overpass API error {response.status}, using mock data")
                        return self._generate_mock_activities(destination, preferences, limit)
                    
                    osm_data = await response.json()
                    
                    # Parse OSM data
                    activities = []
                    for element in osm_data.get('elements', [])[:limit * 2]:
                        activity = self._parse_osm_element(element, preferences, destination)
                        if activity:
                            activities.append(activity)
                        
                        if len(activities) >= limit:
                            break
                    
                    if activities:
                        logger.info(f"✅ Fetched {len(activities)} real activities from OpenStreetMap (100% FREE!)")
                        return activities
                    else:
                        logger.warning("No activities found in OSM response, using mock data")
                        return self._generate_mock_activities(destination, preferences, limit)
        
        except Exception as e:
            logger.error(f"Error fetching activities from OSM/Nominatim: {e}")
            return self._generate_mock_activities(destination, preferences, limit)
    
    def _parse_osm_element(self, element: Dict, preferences: List[str], destination: str) -> Dict:
        """Parse OpenStreetMap element into our activity format."""
        try:
            tags = element.get('tags', {})
            
            # Get name
            name = tags.get('name', tags.get('name:en', ''))
            if not name:
                return None
            
            # Determine category and type
            tourism_type = tags.get('tourism', '')
            amenity_type = tags.get('amenity', '')
            leisure_type = tags.get('leisure', '')
            historic_type = tags.get('historic', '')
            
            # Map to our categories
            category = 'cultural'
            activity_type = 'Attraction'
            
            if tourism_type in ['museum', 'gallery', 'artwork']:
                category = 'cultural'
                activity_type = 'Museum/Gallery'
            elif tourism_type in ['viewpoint', 'attraction']:
                category = 'nature'
                activity_type = 'Viewpoint'
            elif tourism_type == 'hotel' or amenity_type == 'restaurant':
                return None  # Skip hotels/restaurants
            elif leisure_type in ['park', 'garden', 'beach_resort']:
                category = 'nature'
                activity_type = 'Park/Garden'
            elif historic_type:
                category = 'cultural'
                activity_type = 'Historic Site'
            elif amenity_type in ['theatre', 'cinema', 'arts_centre']:
                category = 'cultural'
                activity_type = 'Entertainment'
            
            # Get location
            lat = element.get('lat', 0)
            lon = element.get('lon', 0)
            
            # Build description
            description = f"{activity_type} in {destination}."
            if tags.get('description'):
                description = tags['description']
            elif tags.get('wikipedia'):
                description = f"Historic {activity_type.lower()} with Wikipedia entry."
            
            # Estimate rating (OSM doesn't have ratings)
            rating = round(random.uniform(4.0, 4.8), 1)
            
            # Get address
            address = tags.get('addr:full', '')
            if not address:
                street = tags.get('addr:street', '')
                housenumber = tags.get('addr:housenumber', '')
                city = tags.get('addr:city', destination)
                if street:
                    address = f"{housenumber} {street}, {city}".strip()
                else:
                    address = city
            
            # Duration based on type
            duration_map = {
                'Museum/Gallery': 2,
                'Historic Site': 2,
                'Park/Garden': 3,
                'Viewpoint': 1,
                'Entertainment': 3
            }
            
            return {
                "activity_id": f"OSM{element.get('id', random.randint(1000, 9999))}",
                "name": name,
                "type": activity_type,
                "category": category,
                "description": description,
                "location": {
                    "address": address,
                    "coordinates": {
                        "lat": lat,
                        "lng": lon
                    }
                },
                "rating": rating,
                "price_level": 1 if tags.get('fee') == 'no' else 2,
                "price": 0 if tags.get('fee') == 'no' else random.choice([10, 15, 20, 25]),  # Estimated entry fee
                "duration_hours": duration_map.get(activity_type, 2),
                "best_time": random.choice(['Morning', 'Afternoon', 'Full Day']),
                "tags": [tourism_type, amenity_type, leisure_type, historic_type] if tourism_type or amenity_type or leisure_type or historic_type else [],
                "website": tags.get('website', tags.get('url', '')),
                "wikipedia": tags.get('wikipedia', ''),
                "photos": []
            }
        
        except Exception as e:
            logger.warning(f"Error parsing OSM element: {e}")
            return None
    
    async def _fetch_yelp_activities(
        self,
        destination: str,
        preferences: List[str],
        limit: int
    ):
        """Fetch activities from Yelp Fusion API (FREE 5,000 calls/day!)."""
        if not self.yelp_key:
            logger.warning("Yelp API key not found, using mock data")
            return self._generate_mock_activities(destination, preferences, limit)
        
        try:
            async with aiohttp.ClientSession() as session:
                # Yelp Fusion API v3
                url = "https://api.yelp.com/v3/businesses/search"
                headers = {
                    "Authorization": f"Bearer {self.yelp_key}",
                    "Accept": "application/json"
                }
                
                # Map preferences to Yelp categories
                category_mapping = {
                    'adventure': 'active,hiking,climbing,diving',
                    'cultural': 'arts,museums,galleries,theater,tours',
                    'culinary': 'restaurants,food,cafes,bars',
                    'nature': 'parks,hiking,beaches',
                    'relaxation': 'spas,massage,wellness',
                    'family_friendly': 'zoos,amusementparks,aquariums',
                    'nightlife': 'nightlife,bars,clubs',
                    'shopping': 'shopping'
                }
                
                # Build categories filter
                categories = []
                if preferences:
                    for pref in preferences:
                        if pref.lower() in category_mapping:
                            categories.extend(category_mapping[pref.lower()].split(','))
                
                # Default categories if none specified
                if not categories:
                    categories = ['arts', 'active', 'food', 'tours']
                
                # Remove duplicates
                categories = list(set(categories))[:3]  # Yelp allows max 3 categories
                
                # Get config values
                radius = self.api_config.get('activities', {}).get('yelp', {}).get('radius', 10000)
                
                params = {
                    'location': destination,
                    'categories': ','.join(categories),
                    'limit': min(limit, 50),  # Max 50 per request
                    'radius': min(radius, 40000),  # Max 40km
                    'sort_by': 'rating'  # Sort by rating
                }
                
                async with session.get(url, headers=headers, params=params, timeout=self.api_config.get('activities', {}).get('timeout', 15)) as response:
                    if response.status == 200:
                        data = await response.json()
                        activities = self._parse_yelp_response(data, preferences)
                        
                        if activities:
                            logger.info(f"✅ Fetched {len(activities)} real activities from Yelp Fusion API (FREE!)")
                            return activities
                        else:
                            logger.warning("No activities found in Yelp response, using mock data")
                            return self._generate_mock_activities(destination, preferences, limit)
                    elif response.status == 401:
                        error_text = await response.text()
                        logger.warning(f"Yelp API 401 Unauthorized: {error_text[:200]}")
                        logger.warning("Please check your YELP_API_KEY in .env file")
                        return self._generate_mock_activities(destination, preferences, limit)
                    else:
                        error_text = await response.text()
                        logger.warning(f"Yelp API error {response.status}: {error_text[:200]}, using mock data")
                        return self._generate_mock_activities(destination, preferences, limit)
        
        except Exception as e:
            logger.error(f"Error fetching activities from Yelp: {e}")
            return self._generate_mock_activities(destination, preferences, limit)
    
    def _parse_yelp_response(self, data: Dict, preferences: List[str]) -> List[Dict]:
        """Parse Yelp Fusion API response into our format."""
        activities = []
        
        if 'businesses' not in data:
            return []
        
        for business in data['businesses']:
            try:
                # Extract categories
                categories = business.get('categories', [])
                category_names = [cat.get('title', '') for cat in categories]
                
                # Determine activity type from categories
                activity_type = category_names[0] if category_names else 'Attraction'
                
                # Map to our preference categories
                activity_category = 'cultural'
                category_str = ' '.join(category_names).lower()
                
                if any(word in category_str for word in ['park', 'outdoor', 'hiking', 'beach', 'nature']):
                    activity_category = 'nature'
                elif any(word in category_str for word in ['restaurant', 'food', 'cafe', 'bar', 'dining']):
                    activity_category = 'culinary'
                elif any(word in category_str for word in ['museum', 'art', 'gallery', 'theater', 'cultural', 'tour']):
                    activity_category = 'cultural'
                elif any(word in category_str for word in ['spa', 'wellness', 'massage', 'yoga']):
                    activity_category = 'relaxation'
                elif any(word in category_str for word in ['active', 'sport', 'climbing', 'diving', 'adventure']):
                    activity_category = 'adventure'
                elif any(word in category_str for word in ['nightlife', 'club', 'bar']):
                    activity_category = 'nightlife'
                
                # Extract location
                location_data = business.get('location', {})
                coordinates = business.get('coordinates', {})
                
                # Extract rating
                rating = business.get('rating', 4.0)
                
                # Extract price level ($ to $$$$)
                price_str = business.get('price', '$$')
                price_level = len(price_str) if price_str else 2
                
                # Estimate duration based on category
                duration_map = {
                    'nature': random.randint(2, 4),
                    'cultural': random.randint(1, 3),
                    'adventure': random.randint(2, 5),
                    'culinary': random.randint(1, 2),
                    'relaxation': random.randint(1, 3),
                    'nightlife': random.randint(2, 4)
                }
                
                # Build address string
                address_parts = [
                    location_data.get('address1', ''),
                    location_data.get('city', ''),
                    location_data.get('state', '')
                ]
                address = ', '.join([part for part in address_parts if part])
                
                activities.append({
                    "activity_id": business.get('id', f"YLP{random.randint(1000, 9999)}"),
                    "name": business.get('name', 'Unknown Activity'),
                    "type": activity_type,
                    "category": activity_category,
                    "description": f"{activity_type} in {location_data.get('city', 'the area')}. " + 
                                  (f"Review: {business.get('review_count', 0)} reviews" if business.get('review_count') else ''),
                    "location": {
                        "address": address,
                        "coordinates": {
                            "lat": coordinates.get('latitude', 0),
                            "lng": coordinates.get('longitude', 0)
                        }
                    },
                    "rating": rating,
                    "review_count": business.get('review_count', 0),
                    "price_level": price_level,
                    "duration_hours": duration_map.get(activity_category, 2),
                    "best_time": random.choice(['Morning', 'Afternoon', 'Evening', 'Full Day']),
                    "tags": category_names[:3],
                    "phone": business.get('phone', ''),
                    "website": business.get('url', ''),
                    "photos": [business.get('image_url')] if business.get('image_url') else [],
                    "is_closed": business.get('is_closed', False)
                })
            except Exception as e:
                logger.warning(f"Error parsing Yelp business data: {e}")
                continue
        
        return activities if activities else []
    
    async def _fetch_opentripmap_activities(
        self,
        destination: str,
        preferences: List[str],
        limit: int
    ):
        """Fetch activities from OpenTripMap API (NO API KEY NEEDED!)."""
        try:
            async with aiohttp.ClientSession() as session:
                # Step 1: Geocode the destination
                geocode_url = "https://api.opentripmap.com/0.1/en/places/geoname"
                params = {'name': destination}
                
                async with session.get(geocode_url, params=params, timeout=self.api_config.get('activities', {}).get('timeout', 15)) as response:
                    if response.status != 200:
                        logger.warning(f"OpenTripMap geocoding error {response.status}, using mock data")
                        return self._generate_mock_activities(destination, preferences, limit)
                    
                    geo_data = await response.json()
                    if not geo_data or 'lat' not in geo_data:
                        logger.warning("OpenTripMap: Could not geocode destination, using mock data")
                        return self._generate_mock_activities(destination, preferences, limit)
                    
                    lat = geo_data['lat']
                    lon = geo_data['lon']
                
                # Step 2: Search for places of interest
                # Map preferences to OpenTripMap kinds
                kinds_mapping = {
                    'adventure': 'natural,sport,natural',
                    'cultural': 'cultural,historic,museums,theatres',
                    'culinary': 'foods',
                    'nature': 'natural,beaches,nature_reserves',
                    'relaxation': 'natural,beaches',
                    'family_friendly': 'amusements,cultural'
                }
                
                # Build kinds parameter based on preferences
                kinds = []
                if preferences:
                    for pref in preferences:
                        if pref.lower() in kinds_mapping:
                            kinds.extend(kinds_mapping[pref.lower()].split(','))
                
                if not kinds:
                    kinds = ['interesting_places', 'cultural', 'natural', 'amusements']
                
                # Remove duplicates
                kinds = ','.join(list(set(kinds)))
                
                radius = self.api_config.get('activities', {}).get('opentripmap', {}).get('radius', 10000)
                
                places_url = "https://api.opentripmap.com/0.1/en/places/radius"
                places_params = {
                    'radius': radius,
                    'lon': lon,
                    'lat': lat,
                    'kinds': kinds,
                    'limit': min(limit * 2, 50)  # Get more to filter
                }
                
                async with session.get(places_url, params=places_params, timeout=self.api_config.get('activities', {}).get('timeout', 15)) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Get detailed info for each place
                        activities = []
                        for place in data[:limit]:
                            xid = place.get('xid')
                            if xid:
                                # Get place details
                                detail_url = f"https://api.opentripmap.com/0.1/en/places/xid/{xid}"
                                async with session.get(detail_url, timeout=10) as detail_response:
                                    if detail_response.status == 200:
                                        detail = await detail_response.json()
                                        activity = self._parse_opentripmap_place(detail, preferences)
                                        if activity:
                                            activities.append(activity)
                                
                                if len(activities) >= limit:
                                    break
                        
                        if activities:
                            logger.info(f"✅ Fetched {len(activities)} real activities from OpenTripMap (FREE!)")
                            return activities
                        else:
                            logger.warning("No activities found in OpenTripMap response, using mock data")
                            return self._generate_mock_activities(destination, preferences, limit)
                    else:
                        logger.warning(f"OpenTripMap API error {response.status}, using mock data")
                        return self._generate_mock_activities(destination, preferences, limit)
        
        except Exception as e:
            logger.error(f"Error fetching activities from OpenTripMap: {e}")
            return self._generate_mock_activities(destination, preferences, limit)
    
    def _parse_opentripmap_place(self, place: Dict, preferences: List[str]) -> Dict:
        """Parse OpenTripMap place data into our format."""
        try:
            name = place.get('name', 'Unknown Place')
            if not name or name == '':
                return None
            
            # Determine category based on kinds
            kinds = place.get('kinds', '').lower()
            category = 'cultural'
            activity_type = 'Attraction'
            
            if 'natural' in kinds or 'beach' in kinds or 'nature' in kinds:
                category = 'nature'
                activity_type = 'Nature'
            elif 'museum' in kinds or 'cultural' in kinds or 'historic' in kinds:
                category = 'cultural'
                activity_type = 'Cultural'
            elif 'sport' in kinds or 'climbing' in kinds:
                category = 'adventure'
                activity_type = 'Adventure'
            elif 'food' in kinds or 'restaurant' in kinds:
                category = 'culinary'
                activity_type = 'Culinary'
            
            # Extract location
            point = place.get('point', {})
            address = place.get('address', {})
            
            # Get rating (OpenTripMap uses "rate" 1-7 scale)
            rate = place.get('rate', 0)
            rating = round(min(rate / 7 * 5, 5.0), 1) if rate else 4.0
            
            # Estimate duration based on category
            duration_map = {
                'nature': random.randint(2, 4),
                'cultural': random.randint(1, 3),
                'adventure': random.randint(2, 5),
                'culinary': random.randint(1, 2)
            }
            
            return {
                "activity_id": place.get('xid', f"OTM{random.randint(1000, 9999)}"),
                "name": name,
                "type": activity_type,
                "category": category,
                "description": place.get('info', {}).get('descr', f"Popular {activity_type.lower()} in the area"),
                "location": {
                    "address": address.get('road', '') + ', ' + address.get('city', ''),
                    "coordinates": {
                        "lat": point.get('lat', 0),
                        "lng": point.get('lon', 0)
                    }
                },
                "rating": rating,
                "price_level": random.randint(1, 3),
                "duration_hours": duration_map.get(category, 2),
                "best_time": random.choice(['Morning', 'Afternoon', 'Evening', 'Full Day']),
                "tags": kinds.split(',')[:3] if kinds else [],
                "website": place.get('url', place.get('wikipedia', '')),
                "photos": [place.get('preview', {}).get('source', '')] if place.get('preview') else []
            }
        
        except Exception as e:
            logger.warning(f"Error parsing OpenTripMap place: {e}")
            return None
    
    async def _fetch_foursquare_activities(
        self,
        destination: str,
        preferences: List[str],
        limit: int
    ):
        """Fetch activities from Foursquare API (if key is provided)."""
        if not self.foursquare_key:
            logger.warning("Foursquare API key not found, using mock data")
            return self._generate_mock_activities(destination, preferences, limit)
        
        try:
            async with aiohttp.ClientSession() as session:
                # NEW Foursquare Places API v3 (2025-06-17 version)
                url = "https://places-api.foursquare.com/places/search"
                headers = {
                    "Authorization": self.foursquare_key,
                    "X-Places-Api-Version": "2025-06-17",  # Required version header
                    "Accept": "application/json"
                }
                
                # Map preferences to Foursquare categories
                category_mapping = {
                    'adventure': '16000',      # Outdoors & Recreation
                    'cultural': '10000',       # Arts & Entertainment
                    'culinary': '13000',       # Food & Drink
                    'nature': '16000',         # Outdoors & Recreation
                    'relaxation': '17000',     # Health & Beauty
                    'family_friendly': '12000' # Community & Government
                }
                
                # Build category filter
                categories = []
                if preferences:
                    for pref in preferences:
                        if pref.lower() in category_mapping:
                            categories.append(category_mapping[pref.lower()])
                
                params = {
                    'near': destination,
                    'limit': min(limit, 50),  # Max 50 per request
                    'sort': 'POPULARITY'
                }
                
                # Add category filter if preferences specified
                if categories:
                    params['fsq_category_ids'] = ','.join(categories)
                
                async with session.get(url, headers=headers, params=params, timeout=self.api_config.get('activities', {}).get('timeout', 15)) as response:
                    if response.status == 200:
                        data = await response.json()
                        activities = self._parse_foursquare_v3_response(data, preferences)
                        
                        if activities:
                            logger.info(f"✅ Fetched {len(activities)} real activities from Foursquare Places API v3")
                            return activities
                        else:
                            logger.warning("No activities found in API response, using mock data")
                            return self._generate_mock_activities(destination, preferences, limit)
                    elif response.status == 401:
                        error_text = await response.text()
                        logger.warning(f"Foursquare API 401 Unauthorized: {error_text[:200]}")
                        logger.warning("Make sure you're using a Service API Key (not Legacy API Key)")
                        return self._generate_mock_activities(destination, preferences, limit)
                    else:
                        error_text = await response.text()
                        logger.warning(f"Foursquare API error {response.status}: {error_text[:200]}, using mock data")
                        return self._generate_mock_activities(destination, preferences, limit)
        
        except Exception as e:
            logger.error(f"Error fetching activities from Foursquare: {e}")
            return self._generate_mock_activities(destination, preferences, limit)
    
    def _parse_foursquare_v3_response(self, data: Dict, preferences: List[str]) -> List[Dict]:
        """Parse Foursquare Places API v3 (2025-06-17) response into our format."""
        activities = []
        
        if 'results' not in data:
            return []
        
        for place in data['results']:
            try:
                # Extract categories
                categories = place.get('categories', [])
                category_names = [cat.get('name', '') for cat in categories]
                
                # Determine activity type from categories
                activity_type = category_names[0] if category_names else 'Attraction'
                
                # Map to our preference categories
                activity_category = 'cultural'
                category_str = ' '.join(category_names).lower()
                if any(word in category_str for word in ['park', 'outdoor', 'nature', 'beach', 'hiking']):
                    activity_category = 'nature'
                elif any(word in category_str for word in ['restaurant', 'food', 'dining', 'cafe', 'bar']):
                    activity_category = 'culinary'
                elif any(word in category_str for word in ['museum', 'art', 'historic', 'cultural', 'theater']):
                    activity_category = 'cultural'
                elif any(word in category_str for word in ['spa', 'wellness', 'relaxation', 'massage']):
                    activity_category = 'relaxation'
                elif any(word in category_str for word in ['adventure', 'sports', 'recreation']):
                    activity_category = 'adventure'
                
                # Extract location
                location_data = place.get('location', {})
                
                # Extract rating (0-10 scale, convert to 5-scale)
                rating = place.get('rating', 0)
                if rating > 0:
                    rating = round(rating / 2, 1)  # Convert 10-scale to 5-scale
                else:
                    rating = round(random.uniform(4.0, 5.0), 1)
                
                # Extract price level
                price_level = place.get('price', random.randint(1, 4))
                
                activities.append({
                    "activity_id": place.get('fsq_place_id', f"ACT{random.randint(1000, 9999)}"),
                    "name": place.get('name', 'Unknown Activity'),
                    "type": activity_type,
                    "category": activity_category,
                    "description": place.get('description', f"Popular {activity_type.lower()} in the area"),
                    "location": {
                        "address": location_data.get('formatted_address', location_data.get('address', 'N/A')),
                        "coordinates": {
                            "lat": place.get('geocodes', {}).get('main', {}).get('latitude', 0),
                            "lng": place.get('geocodes', {}).get('main', {}).get('longitude', 0)
                        }
                    },
                    "rating": rating,
                    "price_level": price_level,
                    "duration_hours": random.randint(1, 4),
                    "best_time": random.choice(['Morning', 'Afternoon', 'Evening', 'Full Day']),
                    "tags": category_names[:3],
                    "website": place.get('website', ''),
                    "photos": [photo.get('prefix', '') + 'original' + photo.get('suffix', '') 
                              for photo in place.get('photos', [])[:3]] if place.get('photos') else []
                })
            except Exception as e:
                logger.warning(f"Error parsing activity data: {e}")
                continue
        
        return activities if activities else []
    
    def _generate_mock_activities(
        self,
        destination: str,
        preferences: List[str],
        limit: int
    ) -> List[Dict]:
        """Generate mock activities data."""
        activity_templates = {
            'adventure': [
                'Zip Lining Adventure', 'Rock Climbing', 'White Water Rafting',
                'Hiking Trail', 'Mountain Biking', 'Paragliding Experience'
            ],
            'cultural': [
                'Historical Museum Visit', 'Art Gallery Tour', 'Cultural Walking Tour',
                'Traditional Dance Performance', 'Heritage Site Visit', 'Local Market Tour'
            ],
            'culinary': [
                'Cooking Class', 'Food Tour', 'Wine Tasting', 'Local Restaurant',
                'Street Food Adventure', 'Farm to Table Experience'
            ],
            'nature': [
                'National Park Visit', 'Botanical Garden', 'Beach Day',
                'Wildlife Safari', 'Scenic Viewpoint', 'Nature Walk'
            ],
            'relaxation': [
                'Spa Day', 'Yoga Session', 'Meditation Retreat',
                'Hot Springs Visit', 'Wellness Center', 'Beach Relaxation'
            ]
        }
        
        activities = []
        activity_pool = []
        
        # Prioritize activities based on preferences
        if preferences:
            for pref in preferences:
                if pref.lower() in activity_templates:
                    activity_pool.extend(activity_templates[pref.lower()])
        
        # Add some random activities
        for category_activities in activity_templates.values():
            activity_pool.extend(category_activities)
        
        # Remove duplicates and limit
        activity_pool = list(set(activity_pool))
        random.shuffle(activity_pool)
        
        for i, activity_name in enumerate(activity_pool[:limit]):
            category = next((cat for cat, acts in activity_templates.items() if activity_name in acts), 'cultural')
            
            activities.append({
                "activity_id": f"ACT{random.randint(1000, 9999)}",
                "name": f"{activity_name} in {destination}",
                "type": category.title(),
                "category": category,
                "description": f"Experience the best {activity_name.lower()} that {destination} has to offer.",
                "location": {
                    "address": f"{destination} City Center",
                    "coordinates": {
                        "lat": round(random.uniform(-90, 90), 6),
                        "lng": round(random.uniform(-180, 180), 6)
                    }
                },
                "rating": round(random.uniform(4.0, 5.0), 1),
                "price_level": random.randint(1, 4),
                "duration_hours": random.randint(1, 6),
                "best_time": random.choice(['Morning', 'Afternoon', 'Evening', 'Full Day']),
                "tags": [category, destination, random.choice(['Popular', 'Recommended', 'Hidden Gem'])],
                "website": f"https://example.com/activity/{i}",
                "photos": []
            })
        
        return activities
