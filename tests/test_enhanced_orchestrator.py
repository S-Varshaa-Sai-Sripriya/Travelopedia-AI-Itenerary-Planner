"""
Test Enhanced LLM Orchestrator

Comprehensive tests for the enhanced LLM Orchestrator with Ollama integration,
Pydantic models, and real-time API services.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta

from app.agents.llm_orchestrator import LLMOrchestrator
from app.services.real_time_api import RealTimeAPIService, fetch_travel_data
from app.models.travel_request import TravelRequest, ValidationResult


class TestLLMOrchestrator:
    """Test suite for LLM Orchestrator"""
    
    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance for testing"""
        return LLMOrchestrator()
    
    @pytest.mark.asyncio
    async def test_parse_travel_request_with_mock(self, orchestrator):
        """Test travel request parsing with mock LLM"""
        # Mock the LLM to avoid actual Ollama dependency in tests
        orchestrator.llm = None  # Force fallback parsing
        
        request = "I want to visit Tokyo for 5 days with a budget of $3000 for 2 people"
        result = await orchestrator.parse_travel_request(request)
        
        assert isinstance(result, dict)
        assert "destination" in result
        assert "budget" in result
        assert "travelers" in result
        assert result["budget"] > 0
        assert result["travelers"] > 0
    
    @pytest.mark.asyncio
    async def test_validate_constraints_valid(self, orchestrator):
        """Test constraint validation with valid data"""
        future_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        future_end_date = (datetime.now() + timedelta(days=37)).strftime("%Y-%m-%d")
        
        valid_request = {
            "destination": "Paris, France",
            "start_date": future_date,
            "end_date": future_end_date,
            "budget": 2000.0,
            "travelers": 2
        }
        
        result = await orchestrator.validate_constraints(valid_request)
        
        assert result["is_valid"] is True
        assert len(result["errors"]) == 0
    
    @pytest.mark.asyncio
    async def test_validate_constraints_invalid_dates(self, orchestrator):
        """Test constraint validation with invalid dates"""
        past_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        future_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        
        invalid_request = {
            "destination": "Paris, France",
            "start_date": past_date,  # Past date
            "end_date": future_date,
            "budget": 2000.0,
            "travelers": 2
        }
        
        result = await orchestrator.validate_constraints(invalid_request)
        
        assert result["is_valid"] is False
        assert len(result["errors"]) > 0
        assert any("future" in error.lower() for error in result["errors"])
    
    @pytest.mark.asyncio
    async def test_validate_constraints_low_budget(self, orchestrator):
        """Test constraint validation with low budget"""
        future_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        future_end_date = (datetime.now() + timedelta(days=37)).strftime("%Y-%m-%d")
        
        low_budget_request = {
            "destination": "Paris, France",
            "start_date": future_date,
            "end_date": future_end_date,
            "budget": 50.0,  # Very low budget
            "travelers": 2
        }
        
        result = await orchestrator.validate_constraints(low_budget_request)
        
        assert result["is_valid"] is False
        assert len(result["errors"]) > 0
        assert any("budget" in error.lower() for error in result["errors"])
    
    @pytest.mark.asyncio
    async def test_coordinate_agents(self, orchestrator):
        """Test agent coordination"""
        sample_request = {
            "destination": "Tokyo, Japan",
            "start_date": "2024-06-01",
            "end_date": "2024-06-07",
            "budget": 3000.0,
            "travelers": 2
        }
        
        result = await orchestrator.coordinate_agents(sample_request)
        
        assert "gnn_recommendations" in result
        assert "budget_optimization" in result
        assert "itinerary_generation" in result
        assert result["coordination_status"] == "completed"
        assert result["processing_time"] > 0
    
    @pytest.mark.asyncio
    async def test_process_request_end_to_end(self, orchestrator):
        """Test complete request processing"""
        # Force fallback parsing for consistent testing
        orchestrator.llm = None
        
        request = "Plan a 5-day trip to Barcelona for 2 people with $2500 budget"
        result = await orchestrator.process_request(request)
        
        assert result["status"] in ["success", "error"]
        assert "parsed_request" in result
        assert "validation" in result
        assert "timestamp" in result
        
        if result["status"] == "success":
            assert "agent_results" in result
            assert result["processing_complete"] is True


