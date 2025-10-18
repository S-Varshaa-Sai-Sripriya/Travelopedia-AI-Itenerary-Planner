"""
User Profile Modeling System

This module handles user profiling for personalized travel recommendations using:
- Demographic features
- Travel history analysis
- Preference learning
- Behavioral patterns
- Feature vector generation for GNN input
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.decomposition import PCA
import torch

from app.core.logging_config import get_logger
from app.core.config import get_settings

logger = get_logger(__name__)
settings = get_settings()


class TravelPersonality(str, Enum):
    """Travel personality types for clustering"""
    EXPLORER = "explorer"           # Seeks new experiences, off-the-beaten-path
    RELAXER = "relaxer"            # Prefers comfort, relaxation, luxury
    ADVENTURER = "adventurer"      # High-energy activities, extreme sports
    CULTURAL = "cultural"          # Museums, history, local culture
    SOCIAL = "social"              # Group activities, nightlife, social events
    FAMILY = "family"              # Family-friendly, safe, educational
    BUDGET = "budget"              # Cost-conscious, value optimization
    LUXURY = "luxury"              # Premium experiences, high-end services


class ActivityPreference(str, Enum):
    """Activity categories for preference modeling"""
    OUTDOOR = "outdoor"
    CULTURAL = "cultural"
    CULINARY = "culinary"
    ADVENTURE = "adventure"
    RELAXATION = "relaxation"
    NIGHTLIFE = "nightlife"
    SHOPPING = "shopping"
    EDUCATIONAL = "educational"
    SPORTS = "sports"
    PHOTOGRAPHY = "photography"


@dataclass
class UserDemographics:
    """User demographic information"""
    age: Optional[int] = None
    gender: Optional[str] = None
    income_bracket: Optional[str] = None  # low, middle, high, luxury
    location: Optional[str] = None
    occupation: Optional[str] = None
    education_level: Optional[str] = None
    family_status: Optional[str] = None  # single, couple, family, group
    travel_frequency: Optional[str] = None  # occasional, regular, frequent


@dataclass
class TravelPreferences:
    """Detailed travel preferences"""
    personality_type: Optional[TravelPersonality] = None
    preferred_destinations: List[str] = field(default_factory=list)
    avoided_destinations: List[str] = field(default_factory=list)
    accommodation_types: List[str] = field(default_factory=list)
    transport_preferences: List[str] = field(default_factory=list)
    activity_preferences: Dict[ActivityPreference, float] = field(default_factory=dict)
    cuisine_preferences: List[str] = field(default_factory=list)
    budget_range: Tuple[float, float] = (0.0, 10000.0)
    trip_duration_preference: Tuple[int, int] = (3, 14)  # days
    season_preferences: List[str] = field(default_factory=list)
    group_size_preference: Tuple[int, int] = (1, 4)


@dataclass
class TravelHistory:
    """User's travel history for pattern analysis"""
    destinations_visited: List[str] = field(default_factory=list)
    trip_ratings: List[float] = field(default_factory=list)
    trip_types: List[str] = field(default_factory=list)
    spending_patterns: List[float] = field(default_factory=list)
    booking_lead_times: List[int] = field(default_factory=list)  # days in advance
    travel_companions: List[str] = field(default_factory=list)
    seasons_traveled: List[str] = field(default_factory=list)
    feedback_scores: Dict[str, List[float]] = field(default_factory=dict)


