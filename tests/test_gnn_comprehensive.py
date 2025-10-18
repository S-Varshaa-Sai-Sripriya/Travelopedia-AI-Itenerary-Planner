"""
Comprehensive GNN Testing Suite

This module provides thorough testing of the Graph Neural Network implementation
including unit tests, integration tests, and performance validation.
"""

import pytest
import torch
import numpy as np
import asyncio
import time
from pathlib import Path
import sys
from typing import Dict, List, Any

# Add app directory to path
sys.path.append(str(Path(__file__).parent.parent / "app"))

from app.agents.gnn_agent import (
    GNNAgent, 
    TravelKnowledgeGraph, 
    GraphAttentionTravelNet,
    TravelEntity,
    GraphEdge,
    create_sample_travel_data
)
from app.models.user_profile import UserProfileModeler


class TestTravelKnowledgeGraph:
    """Test suite for TravelKnowledgeGraph class"""
    
    def setup_method(self):
        """Setup test environment"""
        self.kg = TravelKnowledgeGraph()
        
    def test_entity_addition(self):
        """Test adding entities to knowledge graph"""
        # Create test entity
        entity = TravelEntity(
            entity_id="test_destination_001",
            entity_type="destination",
            name="Test City",
            features={"latitude": 40.7128, "longitude": -74.0060}
        )
        
        # Add entity
        self.kg.add_entity(entity)
        
        # Verify entity was added
        assert "test_destination_001" in self.kg.entities
        assert self.kg.entities["test_destination_001"].name == "Test City"
        assert self.kg.entities["test_destination_001"].entity_type == "destination"
        
    def test_edge_addition(self):
        """Test adding edges to knowledge graph"""
        # Create test entities
        user_entity = TravelEntity("user_001", "user", "Test User", {})
        dest_entity = TravelEntity("dest_001", "destination", "Test Destination", {})
        
        self.kg.add_entity(user_entity)
        self.kg.add_entity(dest_entity)
        
        # Create test edge
        edge = GraphEdge(
            source_id="user_001",
            target_id="dest_001",
            edge_type="visited",
            weight=4.5,
            attributes={"timestamp": "2025-10-18"}
        )
        
        # Add edge
        self.kg.add_edge(edge)
        
        # Verify edge was added
        assert len(self.kg.edges) == 1
        assert self.kg.edges[0].source_id == "user_001"
        assert self.kg.edges[0].target_id == "dest_001"
        assert self.kg.edges[0].weight == 4.5
        
    def test_pytorch_geometric_conversion(self):
        """Test conversion to PyTorch Geometric format"""
        # Add sample entities
        entities = [
            TravelEntity("user_001", "user", "User 1", {}),
            TravelEntity("dest_001", "destination", "Destination 1", {}),
            TravelEntity("hotel_001", "hotel", "Hotel 1", {})
        ]
        
        for entity in entities:
            self.kg.add_entity(entity)
        
        # Add sample edges
        edges = [
            GraphEdge("user_001", "dest_001", "visited", 4.0),
            GraphEdge("dest_001", "hotel_001", "offers", 1.0)
        ]
        
        for edge in edges:
            self.kg.add_edge(edge)
        
        # Convert to PyTorch Geometric format
        data = self.kg.build_pytorch_geometric_data()
        
        # Verify conversion
        assert data.node_types is not None
        assert len(data.node_types) > 0
        
        # Check that we have the expected entity types
        expected_types = {"user", "destination", "hotel"}
        actual_types = set(data.node_types)
        assert expected_types.issubset(actual_types)