class TestRealTimeAPIService:
    """Test suite for Real-Time API Service"""
    
    @pytest.fixture
    async def api_service(self):
        """Create API service instance for testing"""
        async with RealTimeAPIService() as service:
            yield service
    
    @pytest.mark.asyncio
    async def test_mock_weather_data(self, api_service):
        """Test mock weather data generation"""
        dates = ["2024-06-01", "2024-06-02", "2024-06-03"]
        result = api_service._mock_weather_data("Tokyo", dates)
        
        assert result["destination"] == "Tokyo"
        assert "current_weather" in result
        assert "forecast" in result
        assert len(result["forecast"]) == len(dates)
        assert result["status"] == "mock"
    
    @pytest.mark.asyncio
    async def test_mock_flight_data(self, api_service):
        """Test mock flight data generation"""
        result = api_service._mock_flight_data("NYC", "Tokyo", "2024-06-01")
        
        assert result["origin"] == "NYC"
        assert result["destination"] == "Tokyo"
        assert result["date"] == "2024-06-01"
        assert "flights" in result
        assert len(result["flights"]) > 0
        assert result["status"] == "mock"
    
    @pytest.mark.asyncio
    async def test_mock_hotel_data(self, api_service):
        """Test mock hotel data generation"""
        result = api_service._mock_hotel_data("Tokyo", "2024-06-01", "2024-06-07")
        
        assert result["destination"] == "Tokyo"
        assert result["checkin_date"] == "2024-06-01"
        assert result["checkout_date"] == "2024-06-07"
        assert "hotels" in result
        assert len(result["hotels"]) > 0
        assert result["status"] == "mock"
    
    @pytest.mark.asyncio
    async def test_mock_currency_data(self, api_service):
        """Test mock currency data generation"""
        result = api_service._mock_currency_data("USD", ["EUR", "JPY"])
        
        assert result["base_currency"] == "USD"
        assert "rates" in result
        assert "EUR" in result["rates"]
        assert "JPY" in result["rates"]
        assert result["status"] == "mock"
    
    @pytest.mark.asyncio 
    @patch('aiohttp.ClientSession.get')
    async def test_weather_api_with_key(self, mock_get, api_service):
        """Test weather API with actual API key (mocked response)"""
        # Mock the API responses
        mock_geocoding_response = MagicMock()
        mock_geocoding_response.status = 200
        mock_geocoding_response.json = AsyncMock(return_value=[{"lat": 35.6762, "lon": 139.6503}])
        
        mock_weather_response = MagicMock()
        mock_weather_response.status = 200
        mock_weather_response.json = AsyncMock(return_value={
            "main": {"temp": 22.5, "humidity": 65},
            "weather": [{"description": "clear sky"}],
            "wind": {"speed": 3.2}
        })
        
        mock_forecast_response = MagicMock()
        mock_forecast_response.status = 200
        mock_forecast_response.json = AsyncMock(return_value={
            "list": [
                {
                    "dt_txt": "2024-06-01 12:00:00",
                    "main": {"temp": 23.0, "humidity": 60},
                    "weather": [{"description": "sunny"}],
                    "wind": {"speed": 2.8}
                }
            ]
        })
        
        # Set up the mock to return different responses for different URLs
        mock_get.return_value.__aenter__.side_effect = [
            mock_geocoding_response,
            mock_weather_response,
            mock_forecast_response
        ]
        
        # Set a mock API key
        api_service.settings.OPENWEATHER_API_KEY = "test_key"
        
        result = await api_service.get_weather_data("Tokyo", ["2024-06-01"])
        
        assert result["status"] in ["success", "mock"]
        assert "destination" in result
        assert "current_weather" in result
    
    @pytest.mark.asyncio
    async def test_get_all_travel_data_mock(self, api_service):
        """Test fetching all travel data with mock responses"""
        # Force all API keys to None to ensure mock data
        api_service.settings.OPENWEATHER_API_KEY = None
        api_service.settings.AVIATIONSTACK_API_KEY = None
        api_service.settings.FIXER_API_KEY = None
        
        result = await api_service.get_all_travel_data(
            destination="Tokyo",
            origin="NYC",
            start_date="2024-06-01",
            end_date="2024-06-07"
        )
        
        assert result["status"] == "success"
        assert result["destination"] == "Tokyo"
        assert result["origin"] == "NYC"
        assert "weather" in result
        assert "flights" in result
        assert "hotels" in result
        assert "currency" in result
        assert "fetch_timestamp" in result


