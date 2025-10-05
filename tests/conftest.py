"""
Test configuration and fixtures
"""

import pytest
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import Base, get_db
from app.core.config import get_settings

# Test database URL
TEST_DATABASE_URL = "sqlite:///./test_travel_planner.db"

# Create test engine
test_engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    # Create the database tables
    Base.metadata.create_all(bind=test_engine)
    
    # Create a session
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Drop all tables after the test
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database override"""
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "full_name": "Test User"
    }


@pytest.fixture
def sample_trip_data():
    """Sample trip data for testing"""
    return {
        "destination": "Paris, France",
        "start_date": "2024-06-01T00:00:00",
        "end_date": "2024-06-07T00:00:00",
        "budget": 2000,
        "currency": "USD",
        "trip_type": "leisure",
        "group_size": 2
    }


@pytest.fixture
def sample_preferences():
    """Sample user preferences for testing"""
    return {
        "preferred_airlines": ["Air France", "United Airlines"],
        "preferred_class": "economy",
        "accommodation_type": ["hotel"],
        "budget_range": "mid-range",
        "activity_types": ["cultural", "sightseeing"],
        "dietary_restrictions": [],
        "travel_pace": "moderate"
    }