class TestGraphAttentionTravelNet:
    """Test suite for GraphAttentionTravelNet model"""
    
    def setup_method(self):
        """Setup test environment"""
        self.model_config = {
            'input_dim': 128,
            'hidden_dim': 64,  # Smaller for testing
            'output_dim': 32,  # Smaller for testing
            'num_heads': 4,    # Fewer heads for testing
            'num_layers': 2,   # Fewer layers for testing
            'dropout': 0.1
        }
        self.model = GraphAttentionTravelNet(**self.model_config)
        
    def test_model_initialization(self):
        """Test model initialization"""
        assert self.model.input_dim == 128
        assert self.model.hidden_dim == 64
        assert self.model.output_dim == 32
        assert self.model.num_heads == 4
        assert self.model.num_layers == 2
        
    def test_model_parameters(self):
        """Test model parameter count"""
        total_params = sum(p.numel() for p in self.model.parameters())
        assert total_params > 0  # Model should have parameters
        
    def test_recommendation_scoring(self):
        """Test recommendation scoring functionality"""
        # Create dummy embeddings
        user_emb = torch.randn(1, 32)  # batch_size=1, output_dim=32
        item_emb = torch.randn(1, 32)
        
        # Test scoring
        score = self.model.predict_recommendation_score(user_emb, item_emb)
        
        # Verify output
        assert score.shape == (1, 1)
        assert 0 <= score.item() <= 1  # Should be sigmoid output


class TestUserProfileModeler:
    """Test suite for UserProfileModeler integration"""
    
    def setup_method(self):
        """Setup test environment"""
        self.modeler = UserProfileModeler()
        
    def test_feature_vector_generation_dict_format(self):
        """Test feature vector generation with dictionary input"""
        user_profile = {
            'user_id': 'test_user_001',
            'demographics': {
                'age': 28,
                'nationality': 'US',
                'occupation': 'Engineer',
                'income_level': 'mid'
            },
            'travel_preferences': {
                'budget_range': 'mid',
                'travel_style': 'adventure',
                'accommodation_type': 'hotel',
                'preferred_activities': ['culture', 'food']
            },
            'travel_history': {
                'previous_destinations': ['Paris', 'Tokyo'],
                'total_trips': 5,
                'avg_trip_duration': 7,
                'preferred_season': 'spring'
            },
            'interests_and_lifestyle': {
                'interests': ['culture', 'food'],
                'dietary_restrictions': [],
                'accessibility_needs': []
            },
            'social_and_behavioral': {
                'group_travel_preference': 'couple',
                'social_media_activity': 'moderate',
                'review_writing_frequency': 'sometimes'
            }
        }
        
        # Generate feature vector
        features = self.modeler.generate_feature_vector(user_profile)
        
        # Verify output
        assert isinstance(features, torch.Tensor)
        assert features.shape == (128,)
        assert features.dtype == torch.float32
        
        # Verify feature values are in reasonable range
        assert torch.all(features >= 0)
        assert torch.all(features <= 1)
        
    def test_user_similarity_computation(self):
        """Test user similarity computation"""
        # Create two similar users
        user1_profile = {
            'user_id': 'user_001',
            'demographics': {'age': 28, 'nationality': 'US', 'income_level': 'mid'},
            'travel_preferences': {'budget_range': 'mid', 'travel_style': 'adventure', 'preferred_activities': ['culture']},
            'travel_history': {'previous_destinations': ['Paris'], 'total_trips': 5},
            'interests_and_lifestyle': {'interests': ['culture'], 'dietary_restrictions': []},
            'social_and_behavioral': {'group_travel_preference': 'couple', 'social_media_activity': 'moderate'}
        }
        
        user2_profile = {
            'user_id': 'user_002',
            'demographics': {'age': 30, 'nationality': 'US', 'income_level': 'mid'},
            'travel_preferences': {'budget_range': 'mid', 'travel_style': 'adventure', 'preferred_activities': ['culture']},
            'travel_history': {'previous_destinations': ['Tokyo'], 'total_trips': 4},
            'interests_and_lifestyle': {'interests': ['culture'], 'dietary_restrictions': []},
            'social_and_behavioral': {'group_travel_preference': 'couple', 'social_media_activity': 'moderate'}
        }
        
        # Generate feature vectors
        features1 = self.modeler.generate_feature_vector(user1_profile)
        features2 = self.modeler.generate_feature_vector(user2_profile)
        
        # Compute similarity
        similarity = self.modeler.compute_user_similarity(features1, features2)
        
        # Verify similarity
        assert 0 <= similarity <= 1
        assert similarity > 0.5  # Should be reasonably similar


