"""
Test cases for health endpoints
"""

import pytest
from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    """Test basic health check endpoint"""
    response = client.get("/api/v1/health")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert data["version"] == "1.0.0"


def test_detailed_health_check(client: TestClient):
    """Test detailed health check endpoint"""
    response = client.get("/api/v1/health/detailed")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "healthy"
    assert "system" in data
    assert "services" in data
    assert "python_version" in data["system"]
    assert "platform" in data["system"]


def test_root_endpoint(client: TestClient):
    """Test root endpoint"""
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["message"] == "AI Travel Planner API"
    assert data["version"] == "1.0.0"
    assert data["status"] == "healthy"