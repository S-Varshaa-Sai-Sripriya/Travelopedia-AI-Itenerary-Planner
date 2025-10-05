#!/usr/bin/env python3
"""
Database initialization script for AI Travel Planner

This script initializes the database with tables and sample data.
Run this after setting up your environment.
"""

import sys
import os
from pathlib import Path

# Add the app directory to the Python path
app_dir = Path(__file__).parent.parent
sys.path.insert(0, str(app_dir))

from app.core.database import engine, Base, init_db
from app.core.config import get_settings
from app.core.logging_config import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)
settings = get_settings()


def create_tables():
    """Create all database tables"""
    logger.info("Creating database tables...")
    
    try:
        # Import all models to ensure they're registered
        from app.models.user import User
        from app.models.trip import Trip
        from app.models.booking import Booking
        from app.models.preference import UserPreference
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
    except Exception as e:
        logger.error("Error creating database tables", error=str(e))
        raise


def create_sample_data():
    """Create sample data for development"""
    logger.info("Creating sample data...")
    
    try:
        from sqlalchemy.orm import sessionmaker
        from app.models.user import User
        from app.models.preference import UserPreference
        import bcrypt
        from datetime import datetime
        
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Check if sample data already exists
        existing_user = db.query(User).filter(User.email == "demo@example.com").first()
        if existing_user:
            logger.info("Sample data already exists, skipping...")
            db.close()
            return
        
        # Create sample user
        hashed_password = bcrypt.hashpw("demo123".encode('utf-8'), bcrypt.gensalt())
        sample_user = User(
            email="demo@example.com",
            username="demo_user",
            full_name="Demo User",
            hashed_password=hashed_password.decode('utf-8'),
            is_active=True,
            is_verified=True,
            bio="Sample user for testing the AI Travel Planner",
            location="San Francisco, CA"
        )
        
        db.add(sample_user)
        db.commit()
        db.refresh(sample_user)
        
        # Create sample user preferences
        sample_preferences = UserPreference(
            user_id=sample_user.id,
            preferred_airlines=["American Airlines", "United Airlines"],
            preferred_hotel_chains=["Hilton", "Marriott"],
            preferred_class="economy",
            preferred_seat="window",
            accommodation_type=["hotel", "boutique"],
            activity_types=["cultural", "adventure", "relaxation"],
            interests=["museums", "restaurants", "hiking", "beaches"],
            dietary_restrictions=["vegetarian"],
            budget_range="mid-range",
            travel_pace="moderate",
            language="en",
            timezone="America/Los_Angeles"
        )
        
        db.add(sample_preferences)
        db.commit()
        
        logger.info("Sample data created successfully")
        logger.info("Demo user created: demo@example.com / demo123")
        
        db.close()
        
    except Exception as e:
        logger.error("Error creating sample data", error=str(e))
        raise


def main():
    """Main initialization function"""
    logger.info("Starting database initialization...")
    
    try:
        # Create tables
        create_tables()
        
        # Create sample data for development
        if settings.DEBUG:
            create_sample_data()
        
        logger.info("Database initialization completed successfully!")
        logger.info(f"Database URL: {settings.DATABASE_URL}")
        
        print("✅ Database initialization completed!")
        print("📊 Tables created successfully")
        
        if settings.DEBUG:
            print("👤 Sample user created: demo@example.com / demo123")
        
        print("\n🚀 You can now start the application:")
        print("   uvicorn app.main:app --reload")
        
    except Exception as e:
        logger.error("Database initialization failed", error=str(e))
        print(f"❌ Database initialization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()