class TestGNNAgent:
    """Test suite for GNNAgent class"""
    
    def setup_method(self):
        """Setup test environment"""
        self.agent = GNNAgent()
        
    @pytest.mark.asyncio
    async def test_agent_initialization(self):
        """Test GNN agent initialization"""
        assert self.agent.knowledge_graph is not None
        assert self.agent.model is not None
        assert self.agent.user_profile_modeler is not None
        assert not self.agent.trained
        
    @pytest.mark.asyncio
    async def test_user_addition_to_graph(self):
        """Test adding user to knowledge graph"""
        user_profile = {
            'user_id': 'test_user_001',
            'demographics': {'age': 28, 'nationality': 'US', 'income_level': 'mid'},
            'travel_preferences': {'budget_range': 'mid', 'travel_style': 'adventure', 'preferred_activities': ['culture']},
            'travel_history': {'previous_destinations': ['Paris'], 'total_trips': 5},
            'interests_and_lifestyle': {'interests': ['culture'], 'dietary_restrictions': []},
            'social_and_behavioral': {'group_travel_preference': 'couple', 'social_media_activity': 'moderate'}
        }
        
        # Add user to graph
        self.agent.add_user_to_graph(user_profile)
        
        # Verify user was added
        assert 'test_user_001' in self.agent.knowledge_graph.entities
        user_entity = self.agent.knowledge_graph.entities['test_user_001']
        assert user_entity.entity_type == 'user'
        assert user_entity.embedding is not None
        assert user_entity.embedding.shape == (128,)
        
    @pytest.mark.asyncio
    async def test_destination_addition_to_graph(self):
        """Test adding destination to knowledge graph"""
        destination_data = {
            'destination_id': 'test_dest_001',
            'name': 'Test City',
            'latitude': 40.7128,
            'longitude': -74.0060,
            'popularity': 0.8,
            'avg_rating': 4.5,
            'price_level': 0.6,
            'categories': ['urban', 'cultural']
        }
        
        # Add destination to graph
        self.agent.add_destination_to_graph(destination_data)
        
        # Verify destination was added
        assert 'test_dest_001' in self.agent.knowledge_graph.entities
        dest_entity = self.agent.knowledge_graph.entities['test_dest_001']
        assert dest_entity.entity_type == 'destination'
        assert dest_entity.name == 'Test City'
        
    @pytest.mark.asyncio
    async def test_interaction_addition(self):
        """Test adding user-item interactions"""
        # First add user and destination
        user_profile = {
            'user_id': 'test_user_001',
            'demographics': {'age': 28, 'nationality': 'US', 'income_level': 'mid'},
            'travel_preferences': {'budget_range': 'mid', 'travel_style': 'adventure', 'preferred_activities': ['culture']},
            'travel_history': {'previous_destinations': ['Paris'], 'total_trips': 5},
            'interests_and_lifestyle': {'interests': ['culture'], 'dietary_restrictions': []},
            'social_and_behavioral': {'group_travel_preference': 'couple', 'social_media_activity': 'moderate'}
        }
        
        destination_data = {
            'destination_id': 'test_dest_001',
            'name': 'Test City',
            'latitude': 40.7128,
            'longitude': -74.0060,
        }
        
        self.agent.add_user_to_graph(user_profile)
        self.agent.add_destination_to_graph(destination_data)
        
        # Add interaction
        self.agent.add_interaction('test_user_001', 'test_dest_001', 'visited', 4.5)
        
        # Verify interaction was added
        assert len(self.agent.knowledge_graph.edges) == 1
        edge = self.agent.knowledge_graph.edges[0]
        assert edge.source_id == 'test_user_001'
        assert edge.target_id == 'test_dest_001'
        assert edge.edge_type == 'visited'
        assert edge.weight == 4.5
        
    @pytest.mark.asyncio
    async def test_recommendation_generation_fallback(self):
        """Test recommendation generation in fallback mode"""
        # Add some sample data
        destinations, hotels, interactions = create_sample_travel_data()
        
        for dest in destinations:
            self.agent.add_destination_to_graph(dest)
        
        # Generate recommendations
        recommendations = await self.agent.generate_recommendations(
            user_id=1,
            user_preferences={
                'budget_range': 'mid',
                'travel_style': 'adventure',
                'interests': ['culture', 'food']
            },
            destination='Paris, France',
            trip_context={
                'trip_type': 'leisure',
                'duration': 5,
                'group_size': 2
            }
        )
        
        # Verify recommendations
        assert recommendations['status'] == 'success'
        assert 'recommendations' in recommendations
        assert 'personalization_score' in recommendations
        assert recommendations['personalization_score'] > 0
        
        # Check recommendation structure
        recs = recommendations['recommendations']
        assert isinstance(recs, dict)
        
        # Verify each recommendation type has proper structure
        for rec_type, rec_list in recs.items():
            assert isinstance(rec_list, list)
            if rec_list:
                rec = rec_list[0]
                assert 'name' in rec
                assert 'rating' in rec
                assert 'score' in rec


