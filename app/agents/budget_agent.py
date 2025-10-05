"""
Budget Optimization Agent

This agent optimizes budget allocation across different travel categories
while balancing cost vs convenience trade-offs.
"""

from typing import Dict, Any, List, Optional, Tuple
import json
from datetime import datetime

from app.core.config import get_settings
from app.core.logging_config import get_logger

settings = get_settings()
logger = get_logger(__name__)


class BudgetAgent:
    """Agent for budget optimization and cost management"""
    
    def __init__(self):
        self.settings = settings
        self.logger = logger
        
        # Default budget allocation percentages
        self.default_allocation = {
            "flights": 0.35,      # 35% for flights
            "accommodation": 0.30, # 30% for hotels
            "activities": 0.20,    # 20% for activities/attractions
            "food": 0.10,         # 10% for food
            "transport": 0.03,     # 3% for local transport
            "contingency": 0.02    # 2% for unexpected expenses
        }
        
        # Cost ranges by category (USD per day estimates)
        self.cost_ranges = {
            "budget": {
                "accommodation": (30, 80),
                "food": (25, 50),
                "activities": (15, 40),
                "transport": (5, 15)
            },
            "mid-range": {
                "accommodation": (80, 200),
                "food": (50, 100),
                "activities": (40, 100),
                "transport": (15, 40)
            },
            "luxury": {
                "accommodation": (200, 500),
                "food": (100, 250),
                "activities": (100, 300),
                "transport": (40, 100)
            }
        }
    
    async def analyze_budget_feasibility(
        self, 
        total_budget: float, 
        destination: str, 
        duration_days: int,
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze if budget is feasible for the trip"""
        self.logger.info("Analyzing budget feasibility", 
                        budget=total_budget, destination=destination, duration=duration_days)
        
        # Determine budget category based on daily budget
        daily_budget = total_budget / duration_days if duration_days > 0 else total_budget
        
        if daily_budget < 100:
            budget_category = "budget"
        elif daily_budget < 300:
            budget_category = "mid-range"
        else:
            budget_category = "luxury"
        
        # Get cost estimates for destination
        cost_estimates = self._get_destination_costs(destination, budget_category)
        
        # Calculate minimum required budget
        min_daily_cost = sum(cost_estimates[cat][0] for cat in cost_estimates)
        min_total_cost = min_daily_cost * duration_days
        
        # Analyze feasibility
        feasibility_ratio = total_budget / min_total_cost if min_total_cost > 0 else 1.0
        
        analysis = {
            "is_feasible": feasibility_ratio >= 0.8,
            "budget_category": budget_category,
            "daily_budget": daily_budget,
            "min_daily_cost": min_daily_cost,
            "min_total_cost": min_total_cost,
            "feasibility_ratio": feasibility_ratio,
            "cost_estimates": cost_estimates,
            "recommendations": []
        }
        
        # Add recommendations based on analysis
        if feasibility_ratio < 0.8:
            analysis["recommendations"].append(
                f"Consider increasing budget by ${min_total_cost - total_budget:.0f}"
            )
            analysis["recommendations"].append("Look for budget accommodation options")
            analysis["recommendations"].append("Consider cooking some meals")
        elif feasibility_ratio > 1.5:
            analysis["recommendations"].append("You have room for upgrades!")
            analysis["recommendations"].append("Consider premium experiences")
        
        return analysis
    
    def _get_destination_costs(self, destination: str, budget_category: str) -> Dict[str, Tuple[float, float]]:
        """Get cost estimates for specific destination"""
        # TODO: Implement destination-specific cost data
        # This would typically come from a database or external API
        
        base_costs = self.cost_ranges[budget_category]
        
        # Apply destination multipliers (placeholder)
        destination_multipliers = {
            "paris": 1.3,
            "tokyo": 1.4,
            "bangkok": 0.6,
            "new york": 1.5,
            "mumbai": 0.4,
            "london": 1.4,
            "default": 1.0
        }
        
        multiplier = destination_multipliers.get(
            destination.lower().split(",")[0], 
            destination_multipliers["default"]
        )
        
        adjusted_costs = {}
        for category, (min_cost, max_cost) in base_costs.items():
            adjusted_costs[category] = (min_cost * multiplier, max_cost * multiplier)
        
        return adjusted_costs
    
    async def optimize_allocation(
        self,
        total_budget: float,
        preferences: Dict[str, Any],
        trip_context: Dict[str, Any],
        constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Optimize budget allocation across categories"""
        self.logger.info("Optimizing budget allocation", budget=total_budget)
        
        # Start with default allocation
        allocation = self.default_allocation.copy()
        
        # Adjust based on preferences
        allocation = self._adjust_for_preferences(allocation, preferences)
        
        # Adjust based on trip context
        allocation = self._adjust_for_context(allocation, trip_context)
        
        # Apply constraints if any
        if constraints:
            allocation = self._apply_constraints(allocation, constraints)
        
        # Calculate actual amounts
        budget_plan = {}
        for category, percentage in allocation.items():
            budget_plan[category] = {
                "allocated": total_budget * percentage,
                "percentage": percentage * 100,
                "daily_amount": (total_budget * percentage) / trip_context.get("duration_days", 1)
            }
        
        # Calculate optimization score
        optimization_score = self._calculate_optimization_score(allocation, preferences, trip_context)
        
        result = {
            "status": "success",
            "total_budget": total_budget,
            "allocation_percentages": {k: v * 100 for k, v in allocation.items()},
            "budget_plan": budget_plan,
            "optimization_score": optimization_score,
            "optimization_factors": {
                "preference_alignment": 0.85,
                "cost_efficiency": 0.78,
                "flexibility": 0.90
            }
        }
        
        return result
    
    def _adjust_for_preferences(self, allocation: Dict[str, float], preferences: Dict[str, Any]) -> Dict[str, float]:
        """Adjust allocation based on user preferences"""
        adjusted = allocation.copy()
        
        # Accommodation preference adjustments
        if preferences.get("accommodation_importance") == "high":
            adjusted["accommodation"] += 0.05
            adjusted["activities"] -= 0.03
            adjusted["food"] -= 0.02
        
        # Food preference adjustments
        if preferences.get("food_importance") == "high":
            adjusted["food"] += 0.05
            adjusted["activities"] -= 0.03
            adjusted["accommodation"] -= 0.02
        
        # Activity preference adjustments
        if preferences.get("activity_importance") == "high":
            adjusted["activities"] += 0.05
            adjusted["accommodation"] -= 0.03
            adjusted["food"] -= 0.02
        
        # Ensure allocations sum to 1.0
        total = sum(adjusted.values())
        for key in adjusted:
            adjusted[key] = adjusted[key] / total
        
        return adjusted
    
    def _adjust_for_context(self, allocation: Dict[str, float], context: Dict[str, Any]) -> Dict[str, float]:
        """Adjust allocation based on trip context"""
        adjusted = allocation.copy()
        
        # Trip type adjustments
        trip_type = context.get("trip_type", "leisure")
        
        if trip_type == "business":
            # Business trips: prioritize accommodation and transport
            adjusted["accommodation"] += 0.05
            adjusted["transport"] += 0.02
            adjusted["activities"] -= 0.05
            adjusted["food"] -= 0.02
        
        elif trip_type == "adventure":
            # Adventure trips: prioritize activities
            adjusted["activities"] += 0.08
            adjusted["accommodation"] -= 0.05
            adjusted["food"] -= 0.03
        
        elif trip_type == "relaxation":
            # Relaxation trips: prioritize accommodation
            adjusted["accommodation"] += 0.08
            adjusted["activities"] -= 0.05
            adjusted["transport"] -= 0.03
        
        # Duration adjustments
        duration = context.get("duration_days", 5)
        if duration > 10:
            # Longer trips: reduce flight percentage, increase others
            adjusted["flights"] -= 0.05
            adjusted["accommodation"] += 0.02
            adjusted["food"] += 0.02
            adjusted["activities"] += 0.01
        
        # Ensure allocations sum to 1.0
        total = sum(adjusted.values())
        for key in adjusted:
            adjusted[key] = adjusted[key] / total
        
        return adjusted
    
    def _apply_constraints(self, allocation: Dict[str, float], constraints: Dict[str, Any]) -> Dict[str, float]:
        """Apply hard constraints to allocation"""
        adjusted = allocation.copy()
        
        # Maximum/minimum constraints
        for category, limits in constraints.items():
            if category in adjusted:
                if "max_percentage" in limits:
                    adjusted[category] = min(adjusted[category], limits["max_percentage"] / 100)
                if "min_percentage" in limits:
                    adjusted[category] = max(adjusted[category], limits["min_percentage"] / 100)
        
        # Ensure allocations sum to 1.0 after constraints
        total = sum(adjusted.values())
        for key in adjusted:
            adjusted[key] = adjusted[key] / total
        
        return adjusted
    
    def _calculate_optimization_score(
        self, 
        allocation: Dict[str, float], 
        preferences: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> float:
        """Calculate how well the allocation matches preferences and context"""
        # TODO: Implement sophisticated scoring algorithm
        # For now, return a placeholder score
        return 0.85
    
    async def compare_options(
        self,
        options: List[Dict[str, Any]],
        budget_limit: float,
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compare different travel options against budget and preferences"""
        self.logger.info("Comparing travel options", num_options=len(options), budget_limit=budget_limit)
        
        scored_options = []
        
        for i, option in enumerate(options):
            # Calculate cost score (lower cost = higher score)
            cost = option.get("total_cost", 0)
            cost_score = max(0, (budget_limit - cost) / budget_limit) if budget_limit > 0 else 0
            
            # Calculate value score (placeholder)
            value_score = option.get("rating", 3.0) / 5.0
            
            # Calculate preference alignment score (placeholder)
            preference_score = 0.7  # Would be computed based on actual preferences
            
            # Overall score
            overall_score = (cost_score * 0.4 + value_score * 0.3 + preference_score * 0.3)
            
            scored_options.append({
                "option_id": i,
                "option": option,
                "scores": {
                    "cost_score": cost_score,
                    "value_score": value_score,
                    "preference_score": preference_score,
                    "overall_score": overall_score
                },
                "within_budget": cost <= budget_limit
            })
        
        # Sort by overall score
        scored_options.sort(key=lambda x: x["scores"]["overall_score"], reverse=True)
        
        return {
            "status": "success",
            "budget_limit": budget_limit,
            "options_analyzed": len(options),
            "ranked_options": scored_options,
            "best_option": scored_options[0] if scored_options else None,
            "budget_utilization": scored_options[0]["option"].get("total_cost", 0) / budget_limit if scored_options and budget_limit > 0 else 0
        }