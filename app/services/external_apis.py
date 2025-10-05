"""
External API Services for Real-time Data Integration

This module handles all external API calls for flights, hotels, weather, etc.
All APIs used are free or have generous free tiers.
"""

import aiohttp
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json

from app.core.config import get_settings
from app.core.logging_config import get_logger

settings = get_settings()
logger = get_logger(__name__)


class ExternalAPIService:
    """Service for managing external API integrations"""
    
    def __init__(self):
        self.settings = settings
        self.logger = logger
        self.session = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()


class WeatherService(ExternalAPIService):
    """OpenWeatherMap API service (1000 calls/day free)"""
    
    BASE_URL = "https://api.openweathermap.org/data/2.5"
    
    async def get_weather_forecast(self, destination: str, days: int = 7) -> Dict[str, Any]:
        """Get weather forecast for destination"""
        if not self.settings.OPENWEATHER_API_KEY:
            self.logger.warning("OpenWeatherMap API key not configured")
            return self._get_mock_weather_data(destination, days)
        
        try:
            # First get coordinates for the destination
            geo_url = f"http://api.openweathermap.org/geo/1.0/direct"
            geo_params = {
                "q": destination,
                "limit": 1,
                "appid": self.settings.OPENWEATHER_API_KEY
            }
            
            async with self.session.get(geo_url, params=geo_params) as response:
                if response.status == 200:
                    geo_data = await response.json()
                    if not geo_data:
                        return self._get_mock_weather_data(destination, days)
                    
                    lat, lon = geo_data[0]["lat"], geo_data[0]["lon"]
                else:
                    return self._get_mock_weather_data(destination, days)
            
            # Get forecast data
            forecast_url = f"{self.BASE_URL}/forecast"
            forecast_params = {
                "lat": lat,
                "lon": lon,
                "appid": self.settings.OPENWEATHER_API_KEY,
                "units": "metric"
            }
            
            async with self.session.get(forecast_url, params=forecast_params) as response:
                if response.status == 200:
                    forecast_data = await response.json()
                    return self._process_weather_data(forecast_data, destination, days)
                else:
                    return self._get_mock_weather_data(destination, days)
                    
        except Exception as e:
            self.logger.error("Error fetching weather data", error=str(e))
            return self._get_mock_weather_data(destination, days)
    
    def _process_weather_data(self, raw_data: Dict, destination: str, days: int) -> Dict[str, Any]:
        """Process raw weather API response"""
        processed = {
            "destination": destination,
            "forecast_days": days,
            "daily_forecast": [],
            "average_temp": 0,
            "weather_summary": "",
            "recommendations": []
        }
        
        # Process forecast data (OpenWeatherMap gives 5-day forecast with 3-hour intervals)
        daily_data = {}
        
        for item in raw_data.get("list", [])[:days * 8]:  # 8 intervals per day
            date = datetime.fromtimestamp(item["dt"]).date()
            
            if date not in daily_data:
                daily_data[date] = {
                    "date": date.isoformat(),
                    "temps": [],
                    "conditions": [],
                    "humidity": [],
                    "precipitation": 0
                }
            
            daily_data[date]["temps"].append(item["main"]["temp"])
            daily_data[date]["conditions"].append(item["weather"][0]["main"])
            daily_data[date]["humidity"].append(item["main"]["humidity"])
            
            if "rain" in item:
                daily_data[date]["precipitation"] += item["rain"].get("3h", 0)
        
        # Calculate daily summaries
        total_temp = 0
        for date, data in daily_data.items():
            daily_summary = {
                "date": data["date"],
                "min_temp": min(data["temps"]),
                "max_temp": max(data["temps"]),
                "avg_temp": sum(data["temps"]) / len(data["temps"]),
                "condition": max(set(data["conditions"]), key=data["conditions"].count),
                "humidity": sum(data["humidity"]) / len(data["humidity"]),
                "precipitation_mm": data["precipitation"]
            }
            
            processed["daily_forecast"].append(daily_summary)
            total_temp += daily_summary["avg_temp"]
        
        processed["average_temp"] = total_temp / len(daily_data) if daily_data else 20
        
        # Generate recommendations
        if processed["average_temp"] < 10:
            processed["recommendations"].append("Pack warm clothing")
        elif processed["average_temp"] > 30:
            processed["recommendations"].append("Pack light, breathable clothing")
        
        if any(day["precipitation_mm"] > 5 for day in processed["daily_forecast"]):
            processed["recommendations"].append("Bring rain gear or umbrella")
        
        return processed
    
    def _get_mock_weather_data(self, destination: str, days: int) -> Dict[str, Any]:
        """Return mock weather data when API is unavailable"""
        return {
            "destination": destination,
            "forecast_days": days,
            "daily_forecast": [
                {
                    "date": (datetime.now() + timedelta(days=i)).date().isoformat(),
                    "min_temp": 18 + (i % 3),
                    "max_temp": 25 + (i % 3),
                    "avg_temp": 22 + (i % 3),
                    "condition": "Clear",
                    "humidity": 60,
                    "precipitation_mm": 0
                }
                for i in range(days)
            ],
            "average_temp": 22,
            "weather_summary": "Generally pleasant weather expected",
            "recommendations": ["Pack light layers"],
            "data_source": "mock"
        }