class TestGNNPerformance:
    """Performance and stress tests for GNN implementation"""
    
    def setup_method(self):
        """Setup test environment"""
        self.agent = GNNAgent()
        
    @pytest.mark.asyncio
    async def test_large_graph_performance(self):
        """Test performance with larger knowledge graph"""
        # Add many entities to test scalability
        num_users = 100
        num_destinations = 50
        num_interactions = 500
        
        start_time = time.time()
        
        # Add users
        for i in range(num_users):
            user_profile = {
                'user_id': f'user_{i:03d}',
                'demographics': {'age': 25 + (i % 40), 'nationality': 'US', 'income_level': 'mid'},
                'travel_preferences': {'budget_range': 'mid', 'travel_style': 'adventure', 'preferred_activities': ['culture']},
                'travel_history': {'previous_destinations': ['Paris'], 'total_trips': 5},
                'interests_and_lifestyle': {'interests': ['culture'], 'dietary_restrictions': []},
                'social_and_behavioral': {'group_travel_preference': 'couple', 'social_media_activity': 'moderate'}
            }
            self.agent.add_user_to_graph(user_profile)
        
        # Add destinations
        for i in range(num_destinations):
            dest_data = {
                'destination_id': f'dest_{i:03d}',
                'name': f'Destination {i}',
                'latitude': 40.0 + (i % 20),
                'longitude': -74.0 + (i % 20),
                'popularity': 0.5 + (i % 5) * 0.1,
                'avg_rating': 3.5 + (i % 3) * 0.5,
                'price_level': 0.3 + (i % 4) * 0.2
            }
            self.agent.add_destination_to_graph(dest_data)
        
        # Add interactions
        for i in range(num_interactions):
            user_id = f'user_{i % num_users:03d}'
            dest_id = f'dest_{i % num_destinations:03d}'
            rating = 3.0 + (i % 3)
            self.agent.add_interaction(user_id, dest_id, 'visited', rating)
        
        graph_building_time = time.time() - start_time
        
        # Test knowledge graph conversion
        conversion_start = time.time()
        kg_data = self.agent.knowledge_graph.build_pytorch_geometric_data()
        conversion_time = time.time() - conversion_start
        
        # Performance assertions
        assert graph_building_time < 10.0  # Should complete within 10 seconds
        assert conversion_time < 5.0       # Conversion should be fast
        
        # Verify graph structure
        assert len(self.agent.knowledge_graph.entities) == num_users + num_destinations
        assert len(self.agent.knowledge_graph.edges) == num_interactions
        
        print(f"Performance Results:")
        print(f"  Graph building time: {graph_building_time:.2f}s")
        print(f"  Conversion time: {conversion_time:.2f}s")
        print(f"  Entities: {len(self.agent.knowledge_graph.entities)}")
        print(f"  Edges: {len(self.agent.knowledge_graph.edges)}")
        
    @pytest.mark.asyncio
    async def test_recommendation_response_time(self):
        """Test recommendation generation response time"""
        # Add sample data
        destinations, hotels, interactions = create_sample_travel_data()
        
        for dest in destinations:
            self.agent.add_destination_to_graph(dest)
        
        # Test multiple recommendation requests
        response_times = []
        
        for i in range(10):  # Test 10 requests
            start_time = time.time()
            
            recommendations = await self.agent.generate_recommendations(
                user_id=i,
                user_preferences={
                    'budget_range': 'mid',
                    'travel_style': 'adventure',
                    'interests': ['culture', 'food']
                },
                destination=f'Test City {i}',
                trip_context={
                    'trip_type': 'leisure',
                    'duration': 5,
                    'group_size': 2
                }
            )
            
            response_time = time.time() - start_time
            response_times.append(response_time)
            
            # Verify successful response
            assert recommendations['status'] == 'success'
        
        # Performance assertions
        avg_response_time = np.mean(response_times)
        max_response_time = np.max(response_times)
        
        assert avg_response_time < 1.0    # Average should be under 1 second
        assert max_response_time < 2.0    # Maximum should be under 2 seconds
        
        print(f"Response Time Results:")
        print(f"  Average: {avg_response_time:.3f}s")
        print(f"  Maximum: {max_response_time:.3f}s")
        print(f"  Minimum: {np.min(response_times):.3f}s")


