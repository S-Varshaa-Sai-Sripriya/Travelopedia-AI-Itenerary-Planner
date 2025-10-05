"""
User preferences model for the AI Travel Planner.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Float, Boolean, JSON, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class UserPreference(Base):
    """User preferences model for personalization"""
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Travel preferences
    preferred_airlines = Column(JSON, nullable=True)  # List of airline codes
    preferred_hotel_chains = Column(JSON, nullable=True)  # List of hotel chains
    preferred_class = Column(String(20), default="economy")  # economy, business, first
    preferred_seat = Column(String(20), nullable=True)  # window, aisle, middle
    
    # Accommodation preferences
    accommodation_type = Column(JSON, nullable=True)  # hotel, airbnb, hostel, etc.
    room_type = Column(String(50), nullable=True)  # single, double, suite, etc.
    amenities = Column(JSON, nullable=True)  # wifi, pool, gym, spa, etc.
    
    # Activity preferences
    activity_types = Column(JSON, nullable=True)  # adventure, cultural, relaxation, etc.
    interests = Column(JSON, nullable=True)  # museums, beaches, nightlife, etc.
    mobility_requirements = Column(String(100), nullable=True)
    
    # Dietary and accessibility
    dietary_restrictions = Column(JSON, nullable=True)  # vegetarian, vegan, halal, etc.
    accessibility_needs = Column(JSON, nullable=True)
    
    # Budget preferences
    budget_range = Column(String(20), nullable=True)  # budget, mid-range, luxury
    budget_distribution = Column(JSON, nullable=True)  # % for flights, hotels, activities
    
    # Travel style
    travel_pace = Column(String(20), default="moderate")  # slow, moderate, fast
    group_preference = Column(String(20), default="any")  # solo, couple, family, group
    planning_style = Column(String(20), default="balanced")  # structured, flexible, balanced
    
    # Notifications and communication
    notification_preferences = Column(JSON, nullable=True)
    language = Column(String(5), default="en")
    timezone = Column(String(50), nullable=True)
    
    # GNN features (for learning)
    feature_vector = Column(JSON, nullable=True)  # Computed feature representation
    similarity_scores = Column(JSON, nullable=True)  # Similarity to other users
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="preferences")