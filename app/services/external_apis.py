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
    """Hotel and accommodation search using OpenStreetMap and Overpass API (completely free)"""
    
    async def search_hotels(
        self,
        destination: str,
        check_in: str,
        check_out: str,
        guests: int = 2,
        budget_range: str = "mid-range"
    ) -> Dict[str, Any]:
        """Search for hotels using Overpass API (completely free)"""
        
        try:
            # First, get coordinates for the destination using Nominatim
            coordinates = await self._get_coordinates(destination)
            if not coordinates:
                return self._get_mock_hotel_data(destination, check_in, check_out, guests, budget_range)
            
            lat, lon = coordinates
            
            # Search for accommodations using Overpass API
            accommodations = await self._search_overpass_accommodations(lat, lon)
            
            # Process and return results
            return self._process_accommodation_data(accommodations, destination, check_in, check_out, guests, budget_range)
            
        except Exception as e:
            self.logger.error("Error fetching hotel data from free APIs", error=str(e))
            return self._get_mock_hotel_data(destination, check_in, check_out, guests, budget_range)
    
    async def _get_coordinates(self, destination: str) -> Optional[tuple]:
        """Get coordinates using Nominatim (free)"""
        try:
            url = "https://nominatim.openstreetmap.org/search"
            params = {
                "q": destination,
                "format": "json",
                "limit": 1,
                "addressdetails": 1
            }
            headers = {"User-Agent": "AI-Travel-Planner/1.0"}
            
            async with self.session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data:
                        return float(data[0]["lat"]), float(data[0]["lon"])
            
            return None
            
        except Exception as e:
            self.logger.error("Error getting coordinates", error=str(e))
            return None
    
    async def _search_overpass_accommodations(self, lat: float, lon: float, radius: int = 5000) -> List[Dict]:
        """Search for accommodations using Overpass API (free)"""
        try:
            # Overpass API query for hotels, hostels, and guesthouses
            overpass_query = f"""
            [out:json][timeout:25];
            (
              node["tourism"~"^(hotel|hostel|guest_house|motel|apartment)$"](around:{radius},{lat},{lon});
              way["tourism"~"^(hotel|hostel|guest_house|motel|apartment)$"](around:{radius},{lat},{lon});
              relation["tourism"~"^(hotel|hostel|guest_house|motel|apartment)$"](around:{radius},{lat},{lon});
            );
            out center meta;
            """
            
            url = "https://overpass-api.de/api/interpreter"
            headers = {"User-Agent": "AI-Travel-Planner/1.0"}
            
            async with self.session.post(url, data=overpass_query, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("elements", [])
            
            return []
            
        except Exception as e:
            self.logger.error("Error querying Overpass API", error=str(e))
            return []
    
    def _process_accommodation_data(
        self, 
        elements: List[Dict], 
        destination: str, 
        check_in: str, 
        check_out: str, 
        guests: int, 
        budget_range: str
    ) -> Dict[str, Any]:
        """Process Overpass API accommodation data"""
        
        accommodations = []
        price_ranges = {
            "budget": (30, 80),
            "mid-range": (80, 200),
            "luxury": (200, 500)
        }
        min_price, max_price = price_ranges.get(budget_range, (80, 200))
        
        for element in elements[:20]:  # Limit to first 20 results
            tags = element.get("tags", {})
            
            # Extract accommodation info
            name = tags.get("name", f"Accommodation {element.get('id', 'Unknown')}")
            tourism_type = tags.get("tourism", "hotel")
            
            # Estimate price based on type and location
            type_multipliers = {
                "hotel": 1.0,
                "hostel": 0.4,
                "guest_house": 0.6,
                "motel": 0.7,
                "apartment": 0.8
            }
            
            multiplier = type_multipliers.get(tourism_type, 1.0)
            estimated_price = int((min_price + max_price) / 2 * multiplier)
            
            # Get coordinates
            if element["type"] == "node":
                acc_lat, acc_lon = element["lat"], element["lon"]
            else:
                center = element.get("center", {})
                acc_lat, acc_lon = center.get("lat", 0), center.get("lon", 0)
            
            accommodation = {
                "name": name,
                "type": tourism_type,
                "price_per_night": estimated_price,
                "total_price": estimated_price * 3,  # Assuming 3 nights
                "rating": float(tags.get("stars", "0") or "4.0"),
                "amenities": self._extract_amenities(tags),
                "address": tags.get("addr:full") or tags.get("addr:street", "Address not available"),
                "phone": tags.get("phone", ""),
                "website": tags.get("website", ""),
                "coordinates": {"lat": acc_lat, "lon": acc_lon},
                "source": "OpenStreetMap",
                "osm_id": element.get("id")
            }
            
            accommodations.append(accommodation)
        
        return {
            "destination": destination,
            "check_in": check_in,
            "check_out": check_out,
            "guests": guests,
            "budget_range": budget_range,
            "accommodations": accommodations,
            "total_found": len(accommodations),
            "search_timestamp": datetime.utcnow().isoformat(),
            "data_source": "OpenStreetMap + Overpass API (free)"
        }
    
    def _extract_amenities(self, tags: Dict[str, str]) -> List[str]:
        """Extract amenities from OSM tags"""
        amenities = []
        
        # Check for common amenities in tags
        amenity_mapping = {
            "wifi": ["internet_access", "wifi"],
            "parking": ["parking"],
            "restaurant": ["restaurant"],
            "bar": ["bar"],
            "pool": ["swimming_pool"],
            "gym": ["fitness_centre", "gym"],
            "spa": ["spa"],
            "air_conditioning": ["air_conditioning"],
            "pets_allowed": ["pets"],
            "breakfast": ["breakfast"]
        }
        
        for amenity, tag_keys in amenity_mapping.items():
            for tag_key in tag_keys:
                if tags.get(tag_key) in ["yes", "true", "1"] or tag_key in tags:
                    amenities.append(amenity)
                    break
        
        return amenities
    
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


class POIService(ExternalAPIService):
    """Points of Interest service using OpenStreetMap and Overpass API (completely free)"""
    
    async def search_attractions(
        self,
        destination: str,
        categories: List[str] = None,
        radius: int = 10000
    ) -> Dict[str, Any]:
        """Search for attractions and activities using Overpass API"""
        
        if categories is None:
            categories = ["tourism", "amenity", "leisure", "historic"]
        
        try:
            # Get destination coordinates
            coordinates = await self._get_coordinates(destination)
            if not coordinates:
                return self._get_mock_poi_data(destination, categories)
            
            lat, lon = coordinates
            
            # Search for POIs using Overpass API
            pois = await self._search_overpass_pois(lat, lon, categories, radius)
            
            # Process and return results
            return self._process_poi_data(pois, destination, categories)
            
        except Exception as e:
            self.logger.error("Error fetching POI data from free APIs", error=str(e))
            return self._get_mock_poi_data(destination, categories)
    
    async def _get_coordinates(self, destination: str) -> Optional[tuple]:
        """Get coordinates using Nominatim (free)"""
        try:
            url = "https://nominatim.openstreetmap.org/search"
            params = {
                "q": destination,
                "format": "json",
                "limit": 1,
                "addressdetails": 1
            }
            headers = {"User-Agent": "AI-Travel-Planner/1.0"}
            
            async with self.session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data:
                        return float(data[0]["lat"]), float(data[0]["lon"])
            
            return None
            
        except Exception as e:
            self.logger.error("Error getting coordinates for POI search", error=str(e))
            return None
    
    async def _search_overpass_pois(
        self, 
        lat: float, 
        lon: float, 
        categories: List[str], 
        radius: int
    ) -> List[Dict]:
        """Search for POIs using Overpass API"""
        try:
            # Build Overpass query for different POI categories
            category_queries = []
            
            if "tourism" in categories:
                category_queries.append(f'node["tourism"](around:{radius},{lat},{lon});')
                category_queries.append(f'way["tourism"](around:{radius},{lat},{lon});')
            
            if "amenity" in categories:
                category_queries.append(f'node["amenity"~"^(restaurant|cafe|bar|pub|museum|theatre|cinema)$"](around:{radius},{lat},{lon});')
                category_queries.append(f'way["amenity"~"^(restaurant|cafe|bar|pub|museum|theatre|cinema)$"](around:{radius},{lat},{lon});')
            
            if "leisure" in categories:
                category_queries.append(f'node["leisure"](around:{radius},{lat},{lon});')
                category_queries.append(f'way["leisure"](around:{radius},{lat},{lon});')
            
            if "historic" in categories:
                category_queries.append(f'node["historic"](around:{radius},{lat},{lon});')
                category_queries.append(f'way["historic"](around:{radius},{lat},{lon});')
            
            overpass_query = f"""
            [out:json][timeout:30];
            (
              {chr(10).join(category_queries)}
            );
            out center meta;
            """
            
            url = "https://overpass-api.de/api/interpreter"
            headers = {"User-Agent": "AI-Travel-Planner/1.0"}
            
            async with self.session.post(url, data=overpass_query, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("elements", [])
            
            return []
            
        except Exception as e:
            self.logger.error("Error querying Overpass API for POIs", error=str(e))
            return []
    
    def _process_poi_data(
        self, 
        elements: List[Dict], 
        destination: str, 
        categories: List[str]
    ) -> Dict[str, Any]:
        """Process Overpass API POI data"""
        
        pois = []
        
        for element in elements[:50]:  # Limit to first 50 results
            tags = element.get("tags", {})
            
            # Skip elements without names (usually not interesting for tourists)
            name = tags.get("name")
            if not name:
                continue
            
            # Determine POI type and category
            poi_type = self._determine_poi_type(tags)
            if not poi_type:
                continue
            
            # Get coordinates
            if element["type"] == "node":
                poi_lat, poi_lon = element["lat"], element["lon"]
            else:
                center = element.get("center", {})
                poi_lat, poi_lon = center.get("lat", 0), center.get("lon", 0)
            
            # Extract additional information
            description = self._generate_description(tags, poi_type)
            
            poi = {
                "name": name,
                "type": poi_type,
                "category": self._get_category_from_tags(tags),
                "description": description,
                "address": self._format_address(tags),
                "coordinates": {"lat": poi_lat, "lon": poi_lon},
                "opening_hours": tags.get("opening_hours", "Unknown"),
                "phone": tags.get("phone", ""),
                "website": tags.get("website", ""),
                "wikipedia": tags.get("wikipedia", ""),
                "rating": self._estimate_rating(tags),
                "price_level": self._estimate_price_level(tags, poi_type),
                "accessibility": self._check_accessibility(tags),
                "source": "OpenStreetMap",
                "osm_id": element.get("id"),
                "last_updated": element.get("timestamp", "")
            }
            
            pois.append(poi)
        
        # Sort by estimated popularity/rating
        pois.sort(key=lambda x: x["rating"], reverse=True)
        
        return {
            "destination": destination,
            "categories": categories,
            "pois": pois,
            "total_found": len(pois),
            "search_timestamp": datetime.utcnow().isoformat(),
            "data_source": "OpenStreetMap + Overpass API (free)"
        }
    
    def _determine_poi_type(self, tags: Dict[str, str]) -> Optional[str]:
        """Determine POI type from OSM tags"""
        if "tourism" in tags:
            return tags["tourism"]
        elif "amenity" in tags:
            return tags["amenity"]
        elif "leisure" in tags:
            return tags["leisure"]
        elif "historic" in tags:
            return "historic_site"
        return None
    
    def _get_category_from_tags(self, tags: Dict[str, str]) -> str:
        """Get general category from specific tags"""
        tourism_attractions = ["attraction", "museum", "zoo", "aquarium", "theme_park", "viewpoint"]
        tourism_culture = ["artwork", "gallery", "theatre", "opera", "monument"]
        amenity_food = ["restaurant", "cafe", "bar", "pub", "fast_food"]
        leisure_activities = ["park", "garden", "sports_centre", "swimming_pool", "golf_course"]
        
        poi_type = self._determine_poi_type(tags)
        
        if poi_type in tourism_attractions:
            return "attraction"
        elif poi_type in tourism_culture:
            return "culture"
        elif poi_type in amenity_food:
            return "food_drink"
        elif poi_type in leisure_activities:
            return "recreation"
        elif tags.get("historic"):
            return "historic"
        else:
            return "other"
    
    def _generate_description(self, tags: Dict[str, str], poi_type: str) -> str:
        """Generate a description from OSM tags"""
        description_parts = []
        
        if "description" in tags:
            return tags["description"]
        
        # Build description from available tags
        if poi_type == "museum":
            description_parts.append("Museum")
        elif poi_type == "restaurant":
            cuisine = tags.get("cuisine", "")
            if cuisine:
                description_parts.append(f"{cuisine.title()} restaurant")
            else:
                description_parts.append("Restaurant")
        elif poi_type == "attraction":
            description_parts.append("Tourist attraction")
        elif poi_type == "park":
            description_parts.append("Park")
        else:
            description_parts.append(poi_type.replace("_", " ").title())
        
        # Add additional details
        if "building:levels" in tags:
            levels = tags["building:levels"]
            description_parts.append(f"({levels} floors)")
        
        if "fee" in tags:
            if tags["fee"] == "yes":
                description_parts.append("(Entry fee required)")
            else:
                description_parts.append("(Free entry)")
        
        return " ".join(description_parts) if description_parts else "Point of interest"
    
    def _format_address(self, tags: Dict[str, str]) -> str:
        """Format address from OSM tags"""
        address_parts = []
        
        if "addr:housenumber" in tags and "addr:street" in tags:
            address_parts.append(f"{tags['addr:housenumber']} {tags['addr:street']}")
        elif "addr:street" in tags:
            address_parts.append(tags["addr:street"])
        
        if "addr:city" in tags:
            address_parts.append(tags["addr:city"])
        
        if "addr:country" in tags:
            address_parts.append(tags["addr:country"])
        
        return ", ".join(address_parts) if address_parts else "Address not available"
    
    def _estimate_rating(self, tags: Dict[str, str]) -> float:
        """Estimate rating based on available tags"""
        # Base rating
        rating = 3.5
        
        # Boost for popular tourist attractions
        if tags.get("tourism") in ["attraction", "museum", "monument"]:
            rating += 0.5
        
        # Boost for UNESCO sites
        if "heritage" in tags or "unesco" in str(tags).lower():
            rating += 1.0
        
        # Boost for places with websites
        if "website" in tags:
            rating += 0.3
        
        # Boost for places with Wikipedia entries
        if "wikipedia" in tags:
            rating += 0.4
        
        return min(5.0, rating)
    
    def _estimate_price_level(self, tags: Dict[str, str], poi_type: str) -> str:
        """Estimate price level"""
        if tags.get("fee") == "no":
            return "Free"
        elif poi_type in ["park", "garden", "viewpoint"]:
            return "Free"
        elif poi_type in ["museum", "attraction", "zoo", "aquarium"]:
            return "$"
        elif poi_type in ["restaurant", "bar", "cafe"]:
            return "$$"
        else:
            return "$"
    
    def _check_accessibility(self, tags: Dict[str, str]) -> Dict[str, bool]:
        """Check accessibility features"""
        return {
            "wheelchair": tags.get("wheelchair") == "yes",
            "blind": tags.get("tactile_paving") == "yes",
            "hearing_loop": tags.get("hearing_loop") == "yes"
        }
    
    def _get_mock_poi_data(self, destination: str, categories: List[str]) -> Dict[str, Any]:
        """Return mock POI data when API is unavailable"""
        mock_pois = [
            {
                "name": f"Central Museum - {destination}",
                "type": "museum",
                "category": "culture",
                "description": "Main city museum with local history and art",
                "address": f"Museum Street 1, {destination}",
                "coordinates": {"lat": 0.0, "lon": 0.0},
                "rating": 4.2,
                "price_level": "$",
                "source": "mock"
            },
            {
                "name": f"City Park - {destination}",
                "type": "park",
                "category": "recreation",
                "description": "Large urban park perfect for walking and relaxation",
                "address": f"Park Avenue, {destination}",
                "coordinates": {"lat": 0.0, "lon": 0.0},
                "rating": 4.0,
                "price_level": "Free",
                "source": "mock"
            }
        ]
        
        return {
            "destination": destination,
            "categories": categories,
            "pois": mock_pois,
            "total_found": len(mock_pois),
            "search_timestamp": datetime.utcnow().isoformat(),
            "data_source": "mock"
        }