class TestPydanticModels:
    """Test suite for Pydantic models"""
    
    def test_travel_request_validation_valid(self):
        """Test TravelRequest model with valid data"""
        future_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        future_end_date = (datetime.now() + timedelta(days=37)).strftime("%Y-%m-%d")
        
        request = TravelRequest(
            destination="Tokyo, Japan",
            start_date=future_date,
            end_date=future_end_date,
            budget=3000.0,
            travelers=2,
            trip_type="leisure"
        )
        
        assert request.destination == "Tokyo, Japan"
        assert request.budget == 3000.0
        assert request.travelers == 2
        assert request.currency == "USD"  # default value
    
    def test_travel_request_validation_invalid_date_format(self):
        """Test TravelRequest model with invalid date format"""
        with pytest.raises(ValueError, match="Date must be in YYYY-MM-DD format"):
            TravelRequest(
                destination="Tokyo, Japan",
                start_date="2024/06/01",  # Wrong format
                end_date="2024-06-07",
                budget=3000.0,
                travelers=2
            )
    
    def test_travel_request_validation_invalid_dates(self):
        """Test TravelRequest model with invalid date logic"""
        past_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        future_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        
        with pytest.raises(ValueError, match="Start date must be in the future"):
            TravelRequest(
                destination="Tokyo, Japan",
                start_date=past_date,
                end_date=future_date,
                budget=3000.0,
                travelers=2
            )
    
    def test_travel_request_validation_end_before_start(self):
        """Test TravelRequest model with end date before start date"""
        date1 = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        date2 = (datetime.now() + timedelta(days=25)).strftime("%Y-%m-%d")
        
        with pytest.raises(ValueError, match="End date must be after start date"):
            TravelRequest(
                destination="Tokyo, Japan",
                start_date=date1,
                end_date=date2,  # Before start date
                budget=3000.0,
                travelers=2
            )
    
    def test_travel_request_validation_negative_budget(self):
        """Test TravelRequest model with negative budget"""
        future_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        future_end_date = (datetime.now() + timedelta(days=37)).strftime("%Y-%m-%d")
        
        with pytest.raises(ValueError):
            TravelRequest(
                destination="Tokyo, Japan",
                start_date=future_date,
                end_date=future_end_date,
                budget=-1000.0,  # Negative budget
                travelers=2
            )
    
    def test_travel_request_validation_invalid_travelers(self):
        """Test TravelRequest model with invalid number of travelers"""
        future_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        future_end_date = (datetime.now() + timedelta(days=37)).strftime("%Y-%m-%d")
        
        with pytest.raises(ValueError):
            TravelRequest(
                destination="Tokyo, Japan",
                start_date=future_date,
                end_date=future_end_date,
                budget=3000.0,
                travelers=0  # Invalid number
            )
    
    def test_validation_result_model(self):
        """Test ValidationResult model"""
        validation = ValidationResult(
            is_valid=False,
            errors=["Invalid date"],
            warnings=["Budget might be tight"],
            suggestions=["Consider extending stay"]
        )
        
        assert validation.is_valid is False
        assert len(validation.errors) == 1
        assert len(validation.warnings) == 1
        assert len(validation.suggestions) == 1
        assert validation.confidence_score == 1.0  # default value


class TestIntegration:
    """Integration tests combining multiple components"""
    
    @pytest.mark.asyncio
    async def test_full_pipeline_mock(self):
        """Test the full pipeline with mock data"""
        orchestrator = LLMOrchestrator()
        orchestrator.llm = None  # Force fallback parsing
        
        request = "Plan a week-long trip to Paris for 2 people with $4000 budget"
        result = await orchestrator.process_request(request)
        
        # Should succeed with mock data
        assert result["status"] == "success"
        assert result["parsed_request"]["destination"] is not None
        assert result["parsed_request"]["budget"] > 0
        assert result["validation"]["is_valid"] is True
        assert result["agent_results"]["coordination_status"] == "completed"
    
    @pytest.mark.asyncio
    async def test_fetch_travel_data_convenience_function(self):
        """Test the convenience function for fetching travel data"""
        result = await fetch_travel_data("Tokyo")
        
        assert "status" in result
        assert "destination" in result
        assert "weather" in result
        assert "flights" in result
        assert "hotels" in result
        assert "currency" in result


# Test runner configuration
if __name__ == "__main__":
    # Run specific tests
    pytest.main([__file__, "-v", "--tb=short"])