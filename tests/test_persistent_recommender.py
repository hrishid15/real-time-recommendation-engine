import asyncio
import sys
sys.path.append('..')
from models.persistent_cached_hybrid_recommender import PersistentCachedHybridRecommender

async def test_persistent_system():
    print("Testing Persistent Recommender")
    print("=" * 40)
    
    interactions = [
        {"user_id": "alice", "item_id": "iphone", "rating": 5},
        {"user_id": "alice", "item_id": "macbook", "rating": 4},
        {"user_id": "bob", "item_id": "iphone", "rating": 5},
        {"user_id": "bob", "item_id": "gaming_chair", "rating": 5},
    ]
    
    items_data = [
        {"item_id": "iphone", "category": "electronics", "brand": "apple", "description": "smartphone mobile phone"},
        {"item_id": "macbook", "category": "electronics", "brand": "apple", "description": "laptop computer"},
        {"item_id": "gaming_chair", "category": "furniture", "brand": "dxracer", "description": "chair gaming seat"},
        {"item_id": "airpods", "category": "electronics", "brand": "apple", "description": "headphones wireless music"},
    ]
    
    system = PersistentCachedHybridRecommender("test_persistent.db")
    await system.initialize(interactions, items_data)
    
    print("\n1. First request (cache miss):")
    result1 = await system.get_recommendations("alice", 3)
    print(f"Response time: {result1['response_time_ms']}ms")
    print(f"Source: {result1['source']}")
    print(f"Recommendations: {[r['item'] for r in result1['recommendations']]}")
    
    print("\n2. Second request (cache hit):")
    result2 = await system.get_recommendations("alice", 3)
    print(f"Response time: {result2['response_time_ms']}ms")
    print(f"Source: {result2['source']}")
    
    print("\n3. Recording new interaction:")
    interaction_result = await system.record_user_interaction("alice", "airpods", 4.0)
    print(f"Recorded in: {interaction_result['response_time_ms']}ms")
    print(f"Persisted: {interaction_result['persisted']}")
    
    print("\n4. Request after interaction (cache miss due to invalidation):")
    result3 = await system.get_recommendations("alice", 3)
    print(f"Response time: {result3['response_time_ms']}ms")
    print(f"Source: {result3['source']}")
    
    print("\n5. Testing similar items:")
    similar_result = await system.get_similar_items("iphone", 2)
    print(f"Similar to iPhone: {[item['item'] for item in similar_result['similar_items']]}")
    
    print("\n6. Performance stats:")
    stats = system.get_performance_stats()
    print(f"Cache hit rate: {stats['cache_hit_rate']}")
    print(f"Database connected: {stats['database_connected']}")
    
    await system.close()
    print("\nTest completed! Data saved to test_persistent.db")

if __name__ == "__main__":
    asyncio.run(test_persistent_system())