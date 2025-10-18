#!/usr/bin/env python3
"""
Test Enhanced GNN Implementation
"""

import sys
import asyncio
from pathlib import Path

# Add app directory to path
sys.path.append(str(Path(__file__).parent / "app"))

from app.agents.gnn_agent import GNNAgent, TravelKnowledgeGraph, GraphAttentionTravelNet, create_sample_travel_data
import torch
import torch.nn as nn


async def test_enhanced_gnn():
    """Test the enhanced GNN implementation"""
    print("🧠 Testing Enhanced GNN Implementation...")
    
    # Initialize GNN agent
    gnn_agent = GNNAgent()
    print("✅ GNN Agent initialized successfully")
    
    # Create sample travel data
    destinations, hotels, interactions = create_sample_travel_data()
    print(f"📊 Created sample data: {len(destinations)} destinations, {len(hotels)} hotels, {len(interactions)} interactions")
    
    # Add destinations to knowledge graph
    for dest in destinations:
        gnn_agent.add_destination_to_graph(dest)
    print("🗺️ Added destinations to knowledge graph")
    
    # Add sample user profiles (matching UserProfileModeler format)
    sample_users = [
        {
            'user_id': 'user_001',
            'demographics': {
                'age': 28,
                'nationality': 'US',
                'occupation': 'Software Engineer',
                'income_level': 'mid'
            },
            'travel_preferences': {
                'budget_range': 'mid',
                'travel_style': 'adventure',
                'accommodation_type': 'hotel',
                'preferred_activities': ['culture', 'food', 'photography']
            },
            'travel_history': {
                'previous_destinations': ['Paris', 'Tokyo'],
                'total_trips': 5,
                'avg_trip_duration': 7,
                'preferred_season': 'spring'
            },
            'interests_and_lifestyle': {
                'interests': ['culture', 'food', 'photography'],
                'dietary_restrictions': [],
                'accessibility_needs': []
            },
            'social_and_behavioral': {
                'group_travel_preference': 'couple',
                'social_media_activity': 'moderate',
                'review_writing_frequency': 'sometimes'
            }
        },
        {
            'user_id': 'user_002', 
            'demographics': {
                'age': 35,
                'nationality': 'UK',
                'occupation': 'Marketing Manager',
                'income_level': 'high'
            },
            'travel_preferences': {
                'budget_range': 'luxury',
                'travel_style': 'relaxation',
                'accommodation_type': 'resort',
                'preferred_activities': ['spa', 'fine_dining', 'art']
            },
            'travel_history': {
                'previous_destinations': ['Paris', 'Bali'],
                'total_trips': 8,
                'avg_trip_duration': 10,
                'preferred_season': 'summer'
            },
            'interests_and_lifestyle': {
                'interests': ['spa', 'fine_dining', 'art'],
                'dietary_restrictions': ['vegetarian'],
                'accessibility_needs': []
            },
            'social_and_behavioral': {
                'group_travel_preference': 'solo',
                'social_media_activity': 'high',
                'review_writing_frequency': 'often'
            }
        }
    ]
    
    for user in sample_users:
        gnn_agent.add_user_to_graph(user)
    print(f"👥 Added {len(sample_users)} users to knowledge graph")
    
    # Add interactions
    for interaction in interactions:
        gnn_agent.add_interaction(
            interaction['user_id'],
            interaction['item_id'],
            interaction['type'],
            interaction['rating']
        )
    print(f"🔗 Added {len(interactions)} interactions to knowledge graph")
    
    # Test knowledge graph conversion
    kg_data = gnn_agent.knowledge_graph.build_pytorch_geometric_data()
    print(f"📈 Knowledge graph converted to PyTorch Geometric format")
    print(f"   - Node types: {kg_data.node_types}")
    print(f"   - Edge types: {list(kg_data.edge_types)}")
    
    # Test model architecture
    model = gnn_agent.model
    print(f"🏗️ Model architecture: {model.__class__.__name__}")
    print(f"   - Input dim: {model.input_dim}")
    print(f"   - Hidden dim: {model.hidden_dim}")
    print(f"   - Output dim: {model.output_dim}")
    print(f"   - Attention heads: {model.num_heads}")
    print(f"   - GNN layers: {model.num_layers}")
    
    # Test forward pass (if we have data)
    try:
        if kg_data.node_types:
            print("🔄 Testing model forward pass...")
            model.eval()
            with torch.no_grad():
                embeddings = model(kg_data)
            print(f"✅ Forward pass successful. Generated embeddings for: {list(embeddings.keys())}")
            
            # Show embedding shapes
            for entity_type, emb in embeddings.items():
                print(f"   - {entity_type}: {emb.shape}")
        else:
            print("⚠️ No data in knowledge graph for forward pass test")
    except Exception as e:
        print(f"⚠️ Forward pass test failed: {e}")
    
    # Test recommendation generation
    print("\n🎯 Testing recommendation generation...")
    try:
        recommendations = await gnn_agent.generate_recommendations(
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
        
        print("✅ Recommendations generated successfully!")
        print(f"   - Status: {recommendations['status']}")
        print(f"   - Model type: {recommendations['model_type']}")
        print(f"   - Personalization score: {recommendations['personalization_score']}")
        
        if 'recommendations' in recommendations:
            for rec_type, recs in recommendations['recommendations'].items():
                print(f"   - {rec_type}: {len(recs)} recommendations")
                
    except Exception as e:
        print(f"❌ Recommendation generation failed: {e}")
    
    # Test user similarity computation
    print("\n👥 Testing user similarity computation...")
    try:
        user_profile_modeler = gnn_agent.user_profile_modeler
        
        user1_features = user_profile_modeler.generate_feature_vector(sample_users[0])
        user2_features = user_profile_modeler.generate_feature_vector(sample_users[1])
        
        similarity = user_profile_modeler.compute_user_similarity(user1_features, user2_features)
        print(f"✅ User similarity computed: {similarity:.3f}")
        
    except Exception as e:
        print(f"❌ User similarity computation failed: {e}")
    
    print("\n🎉 Enhanced GNN implementation test completed!")


if __name__ == "__main__":
    asyncio.run(test_enhanced_gnn())