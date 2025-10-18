"""
Travel Request and Response Models

Pydantic models for type safety and validation in the AI Travel Planner system.
"""

from typing import Dict, Any, List, Optional, Union
from datetime import datetime, date
from pydantic import BaseModel, Field, field_validator, model_validator
from enum import Enum


class TripType(str, Enum):
    """Enum for trip types"""
    LEISURE = "leisure"
    BUSINESS = "business"
    ADVENTURE = "adventure"
    HONEYMOON = "honeymoon"
    FAMILY = "family"
    SOLO = "solo"
    GROUP = "group"
    EDUCATIONAL = "educational"
    MEDICAL = "medical"
    RELIGIOUS = "religious"


class AccommodationType(str, Enum):
    """Enum for accommodation preferences"""
    HOTEL = "hotel"
    HOSTEL = "hostel"
    APARTMENT = "apartment"
    RESORT = "resort"
    BNB = "bnb"
    GUESTHOUSE = "guesthouse"
    CAMPING = "camping"
    LUXURY = "luxury"


class TransportType(str, Enum):
    """Enum for transport preferences"""
    FLIGHT = "flight"
    TRAIN = "train"
    BUS = "bus"
    CAR = "car"
    SHIP = "ship"
    MIXED = "mixed"


class TravelPreferences(BaseModel):
    """Travel preferences model"""
    accommodation: AccommodationType = Field(default=AccommodationType.HOTEL)
    transport: TransportType = Field(default=TransportType.FLIGHT)
    activities: List[str] = Field(default_factory=lambda: ["sightseeing"])
    food: str = Field(default="local cuisine")
    budget_priority: str = Field(default="balanced", description="economy, balanced, or luxury")
    pace: str = Field(default="moderate", description="slow, moderate, or fast")
    group_type: Optional[str] = Field(default=None, description="family, couple, friends, solo")


class TravelConstraints(BaseModel):
    """Travel constraints model"""
    dietary: List[str] = Field(default_factory=list, description="Dietary restrictions")
    accessibility: List[str] = Field(default_factory=list, description="Accessibility requirements")
    special_requirements: List[str] = Field(default_factory=list, description="Special requirements")
    visa_requirements: Optional[bool] = Field(default=None)
    vaccination_requirements: Optional[bool] = Field(default=None)


class TravelRequest(BaseModel):
    """Complete travel request model"""
    destination: str = Field(..., description="Destination city/country")
    start_date: str = Field(..., description="Start date in YYYY-MM-DD format")
    end_date: str = Field(..., description="End date in YYYY-MM-DD format")
    budget: float = Field(..., ge=0, description="Total budget in USD")
    currency: str = Field(default="USD", description="Currency code")
    travelers: int = Field(..., ge=1, le=50, description="Number of travelers")
    trip_type: TripType = Field(default=TripType.LEISURE)
    preferences: TravelPreferences = Field(default_factory=TravelPreferences)
    constraints: TravelConstraints = Field(default_factory=TravelConstraints)
    user_id: Optional[str] = Field(default=None, description="User ID for personalization")
    priority: str = Field(default="normal", description="normal, urgent, or flexible")

    @field_validator('start_date', 'end_date')
    @classmethod
    def validate_date_format(cls, v):
        """Validate date format"""
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('Date must be in YYYY-MM-DD format')

    @model_validator(mode='after')
    def validate_dates(self):
        """Validate that end date is after start date"""
        start_date_str = self.start_date
        end_date_str = self.end_date
        
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            
            if end_date <= start_date:
                raise ValueError('End date must be after start date')
            
            if start_date <= datetime.now():
                raise ValueError('Start date must be in the future')
        
        return self


class ValidationError(BaseModel):
    """Validation error model"""
    field: str
    message: str
    code: str


class ValidationResult(BaseModel):
    """Validation result model"""
    is_valid: bool
    errors: List[ValidationError] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0)


class FlightRecommendation(BaseModel):
    """Flight recommendation model"""
    airline: str
    price: float
    departure_time: str
    arrival_time: str
    duration: str
    stops: int
    booking_class: str
    confidence_score: float


