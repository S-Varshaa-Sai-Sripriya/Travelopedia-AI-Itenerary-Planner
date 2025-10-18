#!/usr/bin/env python3
"""
Test GNN Training and Trained Model Recommendations

This script tests the enhanced GNN training functionality and verifies 
that trained models provide real GNN-based recommendations instead of fallback mode.
"""

import sys
import asyncio
import time
from pathlib import Path

# Add app directory to path
sys.path.append(str(Path.cwd() / "app"))

from agents.gnn_agent import GNNAgent, create_sample_travel_data


async def test_gnn_training_and_recommendations():
    """Test GNN training and recommendation generation"""
    
    print("🧠 Testing GNN Training and Trained Model Recommendations...")
    print("=" * 70)
    
    # Initialize GNN agent
    agent = GNNAgent()
    print("✅ GNN Agent initialized")
    
    # Create comprehensive sample data
    destinations, hotels, interactions = create_sample_travel_data()
    print(f"📊 Created sample data: {len(destinations)} destinations, {len(hotels)} hotels, {len(interactions)} interactions")
    
    # Add destinations to knowledge graph
    for dest in destinations:
        agent.add_destination_to_graph(dest)
    print("🗺️ Added destinations to knowledge graph")
    
    # Add sample users with rich profiles
    sample_users = [
        {
            'user_id': 'training_user_001',
            'demographics': {'age': 28, 'nationality': 'US', 'income_level': 'mid'},
            'travel_preferences': {'budget_range': 'mid', 'travel_style': 'adventure', 'preferred_activities': ['culture', 'food']},
            'travel_history': {'previous_destinations': ['Paris'], 'total_trips': 5},
            'interests_and_lifestyle': {'interests': ['culture', 'food'], 'dietary_restrictions': []},
            'social_and_behavioral': {'group_travel_preference': 'couple', 'social_media_activity': 'moderate'}
        },
        {
            'user_id': 'training_user_002',
            'demographics': {'age': 35, 'nationality': 'UK', 'income_level': 'high'},
            'travel_preferences': {'budget_range': 'luxury', 'travel_style': 'relaxation', 'preferred_activities': ['spa', 'fine_dining']},
            'travel_history': {'previous_destinations': ['Tokyo', 'Bali'], 'total_trips': 8},
            'interests_and_lifestyle': {'interests': ['spa', 'fine_dining'], 'dietary_restrictions': ['vegetarian']},
            'social_and_behavioral': {'group_travel_preference': 'solo', 'social_media_activity': 'high'}
        },
        {
            'user_id': 'training_user_003',
            'demographics': {'age': 42, 'nationality': 'DE', 'income_level': 'high'},
            'travel_preferences': {'budget_range': 'luxury', 'travel_style': 'cultural', 'preferred_activities': ['art', 'history']},
            'travel_history': {'previous_destinations': ['Paris', 'Rome'], 'total_trips': 12},
            'interests_and_lifestyle': {'interests': ['art', 'history'], 'dietary_restrictions': []},
            'social_and_behavioral': {'group_travel_preference': 'family', 'social_media_activity': 'low'}
        }
    ]
    
    # Add users to knowledge graph
    for user in sample_users:
        agent.add_user_to_graph(user)
    print(f"👥 Added {len(sample_users)} users to knowledge graph")
    
    # Add interactions to create training data
    enhanced_interactions = [
        {'user_id': 'training_user_001', 'item_id': 'dest_001', 'type': 'visited', 'rating': 4.5},
        {'user_id': 'training_user_001', 'item_id': 'dest_003', 'type': 'visited', 'rating': 4.8},
        {'user_id': 'training_user_002', 'item_id': 'dest_001', 'type': 'visited', 'rating': 5.0},
        {'user_id': 'training_user_002', 'item_id': 'dest_002', 'type': 'visited', 'rating': 4.2},
        {'user_id': 'training_user_003', 'item_id': 'dest_001', 'type': 'visited', 'rating': 4.7},
        {'user_id': 'training_user_003', 'item_id': 'dest_002', 'type': 'visited', 'rating': 4.9},
        # Add preferences
        {'user_id': 'training_user_001', 'item_id': 'dest_001', 'type': 'prefers', 'rating': 4.0},
        {'user_id': 'training_user_002', 'item_id': 'dest_003', 'type': 'prefers', 'rating': 4.5},
        {'user_id': 'training_user_003', 'item_id': 'dest_002', 'type': 'prefers', 'rating': 4.8},
    ]
    
    for interaction in enhanced_interactions:
        agent.add_interaction(
            interaction['user_id'],
            interaction['item_id'],
            interaction['type'],
            interaction['rating']
        )
    
    print(f"🔗 Added {len(enhanced_interactions)} interactions for training")
    
    # Check initial training status
    print(f"\n📊 Initial Status:")
    print(f"   - Model trained: {agent.trained}")
    print(f"   - Knowledge graph entities: {len(agent.knowledge_graph.entities)}")
    print(f"   - Knowledge graph edges: {len(agent.knowledge_graph.edges)}")
    
    # Test recommendations BEFORE training (should trigger training)
    print(f"\n🎯 Testing Recommendations (Should Trigger Training)...")
    training_start_time = time.time()
    
    recommendations_before = await agent.generate_recommendations(
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
    
    training_time = time.time() - training_start_time
    
    print(f"⏱️ Time taken (including training): {training_time:.2f}s")
    print(f"🎯 Recommendations generated!")
    print(f"   - Status: {recommendations_before['status']}")
    print(f"   - Model type: {recommendations_before['model_type']}")
    print(f"   - Personalization score: {recommendations_before['personalization_score']}")
    print(f"   - Model trained after: {agent.trained}")
    
    # Count recommendations
    total_recs_before = sum(len(recs) for recs in recommendations_before['recommendations'].values())
    print(f"   - Total recommendations: {total_recs_before}")
    
    # Show sample recommendations
    for rec_type, recs in recommendations_before['recommendations'].items():
        if recs:
            best_rec = recs[0]
            print(f"   - Best {rec_type}: {best_rec['name']} (score: {best_rec['score']:.3f})")
    
    # Test recommendations AFTER training (should be faster and use trained model)
    print(f"\n🚀 Testing Recommendations with Trained Model...")
    inference_start_time = time.time()
    
    recommendations_after = await agent.generate_recommendations(
        user_id=2,
        user_preferences={
            'budget_range': 'luxury',
            'travel_style': 'relaxation',
            'interests': ['spa', 'fine_dining']
        },
        destination='Tokyo, Japan',
        trip_context={
            'trip_type': 'leisure',
            'duration': 7,
            'group_size': 1
        }
    )
    
    inference_time = time.time() - inference_start_time
    
    print(f"⏱️ Inference time (trained model): {inference_time:.3f}s")
    print(f"🎯 Recommendations generated!")
    print(f"   - Status: {recommendations_after['status']}")
    print(f"   - Model type: {recommendations_after['model_type']}")
    print(f"   - Personalization score: {recommendations_after['personalization_score']}")
    
    # Count recommendations
    total_recs_after = sum(len(recs) for recs in recommendations_after['recommendations'].values())
    print(f"   - Total recommendations: {total_recs_after}")
    
    # Show sample recommendations
    for rec_type, recs in recommendations_after['recommendations'].items():
        if recs:
            best_rec = recs[0]
            print(f"   - Best {rec_type}: {best_rec['name']} (score: {best_rec['score']:.3f})")
    
    # Test multiple recommendation requests for performance
    print(f"\n⚡ Performance Test with Trained Model...")
    performance_times = []
    
    for i in range(5):
        start_time = time.time()
        
        perf_recommendations = await agent.generate_recommendations(
            user_id=i + 10,
            user_preferences={
                'budget_range': 'mid',
                'travel_style': 'adventure',
                'interests': ['culture']
            },
            destination=f'Test City {i}',
            trip_context={
                'trip_type': 'leisure',
                'duration': 5,
                'group_size': 2
            }
        )
        
        request_time = time.time() - start_time
        performance_times.append(request_time)
        
        print(f"   - Request {i+1}: {request_time:.3f}s ({perf_recommendations['model_type']})")
    
    avg_performance = sum(performance_times) / len(performance_times)
    print(f"   - Average response time: {avg_performance:.3f}s")
    
    # Test feedback integration
    print(f"\n🔄 Testing Feedback Integration...")
    feedback_start_edges = len(agent.knowledge_graph.edges)
    
    agent.update_from_feedback('training_user_001', 'dest_001', 4.9)
    agent.update_from_feedback('training_user_002', 'dest_002', 3.8)
    
    feedback_end_edges = len(agent.knowledge_graph.edges)
    print(f"   - Edges before feedback: {feedback_start_edges}")
    print(f"   - Edges after feedback: {feedback_end_edges}")
    print(f"   - New feedback edges: {feedback_end_edges - feedback_start_edges}")
    
    # Final summary
    print(f"\n" + "=" * 70)
    print(f"📈 Training and Performance Summary:")
    print(f"✅ Model successfully trained: {agent.trained}")
    print(f"⚡ Training time: {training_time:.2f}s")
    print(f"🚀 Average inference time: {avg_performance:.3f}s")
    print(f"📊 Knowledge graph size: {len(agent.knowledge_graph.entities)} entities, {len(agent.knowledge_graph.edges)} edges")
    print(f"🎯 Model type: {recommendations_after['model_type']}")
    print(f"🎨 Personalization score: {recommendations_after['personalization_score']}")
    
    # Verify no more fallback warnings
    if "Graph Neural Network" in recommendations_after['model_type']:
        print(f"🎉 SUCCESS: GNN model is now trained and providing real recommendations!")
        print(f"✅ No more fallback mode warnings should appear")
        return True
    else:
        print(f"⚠️ WARNING: Still using fallback recommendations")
        return False


async def main():
    """Main test runner"""
    try:
        success = await test_gnn_training_and_recommendations()
        if success:
            print(f"\n🎉 All GNN training tests passed!")
            print(f"✅ GNN model training and inference working correctly")
        else:
            print(f"\n⚠️ Some issues found with GNN training")
        return success
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit_code = 0 if success else 1
    sys.exit(exit_code)