"""
GNN-based Personalization Agent for user preference reasoning.
Uses Graph Neural Networks to model user preferences and generate personalized recommendations.
"""

import random
from typing import Dict, List, Any, Tuple
import yaml
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class PersonalizationGNN:
    """
    Graph Neural Network agent for personalized travel recommendations.
    Models user preferences, history, and constraints as a graph.
    """
    
    def __init__(self, config_path: str = "backend/utils/config.yaml"):
        """Initialize GNN personalization agent."""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.gnn_config = self.config['models']['gnn']
        self.pref_config = self.config['personalization']
        
        # In production, this would load a trained PyTorch Geometric model
        self.model = None  # Placeholder for GNN model
        self.user_embeddings = {}  # Cache for user embeddings
        
        logger.info("GNN Personalization Agent initialized")
    
    def build_preference_graph(
        self,
        user_id: str,
        preferences: Dict[str, Any],
        history: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Build a preference graph for the user.
        
        Args:
            user_id: User identifier
            preferences: Current preferences
            history: User travel history
            
        Returns:
            Graph representation of preferences
        """
        logger.info(f"Building preference graph for user {user_id}")
        
        # Node types: User, Preferences, Destinations, Activities
        graph = {
            'nodes': [],
            'edges': [],
            'node_features': {},
            'edge_weights': {}
        }
        
        # Add user node
        user_node = {'id': user_id, 'type': 'user'}
        graph['nodes'].append(user_node)
        
        # Add preference nodes
        pref_categories = preferences.get('categories', [])
        for pref in pref_categories:
            pref_node = {'id': f'pref_{pref}', 'type': 'preference', 'category': pref}
            graph['nodes'].append(pref_node)
            
            # Connect user to preference
            graph['edges'].append({
                'source': user_id,
                'target': f'pref_{pref}',
                'weight': 1.0
            })
        
        # Add historical destination nodes
        prev_trips = history.get('previous_trips', [])
        for i, trip in enumerate(prev_trips):
            dest_node = {
                'id': f'dest_{i}',
                'type': 'destination',
                'name': trip.get('destination'),
                'satisfaction': trip.get('satisfaction', 0)
            }
            graph['nodes'].append(dest_node)
            
            # Connect user to destination with satisfaction weight
            graph['edges'].append({
                'source': user_id,
                'target': f'dest_{i}',
                'weight': trip.get('satisfaction', 0) / 5.0  # Normalize to [0, 1]
            })
            
            # Connect destination to preferences
            for pref in trip.get('preferences', []):
                if f'pref_{pref}' in [n['id'] for n in graph['nodes']]:
                    graph['edges'].append({
                        'source': f'dest_{i}',
                        'target': f'pref_{pref}',
                        'weight': 0.8
                    })
        
        logger.debug(f"Built graph with {len(graph['nodes'])} nodes and {len(graph['edges'])} edges")
        return graph
    
    def generate_user_embedding(
        self,
        user_id: str,
        preference_graph: Dict[str, Any]
    ) -> List[float]:
        """
        Generate user embedding from preference graph.
        
        Args:
            user_id: User identifier
            preference_graph: User's preference graph
            
        Returns:
            User embedding vector
        """
        logger.info("Generating user embedding")
        
        # In production, this would use a trained GNN model
        # For now, create a simple embedding based on preferences
        
        embedding_dim = self.pref_config['user_embedding_dim']
        
        # Count preference occurrences
        pref_counts = {}
        for node in preference_graph['nodes']:
            if node['type'] == 'preference':
                category = node['category']
                pref_counts[category] = pref_counts.get(category, 0) + 1
        
        # Create embedding (simplified)
        embedding = [random.random() for _ in range(embedding_dim)]
        
        # Normalize
        norm = sum(x**2 for x in embedding) ** 0.5
        embedding = [x / norm for x in embedding]
        
        # Cache embedding
        self.user_embeddings[user_id] = embedding
        
        logger.debug(f"Generated {embedding_dim}-dimensional embedding")
        return embedding
    
    def rank_options(
        self,
        user_embedding: List[float],
        options: List[Dict[str, Any]],
        option_type: str = 'hotel'
    ) -> List[Dict[str, Any]]:
        """
        Rank options based on user embedding and preferences.
        
        Args:
            user_embedding: User preference embedding
            options: List of options (hotels, flights, activities)
            option_type: Type of options being ranked
            
        Returns:
            Ranked list of options with personalization scores
        """
        logger.info(f"Ranking {len(options)} {option_type} options")
        
        scored_options = []
        
        for option in options:
            # Skip non-dict options
            if not isinstance(option, dict):
                logger.warning(f"Skipping non-dict option: {type(option)}")
                continue
                
            # Calculate personalization score
            score = self._calculate_personalization_score(
                user_embedding,
                option,
                option_type
            )
            
            option_with_score = option.copy()
            option_with_score['personalization_score'] = score
            scored_options.append(option_with_score)
        
        # Sort by personalization score
        if scored_options:
            scored_options.sort(key=lambda x: x['personalization_score'], reverse=True)
            logger.debug(f"Ranked options - top score: {scored_options[0]['personalization_score']:.3f}")
        
        return scored_options
    
    def recommend_activities(
        self,
        user_profile: Dict[str, Any],
        destination: str,
        available_activities: List[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Recommend activities using GNN-based personalization.
        
        Args:
            user_profile: User preferences and profile
            destination: Destination city
            available_activities: Pre-fetched activities from API
            
        Returns:
            List of recommended activities
        """
        logger.info(f"Generating activity recommendations for {destination}")
        
        # Use provided activities or generate mock ones
        if available_activities:
            activities = available_activities
        else:
            # Fallback to mock generation
            activities = self._generate_mock_activities(user_profile, destination)
        
        # Score and rank activities based on user preferences
        for activity in activities:
            activity['personalization_score'] = self._calculate_activity_score(
                activity,
                user_profile.get('preferences', [])
            )
        
        # Sort by score and return top activities
        activities.sort(key=lambda x: x.get('personalization_score', 0), reverse=True)
        
        return activities[:10]  # Return top 10
    
    def _calculate_activity_score(self, activity: Dict, preferences: List[str]) -> float:
        """Calculate personalization score for an activity."""
        score = activity.get('rating', 4.0) * 20  # Base score from rating
        
        # Boost score if activity category matches user preferences
        activity_category = activity.get('category', '').lower()
        if activity_category in [p.lower() for p in preferences]:
            score += 30
        
        # Consider price level (lower is better for budget-conscious)
        price_level = activity.get('price_level', 2)
        score -= (price_level - 1) * 5
        
        return max(0, score)
    
    def _generate_mock_activities(self, user_profile: Dict, destination: str) -> List[Dict]:
        """Generate mock activities (fallback)."""
        activity_types = {
            'adventure': ['Hiking', 'Zip-lining', 'Kayaking', 'Rock Climbing'],
            'cultural': ['Museum Visit', 'Historical Tour', 'Art Gallery', 'Local Market'],
            'culinary': ['Food Tour', 'Cooking Class', 'Wine Tasting', 'Local Restaurant'],
            'nature': ['Beach Visit', 'Park Walk', 'Botanical Garden', 'Scenic Viewpoint'],
            'relaxation': ['Spa Day', 'Yoga Class', 'Meditation', 'Beach Relaxation']
        }
    
    def _calculate_personalization_score(
        self,
        user_embedding: List[float],
        option: Dict[str, Any],
        option_type: str
    ) -> float:
        """Calculate personalization score for an option."""
        # Base score from rating or reviews
        base_score = 0.5
        
        if option_type == 'hotel':
            # Consider rating, amenities, location
            rating = option.get('rating', 3.5)
            base_score = rating / 5.0
            
            # Boost for amenities
            amenities = option.get('amenities', [])
            amenity_boost = min(len(amenities) * 0.02, 0.2)
            base_score += amenity_boost
            
        elif option_type == 'flight':
            # Consider price, duration, stops
            stops = option.get('outbound', {}).get('stops', 0)
            base_score = 0.8 - (stops * 0.15)
            
        # Add some randomness for variety (simulating embedding similarity)
        personalization_factor = random.uniform(0.7, 1.0)
        
        final_score = base_score * personalization_factor
        return min(final_score, 1.0)
    
    def explain_recommendation(
        self,
        option: Dict[str, Any],
        user_id: str
    ) -> str:
        """
        Generate explanation for why an option was recommended.
        
        Args:
            option: Recommended option
            user_id: User identifier
            
        Returns:
            Human-readable explanation
        """
        score = option.get('personalization_score', 0)
        
        if score > 0.85:
            reason = "Perfect match for your preferences"
        elif score > 0.70:
            reason = "Great fit based on your travel history"
        elif score > 0.55:
            reason = "Good option that aligns with your interests"
        else:
            reason = "Recommended based on popularity"
        
        return reason


def create_personalization_agent() -> PersonalizationGNN:
    """Factory function to create personalization agent."""
    return PersonalizationGNN()