class HotelRecommendation(BaseModel):
    """Hotel recommendation model"""
    name: str
    price_per_night: float
    rating: float
    location: str
    amenities: List[str]
    room_type: str
    confidence_score: float


class ActivityRecommendation(BaseModel):
    """Activity recommendation model"""
    name: str
    category: str
    price: Optional[float] = None
    duration: str
    rating: float
    description: str
    location: str
    confidence_score: float


class GNNRecommendations(BaseModel):
    """GNN agent recommendations model"""
    personalization_score: float = Field(ge=0.0, le=1.0)
    flights: List[FlightRecommendation] = Field(default_factory=list)
    hotels: List[HotelRecommendation] = Field(default_factory=list)
    activities: List[ActivityRecommendation] = Field(default_factory=list)
    reasoning: str = Field(default="")
    confidence_score: float = Field(ge=0.0, le=1.0)


class BudgetAllocation(BaseModel):
    """Budget allocation model"""
    flights: float = Field(ge=0)
    accommodation: float = Field(ge=0)
    activities: float = Field(ge=0)
    food: float = Field(ge=0)
    transportation: float = Field(ge=0)
    miscellaneous: float = Field(ge=0)


class BudgetOptimization(BaseModel):
    """Budget optimization result model"""
    optimization_score: float = Field(ge=0.0, le=1.0)
    budget_allocation: BudgetAllocation
    cost_per_person: float = Field(ge=0)
    savings_opportunities: List[str] = Field(default_factory=list)
    alternative_options: List[Dict[str, Any]] = Field(default_factory=list)
    confidence_score: float = Field(ge=0.0, le=1.0)


class DailyItinerary(BaseModel):
    """Daily itinerary model"""
    date: str
    activities: List[Dict[str, Any]] = Field(default_factory=list)
    meals: List[Dict[str, Any]] = Field(default_factory=list)
    transportation: List[Dict[str, Any]] = Field(default_factory=list)
    estimated_cost: float = Field(ge=0)
    notes: str = Field(default="")


class ItineraryGeneration(BaseModel):
    """Itinerary generation result model"""
    itinerary_confidence: float = Field(ge=0.0, le=1.0)
    daily_schedule: List[DailyItinerary] = Field(default_factory=list)
    bookings_required: List[str] = Field(default_factory=list)
    estimated_timeline: str
    total_estimated_cost: float = Field(ge=0)
    contingency_plans: List[str] = Field(default_factory=list)


class AgentResults(BaseModel):
    """Combined agent results model"""
    gnn_recommendations: GNNRecommendations
    budget_optimization: BudgetOptimization
    itinerary_generation: ItineraryGeneration
    coordination_status: str = Field(default="completed")
    processing_time: float = Field(ge=0)


class TravelPlanResponse(BaseModel):
    """Complete travel plan response model"""
    status: str = Field(..., description="success, error, or partial")
    request_id: str = Field(..., description="Unique request identifier")
    parsed_request: TravelRequest
    validation: ValidationResult
    agent_results: Optional[AgentResults] = None
    llm_model_used: str = Field(default="unknown")
    timestamp: str
    processing_complete: bool = Field(default=False)
    errors: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)


class TravelPlanUpdate(BaseModel):
    """Travel plan update model for real-time updates"""
    request_id: str
    update_type: str  # price_change, availability_change, weather_alert, etc.
    affected_component: str  # flight, hotel, activity, etc.
    old_value: Optional[Dict[str, Any]] = None
    new_value: Dict[str, Any]
    impact_score: float = Field(ge=0.0, le=1.0)
    recommended_action: str
    timestamp: str


class UserFeedback(BaseModel):
    """User feedback model for continuous learning"""
    request_id: str
    user_id: Optional[str] = None
    overall_satisfaction: float = Field(ge=1.0, le=5.0)
    component_ratings: Dict[str, float] = Field(default_factory=dict)
    liked_recommendations: List[str] = Field(default_factory=list)
    disliked_recommendations: List[str] = Field(default_factory=list)
    suggestions: str = Field(default="")
    would_use_again: bool = Field(default=True)
    timestamp: str