"""
Booking model for the AI Travel Planner.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text, Boolean, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Booking(Base):
    """Booking model"""
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=True)
    
    # Booking details
    booking_type = Column(String(50), nullable=False)  # flight, hotel, activity, transport
    provider = Column(String(100), nullable=False)
    external_booking_id = Column(String(255), nullable=True)
    
    # Booking information
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    booking_date = Column(DateTime, nullable=False)
    start_datetime = Column(DateTime, nullable=True)
    end_datetime = Column(DateTime, nullable=True)
    
    # Financial details
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    payment_status = Column(String(20), default="pending")  # pending, paid, refunded, failed
    
    # Status and metadata
    booking_status = Column(String(20), default="confirmed")  # confirmed, cancelled, completed
    booking_data = Column(JSON, nullable=True)  # Store provider-specific data
    
    # Confirmation details
    confirmation_number = Column(String(100), nullable=True)
    booking_url = Column(String(500), nullable=True)
    cancellation_policy = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="bookings")
    trip = relationship("Trip", back_populates="bookings")