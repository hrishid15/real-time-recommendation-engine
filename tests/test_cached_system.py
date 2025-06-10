import asyncio
import time
from models.cached_hybrid_recommender import CachedHybridRecommender

async def test_performance_system():
    print("=== Testing Cached Hybrid Recommendation System ===")
    
    interactions = [
        {"user_id": "alice", "item_id": "iphone", "rating": 5},
        {"user_id": "alice", "item_id": "macbook", "rating": 4},
        {"user_id": "alice", "item_id": "coffee_maker", "rating": 3},
        
        {"user_id": "bob", "item_id": "iphone", "rating": 5},
        {"user_id": "bob", "item_id": "macbook", "rating": 4},
        {"user_id": "bob", "item_id": "gaming_chair", "rating": 5},
        
        {"user_id": "carol", "item_id": "coffee_maker", "rating": 4},
        {"user_id": "carol", "item_id": "kitchen_knife", "rating": 5},
        {"user_id": "carol", "item_id": "cookbook", "rating": 4},
    ]
    
    items_data = [
        {"item_id": "iphone", "category": "electronics", "brand": "apple", "description": "smartphone mobile phone"},
        {"item_id": "macbook", "category": "electronics", "brand": "apple", "description": "laptop computer"},
        {"item_id": "gaming_chair", "category": "furniture", "brand": "dxracer", "description": "chair gaming seat"},
        {"item_id": "coffee_maker", "category": "kitchen", "brand": "cuisinart", "description": "coffee machine brewing"},
        {"item_id": "kitchen_knife", "category": "kitchen", "brand": "henckels", "description": "knife cutting cooking"},
        {"item_id": "cookbook", "category": "books", "brand": "penguin", "description": "recipes cooking food"},
        {"item_id": "airpods", "category": "electronics", "brand": "apple", "description": "headphones wireless music"},
        {"item_id": "ipad", "category": "electronics", "brand": "apple", "description": "tablet computer touch"},
    ]
    
    system = CachedHybridRecommender()
    await system.initialize(interactions, items_data)
    
    print("\n1. First request (cache miss):")
    result1 = await system.get_recommendations("alice", 5)
    print(f"Response time: {result1['response_time_ms']}ms")
    print(f"Source: {result1['source']}")
    print(f"Recommendations: {[r['item'] for r in result1['recommendations']]}")
    
    print("\n2. Second request (cache hit):")
    result2 = await system.get_recommendations("alice", 5)
    print(f"Response time: {result2['response_time_ms']}ms")
    print(f"Source: {result2['source']}")
    
    print("\n3. Request more items (should still be cache hit):")
    result3 = await system.get_recommendations("alice", 8)
    print(f"Response time: {result3['response_time_ms']}ms")
    print(f"Source: {result3['source']}")
    print(f"Got {len(result3['recommendations'])} recommendations")
    
    print("\n4. User interaction (invalidates cache):")
    interaction_result = await system.record_user_interaction("alice", "gaming_chair", 5.0)
    print(f"Interaction recorded in: {interaction_result['response_time_ms']}ms")
    print(f"Cache invalidated: {interaction_result['cache_invalidated']}")
    
    print("\n5. Request after interaction (cache miss again):")
    result4 = await system.get_recommendations("alice", 5)
    print(f"Response time: {result4['response_time_ms']}ms")
    print(f"Source: {result4['source']}")
    print(f"New recommendations: {[r['item'] for r in result4['recommendations']]}")
    
    print("\n6. Similar items (should be cached from precomputation):")
    similar_result = await system.get_similar_items("iphone", 3)
    print(f"Response time: {similar_result['response_time_ms']}ms")
    print(f"Source: {similar_result['source']}")
    print(f"Similar to iPhone: {[item['item'] for item in similar_result['similar_items']]}")
    
    print("\n7. Popular items (should be cached):")
    popular_result = await system.get_popular_items("electronics", 3)
    print(f"Response time: {popular_result['response_time_ms']}ms")
    print(f"Source: {popular_result['source']}")
    
    print("\n8. Performance statistics:")
    stats = system.get_performance_stats()
    print(f"Stats: {stats}")
    
    await system.close()

if __name__ == "__main__":
    asyncio.run(test_performance_system())