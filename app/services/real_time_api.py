"""
Real-time API Service

Service for fetching real-time data from external APIs:
- Weather data from OpenWeatherMap
- Flight data from Aviationstack
- Currency exchange from Fixer.io
- Hotel/POI data from OpenStreetMap
"""

import asyncio
import aiohttp
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json

from app.core.config import get_settings
from app.core.logging_config import get_logger

settings = get_settings()
logger = get_logger(__name__)


class RealTimeAPIService:
    """Service for fetching real-time travel data"""
    
    def __init__(self):
        self.settings = settings
        self.logger = logger
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def get_weather_data(self, destination: str, dates: List[str]) -> Dict[str, Any]:
        """Fetch weather data from OpenWeatherMap API"""
        if not self.settings.OPENWEATHER_API_KEY:
            self.logger.warning("OpenWeatherMap API key not configured")
            return self._mock_weather_data(destination, dates)
        
        try:
            # First, get coordinates for the destination
            geocoding_url = "http://api.openweathermap.org/geo/1.0/direct"
            geocoding_params = {
                "q": destination,
                "limit": 1,
                "appid": self.settings.OPENWEATHER_API_KEY
            }
            
            async with self.session.get(geocoding_url, params=geocoding_params) as response:
                if response.status != 200:
                    raise Exception(f"Geocoding API error: {response.status}")
                
                geocoding_data = await response.json()
                if not geocoding_data:
                    raise Exception("Destination not found")
                
                lat = geocoding_data[0]["lat"]
                lon = geocoding_data[0]["lon"]
            
            # Get current weather
            current_weather_url = "https://api.openweathermap.org/data/2.5/weather"
            current_params = {
                "lat": lat,
                "lon": lon,
                "appid": self.settings.OPENWEATHER_API_KEY,
                "units": "metric"
            }
            
            async with self.session.get(current_weather_url, params=current_params) as response:
                if response.status != 200:
                    raise Exception(f"Weather API error: {response.status}")
                
                current_weather = await response.json()
            
            # Get forecast data
            forecast_url = "https://api.openweathermap.org/data/2.5/forecast"
            forecast_params = {
                "lat": lat,
                "lon": lon,
                "appid": self.settings.OPENWEATHER_API_KEY,
                "units": "metric"
            }
            
            async with self.session.get(forecast_url, params=forecast_params) as response:
                if response.status != 200:
                    raise Exception(f"Forecast API error: {response.status}")
                
                forecast_data = await response.json()
            
            weather_result = {
                "destination": destination,
                "coordinates": {"lat": lat, "lon": lon},
                "current_weather": {
                    "temperature": current_weather["main"]["temp"],
                    "description": current_weather["weather"][0]["description"],
                    "humidity": current_weather["main"]["humidity"],
                    "wind_speed": current_weather["wind"]["speed"],
                    "timestamp": datetime.utcnow().isoformat()
                },
                "forecast": self._process_forecast(forecast_data, dates),
                "source": "OpenWeatherMap",
                "status": "success"
            }
            
            self.logger.info(f"Weather data fetched successfully for {destination}")
            return weather_result
            
        except Exception as e:
            self.logger.error(f"Error fetching weather data: {e}")
            return self._mock_weather_data(destination, dates)
    
    async def get_flight_data(self, origin: str, destination: str, date: str) -> Dict[str, Any]:
        """Fetch flight data from Aviationstack API"""
        if not self.settings.AVIATIONSTACK_API_KEY:
            self.logger.warning("Aviationstack API key not configured")
            return self._mock_flight_data(origin, destination, date)
        
        try:
            # Note: Aviationstack free tier has limitations, this is a basic implementation
            flights_url = "http://api.aviationstack.com/v1/flights"
            params = {
                "access_key": self.settings.AVIATIONSTACK_API_KEY,
                "limit": 10,
                "flight_status": "scheduled"
            }
            
            async with self.session.get(flights_url, params=params) as response:
                if response.status != 200:
                    raise Exception(f"Aviationstack API error: {response.status}")
                
                flight_data = await response.json()
            
            # Process and filter flight data
            processed_flights = []
            for flight in flight_data.get("data", [])[:5]:  # Limit to 5 results
                processed_flights.append({
                    "airline": flight.get("airline", {}).get("name", "Unknown"),
                    "flight_number": flight.get("flight", {}).get("number", "N/A"),
                    "departure": {
                        "airport": flight.get("departure", {}).get("airport", "N/A"),
                        "scheduled": flight.get("departure", {}).get("scheduled", "N/A"),
                        "timezone": flight.get("departure", {}).get("timezone", "N/A")
                    },
                    "arrival": {
                        "airport": flight.get("arrival", {}).get("airport", "N/A"),
                        "scheduled": flight.get("arrival", {}).get("scheduled", "N/A"),
                        "timezone": flight.get("arrival", {}).get("timezone", "N/A")
                    },
                    "status": flight.get("flight_status", "unknown")
                })
            
            flight_result = {
                "origin": origin,
                "destination": destination,
                "date": date,
                "flights": processed_flights,
                "source": "Aviationstack",
                "status": "success"
            }
            
            self.logger.info(f"Flight data fetched for {origin} to {destination}")
            return flight_result
            
        except Exception as e:
            self.logger.error(f"Error fetching flight data: {e}")
            return self._mock_flight_data(origin, destination, date)
    
    async def get_currency_rates(self, base_currency: str = "USD", target_currencies: List[str] = None) -> Dict[str, Any]:
        """Fetch currency exchange rates from Fixer.io API"""
        if not self.settings.FIXER_API_KEY:
            self.logger.warning("Fixer.io API key not configured")
            return self._mock_currency_data(base_currency, target_currencies)
        
        if target_currencies is None:
            target_currencies = ["EUR", "GBP", "JPY", "CAD", "AUD"]
        
        try:
            fixer_url = "http://data.fixer.io/api/latest"
            params = {
                "access_key": self.settings.FIXER_API_KEY,
                "base": base_currency,
                "symbols": ",".join(target_currencies)
            }
            
            async with self.session.get(fixer_url, params=params) as response:
                if response.status != 200:
                    raise Exception(f"Fixer.io API error: {response.status}")
                
                currency_data = await response.json()
            
            if not currency_data.get("success"):
                raise Exception(f"Fixer.io API error: {currency_data.get('error', {})}")
            
            currency_result = {
                "base_currency": base_currency,
                "rates": currency_data.get("rates", {}),
                "timestamp": currency_data.get("timestamp"),
                "date": currency_data.get("date"),
                "source": "Fixer.io",
                "status": "success"
            }
            
            self.logger.info(f"Currency rates fetched for {base_currency}")
            return currency_result
            
        except Exception as e:
            self.logger.error(f"Error fetching currency data: {e}")
            return self._mock_currency_data(base_currency, target_currencies)
    
    async def get_hotel_data(self, destination: str, checkin: str, checkout: str) -> Dict[str, Any]:
        """Fetch hotel/accommodation data using OpenStreetMap"""
        try:
            # Use Nominatim for geocoding (free, no API key required)
            nominatim_url = "https://nominatim.openstreetmap.org/search"
            geocoding_params = {
                "q": destination,
                "format": "json",
                "limit": 1
            }
            
            headers = {"User-Agent": "AI-Travel-Planner/1.0"}
            
            async with self.session.get(nominatim_url, params=geocoding_params, headers=headers) as response:
                if response.status != 200:
                    raise Exception(f"Nominatim API error: {response.status}")
                
                geocoding_data = await response.json()
                if not geocoding_data:
                    raise Exception("Destination not found")
                
                lat = float(geocoding_data[0]["lat"])
                lon = float(geocoding_data[0]["lon"])
            
            # Use Overpass API to find hotels (free, no API key required)
            overpass_url = "https://overpass-api.de/api/interpreter"
            
            # Query for hotels within 5km radius
            overpass_query = f"""
            [out:json][timeout:25];
            (
              node["tourism"="hotel"](around:5000,{lat},{lon});
              way["tourism"="hotel"](around:5000,{lat},{lon});
              relation["tourism"="hotel"](around:5000,{lat},{lon});
            );
            out geom;
            """
            
            async with self.session.post(overpass_url, data=overpass_query, headers=headers) as response:
                if response.status != 200:
                    raise Exception(f"Overpass API error: {response.status}")
                
                hotel_data = await response.json()
            
            # Process hotel data
            hotels = []
            for element in hotel_data.get("elements", [])[:10]:  # Limit to 10 results
                tags = element.get("tags", {})
                hotels.append({
                    "name": tags.get("name", "Unknown Hotel"),
                    "address": tags.get("addr:street", "Address not available"),
                    "website": tags.get("website", ""),
                    "phone": tags.get("phone", ""),
                    "stars": tags.get("stars", "N/A"),
                    "coordinates": {
                        "lat": element.get("lat", element.get("center", {}).get("lat")),
                        "lon": element.get("lon", element.get("center", {}).get("lon"))
                    }
                })
            
            hotel_result = {
                "destination": destination,
                "checkin_date": checkin,
                "checkout_date": checkout,
                "hotels": hotels,
                "total_found": len(hotels),
                "source": "OpenStreetMap/Overpass",
                "status": "success"
            }
            
            self.logger.info(f"Hotel data fetched for {destination}: {len(hotels)} hotels found")
            return hotel_result
            
        except Exception as e:
            self.logger.error(f"Error fetching hotel data: {e}")
            return self._mock_hotel_data(destination, checkin, checkout)
    
    async def get_all_travel_data(self, destination: str, origin: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Fetch all travel data concurrently"""
        self.logger.info(f"Fetching all travel data for {destination}")
        
        # Create date list for weather forecast
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        date_list = [(start + timedelta(days=x)).strftime("%Y-%m-%d") 
                     for x in range((end - start).days + 1)]
        
        # Fetch all data concurrently
        weather_task = self.get_weather_data(destination, date_list)
        flight_task = self.get_flight_data(origin, destination, start_date)
        hotel_task = self.get_hotel_data(destination, start_date, end_date)
        currency_task = self.get_currency_rates()
        
        try:
            weather_data, flight_data, hotel_data, currency_data = await asyncio.gather(
                weather_task, flight_task, hotel_task, currency_task,
                return_exceptions=True
            )
            
            # Handle exceptions
            if isinstance(weather_data, Exception):
                weather_data = self._mock_weather_data(destination, date_list)
            if isinstance(flight_data, Exception):
                flight_data = self._mock_flight_data(origin, destination, start_date)
            if isinstance(hotel_data, Exception):
                hotel_data = self._mock_hotel_data(destination, start_date, end_date)
            if isinstance(currency_data, Exception):
                currency_data = self._mock_currency_data()
            
            combined_result = {
                "destination": destination,
                "origin": origin,
                "travel_dates": {"start": start_date, "end": end_date},
                "weather": weather_data,
                "flights": flight_data,
                "hotels": hotel_data,
                "currency": currency_data,
                "fetch_timestamp": datetime.utcnow().isoformat(),
                "status": "success"
            }
            
            self.logger.info("All travel data fetched successfully")
            return combined_result
            
        except Exception as e:
            self.logger.error(f"Error fetching travel data: {e}")
            return {
                "status": "error",
                "message": "Failed to fetch travel data",
                "error": str(e)
            }
    
    def _process_forecast(self, forecast_data: Dict[str, Any], target_dates: List[str]) -> List[Dict[str, Any]]:
        """Process forecast data for specific dates"""
        forecast_list = []
        for item in forecast_data.get("list", []):
            forecast_date = item["dt_txt"].split(" ")[0]
            if forecast_date in target_dates:
                forecast_list.append({
                    "date": forecast_date,
                    "time": item["dt_txt"],
                    "temperature": item["main"]["temp"],
                    "description": item["weather"][0]["description"],
                    "humidity": item["main"]["humidity"],
                    "wind_speed": item["wind"]["speed"]
                })
        return forecast_list
    
    def _mock_weather_data(self, destination: str, dates: List[str]) -> Dict[str, Any]:
        """Mock weather data when API is unavailable"""
        return {
            "destination": destination,
            "current_weather": {
                "temperature": 22.5,
                "description": "partly cloudy",
                "humidity": 65,
                "wind_speed": 3.2
            },
            "forecast": [
                {
                    "date": date,
                    "temperature": 20 + (i % 10),
                    "description": ["sunny", "cloudy", "partly cloudy"][i % 3]
                }
                for i, date in enumerate(dates)
            ],
            "source": "Mock Data",
            "status": "mock"
        }
    
    def _mock_flight_data(self, origin: str, destination: str, date: str) -> Dict[str, Any]:
        """Mock flight data when API is unavailable"""
        return {
            "origin": origin,
            "destination": destination,
            "date": date,
            "flights": [
                {
                    "airline": "Mock Airlines",
                    "flight_number": "MA001",
                    "departure": {"airport": origin, "scheduled": "08:00"},
                    "arrival": {"airport": destination, "scheduled": "12:00"},
                    "price": 299.99
                }
            ],
            "source": "Mock Data",
            "status": "mock"
        }
    
    def _mock_hotel_data(self, destination: str, checkin: str, checkout: str) -> Dict[str, Any]:
        """Mock hotel data when API is unavailable"""
        return {
            "destination": destination,
            "checkin_date": checkin,
            "checkout_date": checkout,
            "hotels": [
                {
                    "name": f"Grand Hotel {destination}",
                    "rating": 4.5,
                    "price_per_night": 150.0,
                    "address": f"Main Street, {destination}"
                }
            ],
            "source": "Mock Data",
            "status": "mock"
        }
    
    def _mock_currency_data(self, base_currency: str = "USD", target_currencies: List[str] = None) -> Dict[str, Any]:
        """Mock currency data when API is unavailable"""
        if target_currencies is None:
            target_currencies = ["EUR", "GBP", "JPY"]
        
        mock_rates = {"EUR": 0.85, "GBP": 0.73, "JPY": 110.0}
        
        return {
            "base_currency": base_currency,
            "rates": {curr: mock_rates.get(curr, 1.0) for curr in target_currencies},
            "source": "Mock Data",
            "status": "mock"
        }


# Convenience function for single-use API calls
async def fetch_travel_data(destination: str, origin: str = "New York", 
                          start_date: str = None, end_date: str = None) -> Dict[str, Any]:
    """Convenience function to fetch travel data"""
    if not start_date:
        start_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    if not end_date:
        end_date = (datetime.now() + timedelta(days=37)).strftime("%Y-%m-%d")
    
    async with RealTimeAPIService() as api_service:
        return await api_service.get_all_travel_data(destination, origin, start_date, end_date)