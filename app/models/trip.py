"""
Trip model for the AI Travel Planner.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Float, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Trip(Base):
    """Trip model"""
    __tablename__ = "trips"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Trip details
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    destination = Column(String(255), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    
    # Trip metadata
    budget = Column(Float, nullable=True)
    currency = Column(String(3), default="USD")
    trip_type = Column(String(50), nullable=True)  # business, leisure, adventure, etc.
    group_size = Column(Integer, default=1)
    
    # Status
    status = Column(String(20), default="planning")  # planning, confirmed, completed, cancelled
    is_public = Column(Boolean, default=False)
    
    # AI-generated data
    generated_itinerary = Column(JSON, nullable=True)
    preferences_snapshot = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="trips")
    bookings = relationship("Booking", back_populates="trip", cascade="all, delete-orphan")