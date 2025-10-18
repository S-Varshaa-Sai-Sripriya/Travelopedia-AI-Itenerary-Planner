"""
LLM Orchestrator Agent

This agent is responsible for:
- Parsing user travel requests using local LLM (Ollama)
- Coordinating with other agents
- Intent recognition and reasoning
- Mitigating LLM hallucinations through structured output
"""

import asyncio
from typing import Dict, Any, List, Optional
import json
from datetime import datetime, timedelta
import re
import ollama
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from app.core.config import get_settings
from app.core.logging_config import get_logger
from app.models.travel_request import (
    TravelRequest, ValidationResult, TravelPlanResponse, 
    AgentResults, GNNRecommendations, BudgetOptimization, ItineraryGeneration
)
from app.models.travel_request import (
    TravelRequest, ValidationResult, TravelPlanResponse, 
    AgentResults, GNNRecommendations, BudgetOptimization, ItineraryGeneration
)

settings = get_settings()
logger = get_logger(__name__)


class LLMOrchestrator:
    """Main orchestrator agent that coordinates all other agents"""
    
    def __init__(self):
        self.settings = settings
        self.logger = logger
        
        # Initialize Ollama client
        try:
            self.ollama_client = ollama.Client(host=settings.OLLAMA_BASE_URL)
            # Test connection
            models = self.ollama_client.list()
            available_models = [model.model for model in models.models]
            self.logger.info(f"Ollama connected successfully. Available models: {available_models}")
            
            # Use llama2 if available, otherwise use the first available model
            if "llama2:7b" in available_models:
                self.model_name = "llama2:7b"
            elif available_models:
                self.model_name = available_models[0]
            else:
                raise Exception("No Ollama models available")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize Ollama client: {e}")
            self.ollama_client = None
            self.model_name = None
        
        # Initialize LangChain Ollama
        if self.model_name:
            self.llm = ChatOllama(
                model=self.model_name,
                base_url=settings.OLLAMA_BASE_URL,
                temperature=0.1  # Low temperature for consistent parsing
            )
        
    async def parse_travel_request(self, request: str) -> Dict[str, Any]:
        """Parse natural language travel request into structured data using Ollama"""
        self.logger.info("Parsing travel request with Ollama", request_preview=request[:100])
        
        if not self.llm:
            self.logger.error("Ollama LLM not available, using fallback parsing")
            return await self._fallback_parsing(request)
        
        try:
            # Create a structured prompt for travel request parsing
            parser = JsonOutputParser(pydantic_object=TravelRequest)
            
            prompt = ChatPromptTemplate.from_template(
                """
                You are a travel planning expert. Extract travel information from the user's request and return it as valid JSON.
                
                User Request: {request}
                
                Extract the following information:
                - destination: The city, country, or region they want to visit
                - start_date: Start date (format: YYYY-MM-DD, if not specified use a reasonable future date)
                - end_date: End date (format: YYYY-MM-DD, calculate based on duration or assume 7 days)
                - budget: Total budget in USD (if not specified, estimate based on destination and duration)
                - travelers: Number of people traveling (default to 1 if not specified)
                - trip_type: Type of trip (leisure, business, adventure, honeymoon, family, etc.)
                - preferences: Object with accommodation, transport, activities, food preferences
                - constraints: Object with dietary restrictions, accessibility needs, special requirements
                
                If information is missing, make reasonable assumptions based on the destination and context.
                
                {format_instructions}
                
                Return only valid JSON without any additional text or explanation.
                """
            )
            
            chain = prompt | self.llm | parser
            
            result = await asyncio.to_thread(
                chain.invoke,
                {
                    "request": request,
                    "format_instructions": parser.get_format_instructions()
                }
            )
            
            self.logger.info("Successfully parsed travel request", destination=result.get("destination"))
            return result
            
        except Exception as e:
            self.logger.error(f"Error parsing with Ollama: {e}")
            return await self._fallback_parsing(request)
    
    async def _fallback_parsing(self, request: str) -> Dict[str, Any]:
        """Fallback parsing using regex and heuristics"""
        self.logger.info("Using fallback parsing method")
        
        # Simple regex-based extraction
        destination_match = re.search(r'(?:to|visit|go to|travel to)\s+([A-Za-z\s,]+?)(?:\s|$|,|\.|!|\?)', request, re.IGNORECASE)
        budget_match = re.search(r'\$?(\d{1,5})\s*(?:dollars?|USD|budget)', request, re.IGNORECASE)
        travelers_match = re.search(r'(\d+)\s*(?:people|person|travelers?|adults?)', request, re.IGNORECASE)
        
        # Calculate dates
        today = datetime.now()
        start_date = (today + timedelta(days=30)).strftime("%Y-%m-%d")  # Default to 30 days from now
        end_date = (today + timedelta(days=37)).strftime("%Y-%m-%d")    # 7-day trip
        
        parsed_request = {
            "destination": destination_match.group(1).strip() if destination_match else "Paris, France",
            "start_date": start_date,
            "end_date": end_date,
            "budget": float(budget_match.group(1)) if budget_match else 2000.0,
            "currency": "USD",
            "travelers": int(travelers_match.group(1)) if travelers_match else 1,
            "trip_type": "leisure",
            "preferences": {
                "accommodation": "hotel",
                "transport": "flight",
                "activities": ["sightseeing", "museums", "restaurants"],
                "food": "local cuisine"
            },
            "constraints": {
                "dietary": [],
                "accessibility": [],
                "special_requirements": []
            }
        }
        
        return parsed_request
    
    async def validate_constraints(self, parsed_request: Dict[str, Any]) -> Dict[str, Any]:
        """Validate hard constraints and feasibility"""
        validation_result = ValidationResult(is_valid=True)
        
        try:
            # Validate dates
            start_date = datetime.strptime(parsed_request.get("start_date", ""), "%Y-%m-%d")
            end_date = datetime.strptime(parsed_request.get("end_date", ""), "%Y-%m-%d")
            
            if start_date <= datetime.now():
                validation_result.errors.append("Start date must be in the future")
                validation_result.is_valid = False
            
            if end_date <= start_date:
                validation_result.errors.append("End date must be after start date")
                validation_result.is_valid = False
            
            # Validate budget
            budget = parsed_request.get("budget", 0)
            if budget < 100:
                validation_result.errors.append("Budget too low for international travel")
                validation_result.is_valid = False
            elif budget < 1000:
                validation_result.warnings.append("Budget might be tight for the selected destination")
            
            # Validate travelers
            travelers = parsed_request.get("travelers", 1)
            if travelers < 1 or travelers > 20:
                validation_result.errors.append("Invalid number of travelers")
                validation_result.is_valid = False
            
            # Add suggestions
            duration = (end_date - start_date).days
            if duration > 14:
                validation_result.suggestions.append("Consider breaking long trips into multiple shorter ones")
            elif duration < 3:
                validation_result.suggestions.append("Consider extending stay for better value")
                
        except ValueError as e:
            validation_result.errors.append(f"Invalid date format: {e}")
            validation_result.is_valid = False
        
        return validation_result.model_dump()
    
    async def coordinate_agents(self, parsed_request: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate all agents to process the travel request"""
        self.logger.info("Coordinating agents for travel request")
        
        # TODO: Implement actual agent coordination in subsequent phases
        # 1. Call GNN Agent for personalized recommendations
        # 2. Call Budget Agent for optimization
        # 3. Call Itinerary Agent for final assembly
        # 4. Validate results and handle conflicts
        
        coordination_result = {
            "gnn_recommendations": await self._mock_gnn_call(parsed_request),
            "budget_optimization": await self._mock_budget_call(parsed_request),
            "itinerary_generation": await self._mock_itinerary_call(parsed_request),
            "coordination_status": "completed",
            "processing_time": 45.2  # seconds
        }
        
        return coordination_result
    
    async def _mock_gnn_call(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Mock GNN agent call - to be replaced in Phase 2"""
        await asyncio.sleep(1)  # Simulate processing time
        destination = request.get("destination", "Unknown")
        return {
            "personalization_score": 0.87,
            "recommendations": [
                f"Luxury hotel in {destination}",
                f"Highly rated restaurant near {destination}",
                f"Popular museum in {destination}"
            ],
            "reasoning": "Based on user preferences and historical data"
        }
    
    async def _mock_budget_call(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Mock Budget agent call - to be replaced in Phase 2"""
        await asyncio.sleep(1)  # Simulate processing time
        budget = request.get("budget", 2000)
        travelers = request.get("travelers", 1)
        
        return {
            "optimization_score": 0.92,
            "budget_allocation": {
                "flights": budget * 0.3,
                "accommodation": budget * 0.4,
                "activities": budget * 0.2,
                "food": budget * 0.1
            },
            "cost_per_person": budget / travelers,
            "savings_opportunities": ["Book flights 6 weeks in advance", "Consider mid-week travel"]
        }
    
    async def _mock_itinerary_call(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Mock Itinerary agent call - to be replaced in Phase 2"""
        await asyncio.sleep(2)  # Simulate processing time
        start_date = request.get("start_date", "2024-03-15")
        end_date = request.get("end_date", "2024-03-20")
        destination = request.get("destination", "Unknown")
        
        return {
            "itinerary_confidence": 0.89,
            "daily_schedule": [
                f"Day 1 ({start_date}): Arrival in {destination}",
                f"Day 2: City tour and landmark visits",
                f"Day 3: Museum and cultural experiences",
                f"Day 4: Adventure activities and local cuisine",
                f"Day 5 ({end_date}): Departure preparation"
            ],
            "bookings_required": ["Flight", "Hotel", "Museum tickets"],
            "estimated_timeline": "5 days"
        }
    
    async def process_request(self, user_request: str) -> Dict[str, Any]:
        """Main entry point for processing travel requests with enhanced LLM capabilities"""
        try:
            self.logger.info("Starting enhanced travel request processing")
            
            # Step 1: Parse the request using Ollama
            parsed_request = await self.parse_travel_request(user_request)
            
            # Step 2: Validate constraints
            validation = await self.validate_constraints(parsed_request)
            
            if not validation["is_valid"]:
                return {
                    "status": "error",
                    "errors": validation["errors"],
                    "suggestions": validation.get("suggestions", []),
                    "parsed_request": parsed_request
                }
            
            # Step 3: Coordinate agents
            coordination_result = await self.coordinate_agents(parsed_request)
            
            # Step 4: Compile final response
            final_response = {
                "status": "success",
                "parsed_request": parsed_request,
                "validation": validation,
                "agent_results": coordination_result,
                "llm_model_used": self.model_name,
                "timestamp": datetime.utcnow().isoformat(),
                "processing_complete": True
            }
            
            self.logger.info("Enhanced travel request processing completed successfully")
            return final_response
            
        except Exception as e:
            self.logger.error("Error processing travel request", error=str(e))
            return {
                "status": "error",
                "message": "Failed to process travel request",
                "error": str(e),
                "llm_available": self.ollama_client is not None
            }