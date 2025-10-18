#!/usr/bin/env python3
"""
Comprehensive GNN Testing Script

This script runs thorough tests of the GNN implementation without pytest dependencies.
"""

import sys
import asyncio
import time
import traceback
from pathlib import Path

# Add app directory to path
sys.path.append(str(Path.cwd() / "app"))

from agents.gnn_agent import (
    GNNAgent, 
    TravelKnowledgeGraph, 
    GraphAttentionTravelNet,
    TravelEntity,
    GraphEdge,
    create_sample_travel_data
)
from models.user_profile import UserProfileModeler


class GNNTestSuite:
    """Comprehensive GNN test suite"""
    
    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """Log test result"""
        if success:
            self.tests_passed += 1
            print(f"✅ {test_name}")
            if message:
                print(f"   {message}")
        else:
            self.tests_failed += 1
            print(f"❌ {test_name}")
            if message:
                print(f"   Error: {message}")
        
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message
        })
    
    def test_knowledge_graph_basic(self):
        """Test basic knowledge graph functionality"""
        try:
            kg = TravelKnowledgeGraph()
            
            # Test entity addition
            entity = TravelEntity(
                entity_id="test_dest_001",
                entity_type="destination",
                name="Test City",
                features={"latitude": 40.7128, "longitude": -74.0060}
            )
            kg.add_entity(entity)
            
            # Verify entity was added
            assert "test_dest_001" in kg.entities
            assert kg.entities["test_dest_001"].name == "Test City"
            
            # Test edge addition
            user_entity = TravelEntity("user_001", "user", "Test User", {})
            kg.add_entity(user_entity)
            
            edge = GraphEdge("user_001", "test_dest_001", "visited", 4.5)
            kg.add_edge(edge)
            
            assert len(kg.edges) == 1
            assert kg.edges[0].weight == 4.5
            
            self.log_test("Knowledge Graph Basic Operations", True, 
                         f"Added {len(kg.entities)} entities and {len(kg.edges)} edges")
            
        except Exception as e:
            self.log_test("Knowledge Graph Basic Operations", False, str(e))
    
    def test_pytorch_geometric_conversion(self):
        """Test PyTorch Geometric data conversion"""
        try:
            kg = TravelKnowledgeGraph()
            
            # Add sample entities
            entities = [
                TravelEntity("user_001", "user", "User 1", {}),
                TravelEntity("dest_001", "destination", "Destination 1", {}),
                TravelEntity("hotel_001", "hotel", "Hotel 1", {})
            ]
            
            for entity in entities:
                kg.add_entity(entity)
            
            # Add sample edges
            edges = [
                GraphEdge("user_001", "dest_001", "visited", 4.0),
                GraphEdge("dest_001", "hotel_001", "offers", 1.0)
            ]
            
            for edge in edges:
                kg.add_edge(edge)
            
            # Convert to PyTorch Geometric format
            data = kg.build_pytorch_geometric_data()
            
            # Verify conversion
            assert data.node_types is not None
            assert len(data.node_types) > 0
            
            expected_types = {"user", "destination", "hotel"}
            actual_types = set(data.node_types)
            assert expected_types.issubset(actual_types)
            
            self.log_test("PyTorch Geometric Conversion", True, 
                         f"Converted graph with {len(data.node_types)} node types")
            
        except Exception as e:
            self.log_test("PyTorch Geometric Conversion", False, str(e))
    
    def test_model_architecture(self):
        """Test GraphAttentionTravelNet model"""
        try:
            model_config = {
                'input_dim': 128,
                'hidden_dim': 64,
                'output_dim': 32,
                'num_heads': 4,
                'num_layers': 2,
                'dropout': 0.1
            }
            model = GraphAttentionTravelNet(**model_config)
            
            # Verify model parameters
            assert model.input_dim == 128
            assert model.hidden_dim == 64
            assert model.output_dim == 32
            
            # Test parameter count
            total_params = sum(p.numel() for p in model.parameters())
            assert total_params > 0
            
            # Test recommendation scoring
            import torch
            user_emb = torch.randn(1, 32)
            item_emb = torch.randn(1, 32)
            score = model.predict_recommendation_score(user_emb, item_emb)
            
            assert score.shape == (1, 1)
            assert 0 <= score.item() <= 1
            
            self.log_test("Model Architecture", True, 
                         f"Model with {total_params:,} parameters, scoring test passed")
            
        except Exception as e:
            self.log_test("Model Architecture", False, str(e))
    
    def test_user_profile_features(self):
        """Test user profile feature generation"""
        try:
            modeler = UserProfileModeler()
            
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
            features = modeler.generate_feature_vector(user_profile)
            
            # Verify output
            import torch
            assert isinstance(features, torch.Tensor)
            assert features.shape == (128,)
            assert features.dtype == torch.float32
            
            # Verify feature values are in reasonable range
            assert torch.all(features >= 0)
            assert torch.all(features <= 1)
            
            self.log_test("User Profile Features", True, 
                         f"Generated {features.shape[0]}-dimensional feature vector")
            
        except Exception as e:
            self.log_test("User Profile Features", False, str(e))
    
    def test_user_similarity(self):
        """Test user similarity computation"""
        try:
            modeler = UserProfileModeler()
            
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
            features1 = modeler.generate_feature_vector(user1_profile)
            features2 = modeler.generate_feature_vector(user2_profile)
            
            # Compute similarity
            similarity = modeler.compute_user_similarity(features1, features2)
            
            # Verify similarity
            assert 0 <= similarity <= 1
            assert similarity > 0.5  # Should be reasonably similar
            
            self.log_test("User Similarity Computation", True, 
                         f"Computed similarity: {similarity:.3f}")
            
        except Exception as e:
            self.log_test("User Similarity Computation", False, str(e))
    
    async def test_gnn_agent_basic(self):
        """Test basic GNN agent functionality"""
        try:
            agent = GNNAgent()
            
            # Test initialization
            assert agent.knowledge_graph is not None
            assert agent.model is not None
            assert agent.user_profile_modeler is not None
            assert not agent.trained
            
            # Test user addition
            user_profile = {
                'user_id': 'test_user_001',
                'demographics': {'age': 28, 'nationality': 'US', 'income_level': 'mid'},
                'travel_preferences': {'budget_range': 'mid', 'travel_style': 'adventure', 'preferred_activities': ['culture']},
                'travel_history': {'previous_destinations': ['Paris'], 'total_trips': 5},
                'interests_and_lifestyle': {'interests': ['culture'], 'dietary_restrictions': []},
                'social_and_behavioral': {'group_travel_preference': 'couple', 'social_media_activity': 'moderate'}
            }
            
            agent.add_user_to_graph(user_profile)
            
            # Verify user was added
            assert 'test_user_001' in agent.knowledge_graph.entities
            user_entity = agent.knowledge_graph.entities['test_user_001']
            assert user_entity.entity_type == 'user'
            assert user_entity.embedding is not None
            
            # Test destination addition
            destination_data = {
                'destination_id': 'test_dest_001',
                'name': 'Test City',
                'latitude': 40.7128,
                'longitude': -74.0060,
                'popularity': 0.8,
                'avg_rating': 4.5,
                'price_level': 0.6
            }
            
            agent.add_destination_to_graph(destination_data)
            assert 'test_dest_001' in agent.knowledge_graph.entities
            
            # Test interaction addition
            agent.add_interaction('test_user_001', 'test_dest_001', 'visited', 4.5)
            assert len(agent.knowledge_graph.edges) == 1
            
            self.log_test("GNN Agent Basic Operations", True, 
                         f"Added {len(agent.knowledge_graph.entities)} entities")
            
        except Exception as e:
            self.log_test("GNN Agent Basic Operations", False, str(e))
    
    async def test_recommendation_generation(self):
        """Test recommendation generation"""
        try:
            agent = GNNAgent()
            
            # Add sample data
            destinations, hotels, interactions = create_sample_travel_data()
            
            for dest in destinations:
                agent.add_destination_to_graph(dest)
            
            # Generate recommendations
            start_time = time.time()
            recommendations = await agent.generate_recommendations(
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
            response_time = time.time() - start_time
            
            # Verify recommendations
            assert recommendations['status'] == 'success'
            assert 'recommendations' in recommendations
            assert 'personalization_score' in recommendations
            assert recommendations['personalization_score'] > 0
            
            # Check recommendation structure
            recs = recommendations['recommendations']
            assert isinstance(recs, dict)
            
            rec_count = sum(len(rec_list) for rec_list in recs.values())
            
            self.log_test("Recommendation Generation", True, 
                         f"Generated {rec_count} recommendations in {response_time:.3f}s")
            
        except Exception as e:
            self.log_test("Recommendation Generation", False, str(e))
    
    async def test_performance_stress(self):
        """Test performance with larger datasets"""
        try:
            agent = GNNAgent()
            
            # Add many entities to test scalability
            num_users = 50
            num_destinations = 25
            num_interactions = 100
            
            start_time = time.time()
            
            # Add users
            for i in range(num_users):
                user_profile = {
                    'user_id': f'perf_user_{i:03d}',
                    'demographics': {'age': 25 + (i % 40), 'nationality': 'US', 'income_level': 'mid'},
                    'travel_preferences': {'budget_range': 'mid', 'travel_style': 'adventure', 'preferred_activities': ['culture']},
                    'travel_history': {'previous_destinations': ['Paris'], 'total_trips': 5},
                    'interests_and_lifestyle': {'interests': ['culture'], 'dietary_restrictions': []},
                    'social_and_behavioral': {'group_travel_preference': 'couple', 'social_media_activity': 'moderate'}
                }
                agent.add_user_to_graph(user_profile)
            
            # Add destinations
            for i in range(num_destinations):
                dest_data = {
                    'destination_id': f'perf_dest_{i:03d}',
                    'name': f'Performance Destination {i}',
                    'latitude': 40.0 + (i % 20),
                    'longitude': -74.0 + (i % 20),
                    'popularity': 0.5 + (i % 5) * 0.1,
                    'avg_rating': 3.5 + (i % 3) * 0.5,
                    'price_level': 0.3 + (i % 4) * 0.2
                }
                agent.add_destination_to_graph(dest_data)
            
            # Add interactions
            for i in range(num_interactions):
                user_id = f'perf_user_{i % num_users:03d}'
                dest_id = f'perf_dest_{i % num_destinations:03d}'
                rating = 3.0 + (i % 3)
                agent.add_interaction(user_id, dest_id, 'visited', rating)
            
            graph_building_time = time.time() - start_time
            
            # Test knowledge graph conversion
            conversion_start = time.time()
            kg_data = agent.knowledge_graph.build_pytorch_geometric_data()
            conversion_time = time.time() - conversion_start
            
            # Performance checks
            total_time = graph_building_time + conversion_time
            
            assert total_time < 15.0  # Should complete within 15 seconds
            assert len(agent.knowledge_graph.entities) == num_users + num_destinations
            assert len(agent.knowledge_graph.edges) == num_interactions
            
            self.log_test("Performance Stress Test", True, 
                         f"Processed {len(agent.knowledge_graph.entities)} entities and {len(agent.knowledge_graph.edges)} edges in {total_time:.2f}s")
            
        except Exception as e:
            self.log_test("Performance Stress Test", False, str(e))
    
    async def test_end_to_end_integration(self):
        """Test complete end-to-end workflow"""
        try:
            agent = GNNAgent()
            
            # Step 1: Create sample travel data
            destinations, hotels, interactions = create_sample_travel_data()
            
            # Step 2: Build knowledge graph
            for dest in destinations:
                agent.add_destination_to_graph(dest)
            
            # Step 3: Add users
            sample_users = [
                {
                    'user_id': 'e2e_user_001',
                    'demographics': {'age': 28, 'nationality': 'US', 'income_level': 'mid'},
                    'travel_preferences': {'budget_range': 'mid', 'travel_style': 'adventure', 'preferred_activities': ['culture']},
                    'travel_history': {'previous_destinations': ['Paris'], 'total_trips': 5},
                    'interests_and_lifestyle': {'interests': ['culture'], 'dietary_restrictions': []},
                    'social_and_behavioral': {'group_travel_preference': 'couple', 'social_media_activity': 'moderate'}
                },
                {
                    'user_id': 'e2e_user_002',
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
            recommendation_count = 0
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
                
                assert recommendations['status'] == 'success'
                assert 'recommendations' in recommendations
                recommendation_count += sum(len(recs) for recs in recommendations['recommendations'].values())
            
            # Step 6: Test feedback integration
            agent.update_from_feedback('e2e_user_001', 'dest_001', 4.8)
            
            # Verify feedback was added
            feedback_edges = [e for e in agent.knowledge_graph.edges 
                             if e.source_id == 'e2e_user_001' and e.target_id == 'dest_001']
            assert len(feedback_edges) > 0
            
            self.log_test("End-to-End Integration", True, 
                         f"Generated {recommendation_count} total recommendations, feedback integration successful")
            
        except Exception as e:
            self.log_test("End-to-End Integration", False, str(e))
    
    async def run_all_tests(self):
        """Run all comprehensive tests"""
        print("🧪 Starting Comprehensive GNN Test Suite...")
        print("=" * 60)
        
        # Basic functionality tests
        print("\n📋 Basic Functionality Tests:")
        self.test_knowledge_graph_basic()
        self.test_pytorch_geometric_conversion()
        self.test_model_architecture()
        self.test_user_profile_features()
        self.test_user_similarity()
        
        # Agent tests
        print("\n🤖 GNN Agent Tests:")
        await self.test_gnn_agent_basic()
        await self.test_recommendation_generation()
        
        # Performance tests
        print("\n⚡ Performance Tests:")
        await self.test_performance_stress()
        
        # Integration tests
        print("\n🔗 Integration Tests:")
        await self.test_end_to_end_integration()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 Test Summary:")
        print(f"✅ Tests Passed: {self.tests_passed}")
        print(f"❌ Tests Failed: {self.tests_failed}")
        print(f"📈 Success Rate: {self.tests_passed / (self.tests_passed + self.tests_failed) * 100:.1f}%")
        
        if self.tests_failed == 0:
            print("\n🎉 All tests passed successfully!")
            print("✅ GNN implementation is working correctly")
        else:
            print(f"\n⚠️  {self.tests_failed} test(s) failed. Please check the errors above.")
        
        return self.tests_failed == 0


async def main():
    """Main test runner"""
    try:
        test_suite = GNNTestSuite()
        success = await test_suite.run_all_tests()
        return success
    except Exception as e:
        print(f"❌ Test suite failed with error: {e}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit_code = 0 if success else 1
    sys.exit(exit_code)