class FlightService(ExternalAPIService):
    """Aviationstack API service (1000 requests/month free)"""
    
    BASE_URL = "http://api.aviationstack.com/v1"
    
    async def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        return_date: Optional[str] = None,
        passengers: int = 1
    ) -> Dict[str, Any]:
        """Search for flights"""
        if not self.settings.AVIATIONSTACK_API_KEY:
            self.logger.warning("Aviationstack API key not configured")
            return self._get_mock_flight_data(origin, destination, departure_date, return_date)
        
        try:
            # Note: Aviationstack free tier provides real-time flight info but limited search
            # For production, you might need a different API or upgrade
            url = f"{self.BASE_URL}/flights"
            params = {
                "access_key": self.settings.AVIATIONSTACK_API_KEY,
                "dep_iata": origin,
                "arr_iata": destination,
                "limit": 10
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._process_flight_data(data, origin, destination, departure_date, return_date)
                else:
                    return self._get_mock_flight_data(origin, destination, departure_date, return_date)
                    
        except Exception as e:
            self.logger.error("Error fetching flight data", error=str(e))
            return self._get_mock_flight_data(origin, destination, departure_date, return_date)
    
    def _process_flight_data(self, raw_data: Dict, origin: str, destination: str, 
                           departure_date: str, return_date: Optional[str]) -> Dict[str, Any]:
        """Process flight API response"""
        flights = []
        
        for flight in raw_data.get("data", []):
            processed_flight = {
                "flight_number": flight.get("flight", {}).get("number"),
                "airline": flight.get("airline", {}).get("name"),
                "origin": origin,
                "destination": destination,
                "departure_time": flight.get("departure", {}).get("scheduled"),
                "arrival_time": flight.get("arrival", {}).get("scheduled"),
                "aircraft": flight.get("aircraft", {}).get("registration"),
                "status": flight.get("flight_status"),
                "estimated_price": 450 + (len(flights) * 50),  # Mock pricing
                "booking_class": "Economy"
            }
            flights.append(processed_flight)
        
        return {
            "origin": origin,
            "destination": destination,
            "departure_date": departure_date,
            "return_date": return_date,
            "flights": flights,
            "search_timestamp": datetime.utcnow().isoformat(),
            "data_source": "aviationstack"
        }
    
    def _get_mock_flight_data(self, origin: str, destination: str, 
                            departure_date: str, return_date: Optional[str]) -> Dict[str, Any]:
        """Return mock flight data"""
        mock_flights = [
            {
                "flight_number": "AA101",
                "airline": "American Airlines",
                "origin": origin,
                "destination": destination,
                "departure_time": f"{departure_date}T08:00:00Z",
                "arrival_time": f"{departure_date}T14:30:00Z",
                "duration": "6h 30m",
                "estimated_price": 450,
                "booking_class": "Economy",
                "stops": 0
            },
            {
                "flight_number": "UA205",
                "airline": "United Airlines",
                "origin": origin,
                "destination": destination,
                "departure_time": f"{departure_date}T10:15:00Z",
                "arrival_time": f"{departure_date}T16:45:00Z",
                "duration": "6h 30m",
                "estimated_price": 520,
                "booking_class": "Economy",
                "stops": 0
            },
            {
                "flight_number": "DL309",
                "airline": "Delta Airlines",
                "origin": origin,
                "destination": destination,
                "departure_time": f"{departure_date}T15:20:00Z",
                "arrival_time": f"{departure_date}T21:50:00Z",
                "duration": "6h 30m",
                "estimated_price": 480,
                "booking_class": "Economy",
                "stops": 0
            }
        ]
        
        return {
            "origin": origin,
            "destination": destination,
            "departure_date": departure_date,
            "return_date": return_date,
            "flights": mock_flights,
            "search_timestamp": datetime.utcnow().isoformat(),
            "data_source": "mock"
        }


class HotelService(ExternalAPIService):
    """Hotel search service using free APIs"""
    
    async def search_hotels(
        self,
        destination: str,
        check_in: str,
        check_out: str,
        guests: int = 2,
        budget_range: str = "mid-range"
    ) -> Dict[str, Any]:
        """Search for hotels (mock implementation - replace with actual API)"""
        # TODO: Integrate with free hotel APIs like Booking.com's partner API
        # For now, return mock data
        
        return self._get_mock_hotel_data(destination, check_in, check_out, guests, budget_range)
    
    def _get_mock_hotel_data(self, destination: str, check_in: str, check_out: str, 
                           guests: int, budget_range: str) -> Dict[str, Any]:
        """Return mock hotel data"""
        
        price_ranges = {
            "budget": (50, 120),
            "mid-range": (120, 300),
            "luxury": (300, 800)
        }
        
        min_price, max_price = price_ranges.get(budget_range, (120, 300))
        
        mock_hotels = [
            {
                "name": f"Grand Hotel {destination}",
                "rating": 4.5,
                "price_per_night": min_price + 50,
                "total_price": (min_price + 50) * 3,  # Assuming 3 nights
                "amenities": ["WiFi", "Pool", "Gym", "Restaurant", "Spa"],
                "location": f"City Center, {destination}",
                "distance_to_center": "0.5 km",
                "guest_rating": 4.3,
                "images": [],
                "cancellation_policy": "Free cancellation until 24h before"
            },
            {
                "name": f"Boutique Inn {destination}",
                "rating": 4.2,
                "price_per_night": min_price + 20,
                "total_price": (min_price + 20) * 3,
                "amenities": ["WiFi", "Restaurant", "24h Reception"],
                "location": f"Historic District, {destination}",
                "distance_to_center": "1.2 km",
                "guest_rating": 4.1,
                "images": [],
                "cancellation_policy": "Free cancellation until 48h before"
            },
            {
                "name": f"Modern Suites {destination}",
                "rating": 4.0,
                "price_per_night": min_price + 80,
                "total_price": (min_price + 80) * 3,
                "amenities": ["WiFi", "Kitchen", "Laundry", "Parking"],
                "location": f"Business District, {destination}",
                "distance_to_center": "2.0 km",
                "guest_rating": 4.0,
                "images": [],
                "cancellation_policy": "Non-refundable"
            }
        ]
        
        return {
            "destination": destination,
            "check_in": check_in,
            "check_out": check_out,
            "guests": guests,
            "budget_range": budget_range,
            "hotels": mock_hotels,
            "search_timestamp": datetime.utcnow().isoformat(),
            "data_source": "mock"
        }


class CurrencyService(ExternalAPIService):
    """Fixer.io API service (100 requests/month free)"""
    
    BASE_URL = "http://data.fixer.io/api"
    
    async def get_exchange_rates(self, base_currency: str = "USD", target_currencies: List[str] = None) -> Dict[str, Any]:
        """Get current exchange rates"""
        if not self.settings.FIXER_API_KEY:
            self.logger.warning("Fixer API key not configured")
            return self._get_mock_currency_data(base_currency, target_currencies)
        
        try:
            url = f"{self.BASE_URL}/latest"
            params = {
                "access_key": self.settings.FIXER_API_KEY,
                "base": base_currency
            }
            
            if target_currencies:
                params["symbols"] = ",".join(target_currencies)
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._process_currency_data(data, base_currency)
                else:
                    return self._get_mock_currency_data(base_currency, target_currencies)
                    
        except Exception as e:
            self.logger.error("Error fetching currency data", error=str(e))
            return self._get_mock_currency_data(base_currency, target_currencies)
    
    def _process_currency_data(self, raw_data: Dict, base_currency: str) -> Dict[str, Any]:
        """Process currency API response"""
        return {
            "base_currency": base_currency,
            "rates": raw_data.get("rates", {}),
            "timestamp": raw_data.get("timestamp"),
            "data_source": "fixer.io"
        }
    
    def _get_mock_currency_data(self, base_currency: str, target_currencies: List[str]) -> Dict[str, Any]:
        """Return mock currency data"""
        mock_rates = {
            "EUR": 0.85,
            "GBP": 0.73,
            "JPY": 110.0,
            "CAD": 1.25,
            "AUD": 1.35,
            "CHF": 0.92,
            "CNY": 6.45,
            "INR": 74.5
        }
        
        if target_currencies:
            filtered_rates = {k: v for k, v in mock_rates.items() if k in target_currencies}
        else:
            filtered_rates = mock_rates
        
        return {
            "base_currency": base_currency,
            "rates": filtered_rates,
            "timestamp": datetime.utcnow().timestamp(),
            "data_source": "mock"
        }