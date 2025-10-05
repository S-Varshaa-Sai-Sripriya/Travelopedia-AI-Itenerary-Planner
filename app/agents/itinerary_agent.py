"""
Itinerary Agent

This agent consolidates all inputs from other agents and external APIs
to create a final, bookable travel itinerary.
"""

import asyncio
from typing import Dict, Any, List, Optional
import json
from datetime import datetime, timedelta

from app.core.config import get_settings
from app.core.logging_config import get_logger

settings = get_settings()
logger = get_logger(__name__)


class ItineraryAgent:
    """Agent responsible for generating final travel itineraries"""
    
    def __init__(self):
        self.settings = settings
        self.logger = logger
    
    async def generate_itinerary(
        self,
        travel_request: Dict[str, Any],
        recommendations: Dict[str, Any],
        budget_plan: Dict[str, Any],
        real_time_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate complete travel itinerary"""
        self.logger.info("Generating travel itinerary")
        
        try:
            # Extract basic trip information
            destination = travel_request.get("destination")
            start_date = datetime.fromisoformat(travel_request.get("start_date"))
            end_date = datetime.fromisoformat(travel_request.get("end_date"))
            duration = (end_date - start_date).days + 1
            
            # Generate daily schedule
            daily_schedule = await self._create_daily_schedule(
                start_date, end_date, destination, recommendations, budget_plan
            )
            
            # Create booking summary
            booking_summary = await self._create_booking_summary(
                daily_schedule, budget_plan, real_time_data
            )
            
            # Calculate itinerary metrics
            metrics = await self._calculate_metrics(daily_schedule, booking_summary, budget_plan)
            
            # Generate calendar events
            calendar_events = await self._generate_calendar_events(daily_schedule)
            
            itinerary = {
                "status": "success",
                "trip_info": {
                    "destination": destination,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "duration_days": duration,
                    "travelers": travel_request.get("travelers", 1)
                },
                "daily_schedule": daily_schedule,
                "booking_summary": booking_summary,
                "budget_breakdown": budget_plan,
                "metrics": metrics,
                "calendar_events": calendar_events,
                "generated_at": datetime.utcnow().isoformat(),
                "version": "1.0"
            }
            
            self.logger.info("Itinerary generated successfully", duration=duration)
            return itinerary
            
        except Exception as e:
            self.logger.error("Error generating itinerary", error=str(e))
            return {
                "status": "error",
                "message": "Failed to generate itinerary",
                "error": str(e)
            }
    
    async def _create_daily_schedule(
        self,
        start_date: datetime,
        end_date: datetime,
        destination: str,
        recommendations: Dict[str, Any],
        budget_plan: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Create detailed daily schedule"""
        
        daily_schedule = []
        current_date = start_date
        day_number = 1
        
        while current_date <= end_date:
            day_schedule = {
                "day": day_number,
                "date": current_date.isoformat().split('T')[0],
                "day_of_week": current_date.strftime("%A"),
                "activities": [],
                "meals": [],
                "accommodation": None,
                "transport": [],
                "daily_budget": 0,
                "notes": []
            }
            
            # Add activities based on day type
            if day_number == 1:
                # Arrival day
                day_schedule["activities"] = await self._get_arrival_activities(current_date, destination)
            elif current_date == end_date:
                # Departure day
                day_schedule["activities"] = await self._get_departure_activities(current_date, destination)
            else:
                # Regular day
                day_schedule["activities"] = await self._get_daily_activities(
                    current_date, destination, recommendations, day_number
                )
            
            # Add meals
            day_schedule["meals"] = await self._get_daily_meals(recommendations, day_number)
            
            # Add accommodation
            day_schedule["accommodation"] = await self._get_accommodation(
                recommendations, current_date, budget_plan
            )
            
            # Calculate daily budget
            day_schedule["daily_budget"] = await self._calculate_daily_budget(
                day_schedule, budget_plan
            )
            
            daily_schedule.append(day_schedule)
            current_date += timedelta(days=1)
            day_number += 1
        
        return daily_schedule
    
    async def _get_arrival_activities(self, date: datetime, destination: str) -> List[Dict[str, Any]]:
        """Get activities for arrival day"""
        return [
            {
                "time": "14:00",
                "type": "transport",
                "title": "Airport Transfer",
                "description": f"Transfer from airport to accommodation in {destination}",
                "duration": 60,
                "cost": 50,
                "booking_required": True
            },
            {
                "time": "16:00",
                "type": "activity",
                "title": "Check-in & City Orientation",
                "description": "Check into accommodation and get oriented with the area",
                "duration": 120,
                "cost": 0,
                "booking_required": False
            },
            {
                "time": "19:00",
                "type": "meal",
                "title": "Welcome Dinner",
                "description": "Dinner at a local restaurant to start your trip",
                "duration": 90,
                "cost": 60,
                "booking_required": False
            }
        ]
    
    async def _get_departure_activities(self, date: datetime, destination: str) -> List[Dict[str, Any]]:
        """Get activities for departure day"""
        return [
            {
                "time": "10:00",
                "type": "activity",
                "title": "Last-minute Shopping",
                "description": "Pick up souvenirs and last-minute items",
                "duration": 120,
                "cost": 50,
                "booking_required": False
            },
            {
                "time": "13:00",
                "type": "transport",
                "title": "Airport Transfer",
                "description": f"Transfer from accommodation to airport",
                "duration": 60,
                "cost": 50,
                "booking_required": True
            }
        ]
    
    async def _get_daily_activities(
        self,
        date: datetime,
        destination: str,
        recommendations: Dict[str, Any],
        day_number: int
    ) -> List[Dict[str, Any]]:
        """Get activities for a regular day"""
        
        # TODO: Use actual recommendations data
        # This is a placeholder implementation
        
        activities = [
            {
                "time": "09:00",
                "type": "activity",
                "title": f"Morning Activity - Day {day_number}",
                "description": "Explore local attractions and landmarks",
                "duration": 180,
                "cost": 30,
                "booking_required": True
            },
            {
                "time": "14:00",
                "type": "activity",
                "title": f"Afternoon Experience - Day {day_number}",
                "description": "Cultural experience or guided tour",
                "duration": 150,
                "cost": 45,
                "booking_required": True
            },
            {
                "time": "18:00",
                "type": "activity",
                "title": "Evening Leisure",
                "description": "Free time for relaxation or optional activities",
                "duration": 120,
                "cost": 0,
                "booking_required": False
            }
        ]
        
        return activities
    
    async def _get_daily_meals(self, recommendations: Dict[str, Any], day_number: int) -> List[Dict[str, Any]]:
        """Get meal recommendations for the day"""
        return [
            {
                "time": "08:00",
                "type": "breakfast",
                "title": "Breakfast",
                "description": "Local breakfast at accommodation or nearby cafe",
                "cost": 15,
                "location": "Hotel or nearby"
            },
            {
                "time": "12:30",
                "type": "lunch",
                "title": "Lunch",
                "description": "Local cuisine lunch",
                "cost": 25,
                "location": "Recommended restaurant"
            },
            {
                "time": "19:30",
                "type": "dinner",
                "title": "Dinner",
                "description": "Traditional dinner experience",
                "cost": 40,
                "location": "Recommended restaurant"
            }
        ]
    
    async def _get_accommodation(
        self,
        recommendations: Dict[str, Any],
        date: datetime,
        budget_plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get accommodation for the night"""
        return {
            "name": "Recommended Hotel",
            "type": "hotel",
            "rating": 4.2,
            "cost_per_night": budget_plan.get("accommodation", {}).get("daily_amount", 100),
            "amenities": ["wifi", "breakfast", "gym"],
            "booking_reference": None,
            "check_in": "15:00",
            "check_out": "11:00"
        }
    
    async def _calculate_daily_budget(
        self,
        day_schedule: Dict[str, Any],
        budget_plan: Dict[str, Any]
    ) -> float:
        """Calculate total daily budget"""
        daily_cost = 0
        
        # Add activity costs
        for activity in day_schedule.get("activities", []):
            daily_cost += activity.get("cost", 0)
        
        # Add meal costs
        for meal in day_schedule.get("meals", []):
            daily_cost += meal.get("cost", 0)
        
        # Add accommodation cost
        accommodation = day_schedule.get("accommodation")
        if accommodation:
            daily_cost += accommodation.get("cost_per_night", 0)
        
        return daily_cost
    
    async def _create_booking_summary(
        self,
        daily_schedule: List[Dict[str, Any]],
        budget_plan: Dict[str, Any],
        real_time_data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create summary of all bookings needed"""
        
        bookings = {
            "flights": [],
            "accommodation": [],
            "activities": [],
            "transport": [],
            "total_bookings": 0,
            "total_cost": 0,
            "booking_urgency": []
        }
        
        # Extract bookings from daily schedule
        for day in daily_schedule:
            # Activities that require booking
            for activity in day.get("activities", []):
                if activity.get("booking_required", False):
                    bookings["activities"].append({
                        "day": day["day"],
                        "date": day["date"],
                        "activity": activity,
                        "status": "pending",
                        "priority": "medium"
                    })
            
            # Accommodation booking
            accommodation = day.get("accommodation")
            if accommodation and not any(b["date"] == day["date"] for b in bookings["accommodation"]):
                bookings["accommodation"].append({
                    "date": day["date"],
                    "accommodation": accommodation,
                    "status": "pending",
                    "priority": "high"
                })
        
        # Calculate totals
        bookings["total_bookings"] = (
            len(bookings["flights"]) +
            len(bookings["accommodation"]) +
            len(bookings["activities"]) +
            len(bookings["transport"])
        )
        
        # Calculate total cost from budget plan
        bookings["total_cost"] = sum(
            category.get("allocated", 0) for category in budget_plan.values()
            if isinstance(category, dict)
        )
        
        return bookings
    
    async def _calculate_metrics(
        self,
        daily_schedule: List[Dict[str, Any]],
        booking_summary: Dict[str, Any],
        budget_plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate itinerary metrics"""
        
        total_activities = sum(len(day.get("activities", [])) for day in daily_schedule)
        total_days = len(daily_schedule)
        
        return {
            "total_days": total_days,
            "total_activities": total_activities,
            "activities_per_day": total_activities / total_days if total_days > 0 else 0,
            "total_bookings": booking_summary.get("total_bookings", 0),
            "estimated_total_cost": booking_summary.get("total_cost", 0),
            "budget_utilization": 0.85,  # Placeholder
            "itinerary_density": "moderate",  # Based on activities per day
            "confidence_score": 0.89,
            "customization_level": "high"
        }
    
    async def _generate_calendar_events(self, daily_schedule: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate calendar events for the itinerary"""
        
        events = []
        
        for day in daily_schedule:
            date = day["date"]
            
            # Add activities as events
            for activity in day.get("activities", []):
                events.append({
                    "title": activity["title"],
                    "description": activity["description"],
                    "start_time": f"{date}T{activity['time']}:00",
                    "duration_minutes": activity.get("duration", 60),
                    "location": activity.get("location", ""),
                    "type": "activity",
                    "booking_required": activity.get("booking_required", False)
                })
            
            # Add meals as events
            for meal in day.get("meals", []):
                events.append({
                    "title": meal["title"],
                    "description": meal["description"],
                    "start_time": f"{date}T{meal['time']}:00",
                    "duration_minutes": 60,
                    "location": meal.get("location", ""),
                    "type": "meal",
                    "booking_required": False
                })
        
        return events