class UserProfileModeler:
    """Main class for user profile modeling and feature extraction"""
    
    def __init__(self):
        self.logger = logger
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_dim = 128  # Standard feature vector dimension for GNN
        
    def create_user_profile(
        self, 
        user_id: str,
        demographics: Optional[UserDemographics] = None,
        preferences: Optional[TravelPreferences] = None,
        history: Optional[TravelHistory] = None
    ) -> Dict[str, Any]:
        """Create comprehensive user profile"""
        
        profile = {
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "demographics": demographics or UserDemographics(),
            "preferences": preferences or TravelPreferences(),
            "history": history or TravelHistory(),
            "computed_features": {},
            "personality_scores": {},
            "similarity_clusters": []
        }
        
        # Compute derived features
        profile["computed_features"] = self._compute_derived_features(profile)
        profile["personality_scores"] = self._compute_personality_scores(profile)
        
        self.logger.info(f"Created user profile for {user_id}")
        return profile
    
    def generate_feature_vector(self, user_profile: Dict[str, Any]) -> torch.Tensor:
        """Generate feature vector for GNN input"""
        
        features = []
        
        # Handle both dict and dataclass formats
        if isinstance(user_profile, dict):
            # Dict format - adapt key names
            # Demographic features (20 dimensions)
            demo_features = self._encode_demographics(user_profile.get("demographics", {}))
            features.extend(demo_features)
            
            # Preference features (40 dimensions)
            pref_features = self._encode_preferences(user_profile.get("travel_preferences", {}))
            features.extend(pref_features)
            
            # History features (20 dimensions)
            hist_features = self._encode_history(user_profile.get("travel_history", {}))
            features.extend(hist_features)
            
            # Interest/lifestyle features (28 dimensions)
            interest_features = self._encode_interests_lifestyle(user_profile.get("interests_and_lifestyle", {}))
            features.extend(interest_features)
            
            # Social/behavioral features (12 dimensions)
            social_features = self._encode_social_behavioral(user_profile.get("social_and_behavioral", {}))
            features.extend(social_features)
            
        else:
            # Dataclass format (original logic)
            # Demographic features (20 dimensions)
            demo_features = self._encode_demographics(user_profile.demographics)
            features.extend(demo_features)
            
            # Preference features (40 dimensions)
            pref_features = self._encode_preferences(user_profile.preferences)
            features.extend(pref_features)
            
            # History features (20 dimensions)
            hist_features = self._encode_history(user_profile.history)
            features.extend(hist_features)
            
            # Interest/lifestyle features (28 dimensions)
            interest_features = self._encode_interests_lifestyle(user_profile.interests_lifestyle)
            features.extend(interest_features)
            
            # Social/behavioral features (12 dimensions)
            social_features = self._encode_social_behavioral(user_profile.social_behavioral)
            features.extend(social_features)
        
        # Ensure feature vector is exactly 128 dimensions
        target_dim = 128
        if len(features) < target_dim:
            # Pad with neutral values
            features.extend([0.5] * (target_dim - len(features)))
        elif len(features) > target_dim:
            # Truncate
            features = features[:target_dim]
        
        return torch.tensor(features, dtype=torch.float32)
        
        # Personality features (18 dimensions - 8 personality types + 10 activity preferences)
        pers_features = self._encode_personality(user_profile["personality_scores"])
        features.extend(pers_features)
        
        # Pad or truncate to standard dimension
        if len(features) < self.feature_dim:
            features.extend([0.0] * (self.feature_dim - len(features)))
        elif len(features) > self.feature_dim:
            features = features[:self.feature_dim]
        
        return torch.tensor(features, dtype=torch.float32)
    
    def _encode_demographics(self, demographics) -> List[float]:
        """Encode demographic information into feature vector"""
        features = []
        
        # Handle both dataclass and dictionary formats
        if isinstance(demographics, dict):
            age = demographics.get('age', 30)
            gender = demographics.get('gender', 'other')
            income_level = demographics.get('income_level', 'middle')
            nationality = demographics.get('nationality', 'unknown')
        else:
            # Assuming dataclass format
            age = demographics.age or 30
            gender = demographics.gender or 'other'
            income_level = getattr(demographics, 'income_level', getattr(demographics, 'income_bracket', 'middle'))
            nationality = getattr(demographics, 'nationality', 'unknown')
        
        # Age normalization (0-100 years -> 0-1)
        features.append(age / 100.0)
        
        # Gender encoding (one-hot style)
        gender_map = {"male": 1.0, "female": 0.0, "other": 0.5}
        features.append(gender_map.get(gender, 0.25))
        
        # Income bracket encoding
        income_map = {"low": 0.2, "mid": 0.5, "middle": 0.5, "high": 0.8, "luxury": 1.0}
        features.append(income_map.get(income_level, 0.5))
        
        # Travel frequency encoding (use default for dict format)
        travel_frequency = 'regular' if isinstance(demographics, dict) else getattr(demographics, 'travel_frequency', 'regular')
        frequency_map = {"occasional": 0.25, "regular": 0.5, "frequent": 0.75, "business": 1.0}
        features.append(frequency_map.get(travel_frequency, 0.4))
        
        # Family status encoding (use default for dict format)
        family_status = 'single' if isinstance(demographics, dict) else getattr(demographics, 'family_status', 'single')
        family_map = {"single": 0.2, "couple": 0.5, "family": 0.8, "group": 1.0}
        features.append(family_map.get(family_status, 0.5))
        
        # Add 15 more demographic features (occupation, education, etc.)
        # For now, using placeholder values - these would be expanded based on real data
        features.extend([0.5] * 15)
        
        return features
    
    def _encode_preferences(self, preferences) -> List[float]:
        """Encode travel preferences into feature vector"""
        features = []
        
        # Handle both dict and dataclass formats
        if isinstance(preferences, dict):
            # Dict format handling
            budget_range = preferences.get('budget_range', 'mid')
            travel_style = preferences.get('travel_style', 'cultural')
            accommodation_type = preferences.get('accommodation_type', 'hotel')
            preferred_activities = preferences.get('preferred_activities', [])
            
            # Budget preference mapping
            budget_map = {"budget": 0.2, "mid": 0.5, "luxury": 0.8, "premium": 1.0}
            features.append(budget_map.get(budget_range, 0.5))
            
            # Travel style mapping
            style_map = {"adventure": 0.2, "cultural": 0.4, "relaxation": 0.6, "luxury": 0.8, "business": 1.0}
            features.append(style_map.get(travel_style, 0.5))
            
            # Accommodation type
            accom_map = {"hostel": 0.2, "hotel": 0.5, "resort": 0.8, "villa": 1.0}
            features.append(accom_map.get(accommodation_type, 0.5))
            
            # Activity preferences (simplified for dict format)
            activity_categories = ['culture', 'food', 'adventure', 'relaxation', 'nightlife', 'nature', 'shopping', 'art', 'history', 'sports']
            for activity in activity_categories:
                score = 1.0 if activity in preferred_activities else 0.0
                features.append(score)
            
            # Add padding features to match expected dimensions
            features.extend([0.5] * 20)
            
        else:
            # Dataclass format handling (original logic)
            # Personality type encoding
            personality_map = {p.value: i/len(TravelPersonality) for i, p in enumerate(TravelPersonality)}
            pers_score = personality_map.get(preferences.personality_type, 0.5) if preferences.personality_type else 0.5
            features.append(pers_score)
            
            # Budget preference (log scale normalization)
            budget_min, budget_max = preferences.budget_range
            budget_log = np.log(max(budget_max, 1)) / np.log(50000)  # Normalize to 0-1
            features.append(min(budget_log, 1.0))
            
            # Trip duration preference
            duration_avg = sum(preferences.trip_duration_preference) / 2.0
            features.append(duration_avg / 30.0)  # Normalize to 0-1 (max 30 days)
            
            # Activity preferences (10 dimensions for each activity type)
            for activity in ActivityPreference:
                score = preferences.activity_preferences.get(activity, 0.5)
                features.append(score)
            
            # Group size preference
            group_avg = sum(preferences.group_size_preference) / 2.0
            features.append(group_avg / 10.0)  # Normalize to 0-1 (max 10 people)
            
            # Destination diversity (based on number of preferred destinations)
            dest_diversity = min(len(preferences.preferred_destinations) / 20.0, 1.0)
            features.append(dest_diversity)
        
        # Add remaining preference features
        remaining_features = 40 - len(features)
        features.extend([0.5] * remaining_features)
        
        return features
    
    def _encode_history(self, history) -> List[float]:
        """Encode travel history into feature vector"""
        features = []
        
        # Handle both dict and dataclass formats
        if isinstance(history, dict):
            # Dict format handling
            previous_destinations = history.get('previous_destinations', [])
            total_trips = history.get('total_trips', 0)
            avg_trip_duration = history.get('avg_trip_duration', 7)
            preferred_season = history.get('preferred_season', 'spring')
            
            # Travel experience (number of trips)
            experience = min(total_trips / 50.0, 1.0)
            features.append(experience)
            
            # Number of destinations visited
            dest_count = min(len(previous_destinations) / 20.0, 1.0)
            features.append(dest_count)
            
            # Average trip duration
            duration_norm = min(avg_trip_duration / 30.0, 1.0)
            features.append(duration_norm)
            
            # Preferred season encoding
            season_map = {"spring": 0.25, "summer": 0.5, "autumn": 0.75, "winter": 1.0}
            features.append(season_map.get(preferred_season, 0.5))
            
            # Add padding features
            features.extend([0.5] * 16)
            
        else:
            # Dataclass format handling (original logic)
            # Travel experience (number of trips)
            experience = min(len(history.destinations_visited) / 50.0, 1.0)
            features.append(experience)
            
            # Average trip rating
            avg_rating = np.mean(history.trip_ratings) / 5.0 if history.trip_ratings else 0.5
            features.append(avg_rating)
            
            # Spending pattern (average spending normalized)
            avg_spending = np.mean(history.spending_patterns) if history.spending_patterns else 2000
            spending_norm = min(np.log(avg_spending) / np.log(50000), 1.0)
            features.append(spending_norm)
            
            # Booking lead time pattern
            avg_lead_time = np.mean(history.booking_lead_times) if history.booking_lead_times else 30
            lead_time_norm = min(avg_lead_time / 365.0, 1.0)  # Normalize to 0-1 (max 1 year)
            features.append(lead_time_norm)
            
            # Destination diversity in history
            unique_destinations = len(set(history.destinations_visited))
            dest_diversity = min(unique_destinations / 30.0, 1.0)
            features.append(dest_diversity)
            
            # Trip type variety
            unique_trip_types = len(set(history.trip_types))
            type_diversity = min(unique_trip_types / 10.0, 1.0)
            features.append(type_diversity)
            
            # Seasonal travel pattern (4 seasons)
            season_counts = {"spring": 0, "summer": 0, "fall": 0, "winter": 0}
            for season in history.seasons_traveled:
                if season in season_counts:
                    season_counts[season] += 1
            
            total_trips = len(history.seasons_traveled) or 1
            for season in ["spring", "summer", "fall", "winter"]:
                features.append(season_counts[season] / total_trips)
        
        # Add remaining history features to reach target dimension
        remaining_features = 20 - len(features)
        features.extend([0.5] * remaining_features)
        
        return features
    
    def _encode_interests_lifestyle(self, interests_lifestyle) -> List[float]:
        """Encode interests and lifestyle into feature vector"""
        features = []
        
        # Handle both dict and dataclass formats
        if isinstance(interests_lifestyle, dict):
            # Dict format handling
            interests = interests_lifestyle.get('interests', [])
            dietary_restrictions = interests_lifestyle.get('dietary_restrictions', [])
            accessibility_needs = interests_lifestyle.get('accessibility_needs', [])
            
            # Interest categories encoding
            interest_categories = ['culture', 'food', 'adventure', 'relaxation', 'nightlife', 'nature', 'shopping', 'art', 'history', 'sports', 'technology', 'wellness']
            for category in interest_categories:
                score = 1.0 if category in interests else 0.0
                features.append(score)
            
            # Dietary restrictions encoding
            diet_types = ['vegetarian', 'vegan', 'halal', 'kosher', 'gluten_free', 'none']
            for diet_type in diet_types:
                score = 1.0 if diet_type in dietary_restrictions else 0.0
                features.append(score)
            
            # Accessibility needs encoding
            accessibility_types = ['wheelchair', 'visual', 'hearing', 'mobility', 'none']
            for access_type in accessibility_types:
                score = 1.0 if access_type in accessibility_needs else 0.0
                features.append(score)
            
            # Add padding features
            features.extend([0.5] * 3)
            
        else:
            # Dataclass format handling (original logic)
            for interest in InterestCategory:
                score = interests_lifestyle.interests.get(interest, 0.5)
                features.append(score)
                
            # Lifestyle factors
            lifestyle_factors = [
                interests_lifestyle.diet_type.value / 10.0 if interests_lifestyle.diet_type else 0.5,
                interests_lifestyle.fitness_level / 10.0 if interests_lifestyle.fitness_level else 0.5,
                interests_lifestyle.cultural_openness / 10.0 if interests_lifestyle.cultural_openness else 0.5,
                interests_lifestyle.language_skills / 10.0 if interests_lifestyle.language_skills else 0.5,
                interests_lifestyle.technology_comfort / 10.0 if interests_lifestyle.technology_comfort else 0.5
            ]
            features.extend(lifestyle_factors)
        
        # Ensure we have exactly 28 features for interests/lifestyle
        if len(features) < 28:
            features.extend([0.5] * (28 - len(features)))
        elif len(features) > 28:
            features = features[:28]
        
        return features
    
    def _encode_social_behavioral(self, social_behavioral) -> List[float]:
        """Encode social and behavioral features into feature vector"""
        features = []
        
        # Handle both dict and dataclass formats
        if isinstance(social_behavioral, dict):
            # Dict format handling
            group_preference = social_behavioral.get('group_travel_preference', 'couple')
            social_activity = social_behavioral.get('social_media_activity', 'moderate') 
            review_frequency = social_behavioral.get('review_writing_frequency', 'sometimes')
            
            # Group travel preference
            group_map = {"solo": 0.2, "couple": 0.4, "family": 0.6, "friends": 0.8, "group": 1.0}
            features.append(group_map.get(group_preference, 0.5))
            
            # Social media activity
            social_map = {"low": 0.25, "moderate": 0.5, "high": 0.75, "very_high": 1.0}
            features.append(social_map.get(social_activity, 0.5))
            
            # Review writing frequency
            review_map = {"never": 0.0, "rarely": 0.25, "sometimes": 0.5, "often": 0.75, "always": 1.0}
            features.append(review_map.get(review_frequency, 0.5))
            
            # Add padding features
            features.extend([0.5] * 9)
            
        else:
            # Dataclass format handling (original logic)
            # Social connectivity score
            social_score = social_behavioral.social_media_engagement / 10.0 if social_behavioral.social_media_engagement else 0.5
            features.append(social_score)
            
            # Review writing behavior
            review_score = social_behavioral.review_frequency / 10.0 if social_behavioral.review_frequency else 0.5
            features.append(review_score)
            
            # Group travel preference
            group_preference_map = {g.value: i/len(GroupTravelPreference) for i, g in enumerate(GroupTravelPreference)}
            group_score = group_preference_map.get(social_behavioral.group_preference.value, 0.5) if social_behavioral.group_preference else 0.5
            features.append(group_score)
            
            # Communication preferences
            for comm_pref in CommunicationPreference:
                score = social_behavioral.communication_preferences.get(comm_pref, 0.5)
                features.append(score)
        
        # Ensure we have exactly 12 features for social/behavioral
        if len(features) < 12:
            features.extend([0.5] * (12 - len(features)))
        elif len(features) > 12:
            features = features[:12]
        
        return features
        remaining_features = 30 - len(features)
        features.extend([0.5] * remaining_features)
        
        return features
    
    def _encode_computed_features(self, computed_features: Dict[str, Any]) -> List[float]:
        """Encode computed/derived features"""
        features = []
        
        # Adventure score
        features.append(computed_features.get("adventure_score", 0.5))
        
        # Luxury preference score
        features.append(computed_features.get("luxury_score", 0.5))
        
        # Cultural interest score
        features.append(computed_features.get("cultural_score", 0.5))
        
        # Budget consciousness score
        features.append(computed_features.get("budget_consciousness", 0.5))
        
        # Spontaneity score (based on booking lead times)
        features.append(computed_features.get("spontaneity_score", 0.5))
        
        # Social travel preference
        features.append(computed_features.get("social_score", 0.5))
        
        # Add remaining computed features
        remaining_features = 20 - len(features)
        features.extend([0.5] * remaining_features)
        
        return features
    
    def _encode_personality(self, personality_scores: Dict[str, float]) -> List[float]:
        """Encode personality scores"""
        features = []
        
        # 8 personality types
        for personality in TravelPersonality:
            score = personality_scores.get(personality.value, 0.125)  # Equal distribution default
            features.append(score)
        
        # 10 activity preference scores
        activity_scores = personality_scores.get("activity_scores", {})
        for activity in ActivityPreference:
            score = activity_scores.get(activity.value, 0.1)  # Equal distribution default
            features.append(score)
        
        return features
    
    def _compute_derived_features(self, profile: Dict[str, Any]) -> Dict[str, float]:
        """Compute derived features from raw profile data"""
        features = {}
        
        preferences = profile["preferences"]
        history = profile["history"]
        
        # Adventure score based on activity preferences and history
        adventure_activities = ["adventure", "outdoor", "sports"]
        adventure_score = 0.0
        for activity, score in preferences.activity_preferences.items():
            if activity.value in adventure_activities:
                adventure_score += score
        adventure_score = adventure_score / len(adventure_activities) if adventure_activities else 0.5
        features["adventure_score"] = adventure_score
        
        # Luxury score based on budget and accommodation preferences
        budget_max = preferences.budget_range[1]
        luxury_score = min(budget_max / 10000.0, 1.0)  # Normalize against 10k budget
        features["luxury_score"] = luxury_score
        
        # Cultural score
        cultural_activities = ["cultural", "educational"]
        cultural_score = 0.0
        for activity, score in preferences.activity_preferences.items():
            if activity.value in cultural_activities:
                cultural_score += score
        cultural_score = cultural_score / len(cultural_activities) if cultural_activities else 0.5
        features["cultural_score"] = cultural_score
        
        # Budget consciousness (inverse of spending relative to budget)
        avg_spending = np.mean(history.spending_patterns) if history.spending_patterns else budget_max
        budget_consciousness = 1.0 - min(avg_spending / budget_max, 1.0) if budget_max > 0 else 0.5
        features["budget_consciousness"] = budget_consciousness
        
        # Spontaneity score (inverse of booking lead time)
        avg_lead_time = np.mean(history.booking_lead_times) if history.booking_lead_times else 30
        spontaneity_score = 1.0 - min(avg_lead_time / 180.0, 1.0)  # Normalize against 6 months
        features["spontaneity_score"] = spontaneity_score
        
        # Social travel preference
        group_pref = sum(preferences.group_size_preference) / 2.0
        social_score = min(group_pref / 8.0, 1.0)  # Normalize against 8 people
        features["social_score"] = social_score
        
        return features
    
    def _compute_personality_scores(self, profile: Dict[str, Any]) -> Dict[str, float]:
        """Compute personality type scores using heuristics"""
        scores = {}
        
        preferences = profile["preferences"]
        computed = profile["computed_features"]
        
        # Explorer personality
        dest_diversity = len(preferences.preferred_destinations) / 20.0
        scores["explorer"] = min(dest_diversity + computed.get("adventure_score", 0.5), 1.0) / 2.0
        
        # Relaxer personality
        relaxation_pref = preferences.activity_preferences.get(ActivityPreference.RELAXATION, 0.5)
        scores["relaxer"] = (relaxation_pref + computed.get("luxury_score", 0.5)) / 2.0
        
        # Adventurer personality
        scores["adventurer"] = computed.get("adventure_score", 0.5)
        
        # Cultural personality
        scores["cultural"] = computed.get("cultural_score", 0.5)
        
        # Social personality
        scores["social"] = computed.get("social_score", 0.5)
        
        # Family personality
        family_status = profile["demographics"].family_status
        family_score = 0.8 if family_status == "family" else 0.3
        scores["family"] = family_score
        
        # Budget personality
        scores["budget"] = computed.get("budget_consciousness", 0.5)
        
        # Luxury personality
        scores["luxury"] = computed.get("luxury_score", 0.5)
        
        # Normalize scores to sum to 1
        total_score = sum(scores.values())
        if total_score > 0:
            scores = {k: v/total_score for k, v in scores.items()}
        
        return scores
    
    def update_profile_from_feedback(
        self, 
        user_profile: Dict[str, Any], 
        trip_feedback: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update user profile based on trip feedback"""
        
        # Extract feedback components
        overall_rating = trip_feedback.get("overall_satisfaction", 3.0)
        liked_items = trip_feedback.get("liked_recommendations", [])
        disliked_items = trip_feedback.get("disliked_recommendations", [])
        
        # Update trip history
        history = user_profile["history"]
        history.trip_ratings.append(overall_rating)
        
        # Update preferences based on feedback
        if overall_rating >= 4.0:  # Good trip
            # Reinforce preferences that led to good recommendations
            for item in liked_items:
                self._reinforce_preference(user_profile, item, 0.1)
        else:  # Poor trip
            # Reduce preferences that led to poor recommendations
            for item in disliked_items:
                self._reduce_preference(user_profile, item, 0.1)
        
        # Recompute derived features and personality scores
        user_profile["computed_features"] = self._compute_derived_features(user_profile)
        user_profile["personality_scores"] = self._compute_personality_scores(user_profile)
        
        self.logger.info(f"Updated profile for user {user_profile['user_id']} based on feedback")
        return user_profile
    
    def _reinforce_preference(self, profile: Dict[str, Any], item: str, strength: float):
        """Reinforce a preference based on positive feedback"""
        # This would implement more sophisticated preference learning
        # For now, a simple placeholder
        pass
    
    def _reduce_preference(self, profile: Dict[str, Any], item: str, strength: float):
        """Reduce a preference based on negative feedback"""
        # This would implement more sophisticated preference learning
        # For now, a simple placeholder
        pass
    
    def compute_user_similarity(
        self, 
        profile1_or_vec1, 
        profile2_or_vec2
    ) -> float:
        """Compute similarity between two user profiles or feature vectors"""
        
        import torch
        
        # Handle both profile dictionaries and feature vectors
        if isinstance(profile1_or_vec1, torch.Tensor):
            # If tensors are passed directly
            vec1 = profile1_or_vec1
            vec2 = profile2_or_vec2
        else:
            # If profiles are passed, generate feature vectors
            vec1 = self.generate_feature_vector(profile1_or_vec1)
            vec2 = self.generate_feature_vector(profile2_or_vec2)
        
        # Compute cosine similarity
        similarity = torch.cosine_similarity(vec1.unsqueeze(0), vec2.unsqueeze(0))
        
        return similarity.item()
    
    def get_similar_users(
        self, 
        target_profile: Dict[str, Any], 
        all_profiles: List[Dict[str, Any]], 
        top_k: int = 10
    ) -> List[Tuple[str, float]]:
        """Find most similar users to target profile"""
        
        similarities = []
        target_vec = self.generate_feature_vector(target_profile)
        
        for profile in all_profiles:
            if profile["user_id"] != target_profile["user_id"]:
                profile_vec = self.generate_feature_vector(profile)
                similarity = torch.cosine_similarity(
                    target_vec.unsqueeze(0), 
                    profile_vec.unsqueeze(0)
                ).item()
                similarities.append((profile["user_id"], similarity))
        
        # Sort by similarity and return top k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]


def create_sample_user_profiles() -> List[Dict[str, Any]]:
    """Create sample user profiles for testing and development"""
    
    modeler = UserProfileModeler()
    profiles = []
    
    # Sample Profile 1: Young Explorer
    demographics1 = UserDemographics(
        age=25,
        gender="female",
        income_bracket="middle",
        location="New York",
        family_status="single",
        travel_frequency="regular"
    )
    
    preferences1 = TravelPreferences(
        personality_type=TravelPersonality.EXPLORER,
        preferred_destinations=["Thailand", "Japan", "Iceland", "Peru"],
        activity_preferences={
            ActivityPreference.ADVENTURE: 0.8,
            ActivityPreference.CULTURAL: 0.7,
            ActivityPreference.OUTDOOR: 0.9,
            ActivityPreference.PHOTOGRAPHY: 0.6
        },
        budget_range=(1000, 4000),
        trip_duration_preference=(7, 14)
    )
    
    history1 = TravelHistory(
        destinations_visited=["Thailand", "Vietnam", "Nepal"],
        trip_ratings=[4.5, 4.0, 4.8],
        spending_patterns=[2500, 1800, 3200],
        booking_lead_times=[45, 30, 60]
    )
    
    profile1 = modeler.create_user_profile(
        "user_001", demographics1, preferences1, history1
    )
    profiles.append(profile1)
    
    # Sample Profile 2: Luxury Traveler
    demographics2 = UserDemographics(
        age=45,
        gender="male",
        income_bracket="luxury",
        location="Los Angeles",
        family_status="couple",
        travel_frequency="frequent"
    )
    
    preferences2 = TravelPreferences(
        personality_type=TravelPersonality.LUXURY,
        preferred_destinations=["Maldives", "Switzerland", "Monaco", "Dubai"],
        activity_preferences={
            ActivityPreference.RELAXATION: 0.9,
            ActivityPreference.CULINARY: 0.8,
            ActivityPreference.CULTURAL: 0.6,
            ActivityPreference.SHOPPING: 0.7
        },
        budget_range=(5000, 20000),
        trip_duration_preference=(5, 10)
    )
    
    history2 = TravelHistory(
        destinations_visited=["Maldives", "Switzerland", "Japan", "France"],
        trip_ratings=[5.0, 4.8, 4.6, 4.9],
        spending_patterns=[15000, 12000, 8000, 10000],
        booking_lead_times=[90, 120, 60, 75]
    )
    
    profile2 = modeler.create_user_profile(
        "user_002", demographics2, preferences2, history2
    )
    profiles.append(profile2)
    
    # Sample Profile 3: Family Traveler
    demographics3 = UserDemographics(
        age=35,
        gender="female",
        income_bracket="high",
        location="Chicago",
        family_status="family",
        travel_frequency="occasional"
    )
    
    preferences3 = TravelPreferences(
        personality_type=TravelPersonality.FAMILY,
        preferred_destinations=["Orlando", "San Diego", "London", "Tokyo"],
        activity_preferences={
            ActivityPreference.EDUCATIONAL: 0.8,
            ActivityPreference.CULTURAL: 0.7,
            ActivityPreference.RELAXATION: 0.6,
            ActivityPreference.OUTDOOR: 0.5
        },
        budget_range=(3000, 8000),
        trip_duration_preference=(5, 12),
        group_size_preference=(4, 4)
    )
    
    history3 = TravelHistory(
        destinations_visited=["Orlando", "San Diego", "Hawaii"],
        trip_ratings=[4.2, 4.5, 4.0],
        spending_patterns=[6000, 5500, 7000],
        booking_lead_times=[120, 90, 150]
    )
    
    profile3 = modeler.create_user_profile(
        "user_003", demographics3, preferences3, history3
    )
    profiles.append(profile3)
    
    return profiles


if __name__ == "__main__":
    # Test the user profile modeling system
    profiles = create_sample_user_profiles()
    modeler = UserProfileModeler()
    
    print("Sample User Profiles Created:")
    for profile in profiles:
        print(f"\nUser: {profile['user_id']}")
        print(f"Personality Type: {profile['preferences'].personality_type}")
        print(f"Feature Vector Shape: {modeler.generate_feature_vector(profile).shape}")
        print(f"Top Personality Scores: {dict(list(profile['personality_scores'].items())[:3])}")
    
    # Test similarity computation
    if len(profiles) >= 2:
        similarity = modeler.compute_user_similarity(profiles[0], profiles[1])
        print(f"\nSimilarity between User 1 and User 2: {similarity:.3f}")