class TestGNNIntegration:
    """Integration tests for the complete GNN system"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self):
        """Test complete end-to-end GNN workflow"""
        agent = GNNAgent()
        
        # Step 1: Create sample travel data
        destinations, hotels, interactions = create_sample_travel_data()
        
        # Step 2: Build knowledge graph
        for dest in destinations:
            agent.add_destination_to_graph(dest)
        
        # Step 3: Add users
        sample_users = [
            {
                'user_id': 'integration_user_001',
                'demographics': {'age': 28, 'nationality': 'US', 'income_level': 'mid'},
                'travel_preferences': {'budget_range': 'mid', 'travel_style': 'adventure', 'preferred_activities': ['culture']},
                'travel_history': {'previous_destinations': ['Paris'], 'total_trips': 5},
                'interests_and_lifestyle': {'interests': ['culture'], 'dietary_restrictions': []},
                'social_and_behavioral': {'group_travel_preference': 'couple', 'social_media_activity': 'moderate'}
            },
            {
                'user_id': 'integration_user_002',
                'demographics': {'age': 35, 'nationality': 'UK', 'income_level': 'high'},
                'travel_preferences': {'budget_range': 'luxury', 'travel_style': 'relaxation', 'preferred_activities': ['spa']},
                'travel_history': {'previous_destinations': ['Bali'], 'total_trips': 8},
                'interests_and_lifestyle': {'interests': ['spa'], 'dietary_restrictions': ['vegetarian']},
                'social_and_behavioral': {'group_travel_preference': 'solo', 'social_media_activity': 'high'}
            }
        ]
        
        for user in sample_users:
            agent.add_user_to_graph(user)
        
        # Step 4: Add interactions
        for interaction in interactions:
            agent.add_interaction(
                interaction['user_id'],
                interaction['item_id'],
                interaction['type'],
                interaction['rating']
            )
        
        # Step 5: Generate recommendations for each user
        for user in sample_users:
            recommendations = await agent.generate_recommendations(
                user_id=user['user_id'],
                user_preferences=user['travel_preferences'],
                destination='Paris, France',
                trip_context={
                    'trip_type': 'leisure',
                    'duration': 7,
                    'group_size': 2
                }
            )
            
            # Verify recommendations
            assert recommendations['status'] == 'success'
            assert 'recommendations' in recommendations
            assert recommendations['destination'] == 'Paris, France'
            assert recommendations['personalization_score'] > 0
        
        # Step 6: Test feedback integration
        agent.update_from_feedback('integration_user_001', 'dest_001', 4.8)
        
        # Verify feedback was added
        feedback_edges = [e for e in agent.knowledge_graph.edges 
                         if e.source_id == 'integration_user_001' and e.target_id == 'dest_001']
        assert len(feedback_edges) > 0
        
        print("✅ End-to-end integration test completed successfully!")


def run_comprehensive_tests():
    """Run all comprehensive GNN tests"""
    print("🧪 Running Comprehensive GNN Test Suite...")
    
    # Run pytest with verbose output
    pytest_args = [
        __file__,
        "-v",
        "--tb=short",
        "--asyncio-mode=auto"
    ]
    
    exit_code = pytest.main(pytest_args)
    
    if exit_code == 0:
        print("🎉 All GNN tests passed successfully!")
    else:
        print("❌ Some GNN tests failed. Check output above.")
    
    return exit_code == 0


if __name__ == "__main__":
    # Run comprehensive tests when executed directly
    run_comprehensive_tests()