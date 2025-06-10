import asyncio
import time
from cache.memory_cache import MemoryCache

async def test_cache_system():
    print("=== Testing Memory Cache ===")
    
    cache = MemoryCache()
    await cache.connect()
    
    print("\n1. Testing user recommendations cache:")
    
    user_recs = [("iphone", 0.9, "hybrid"), ("macbook", 0.8, "content"), ("ipad", 0.7, "content")]
    
    start_time = time.time()
    await cache.set_user_recommendations("alice", user_recs, ttl=300)
    print(f"Set recommendations: {(time.time() - start_time)*1000:.1f}ms")
    
    start_time = time.time()
    cached_recs = await cache.get_user_recommendations("alice")
    print(f"Get recommendations (should be cached): {(time.time() - start_time)*1000:.1f}ms")
    print(f"Cached data: {cached_recs}")
    
    print("\n2. Testing cache miss:")
    start_time = time.time()
    missing_recs = await cache.get_user_recommendations("bob")
    print(f"Get recommendations (cache miss): {(time.time() - start_time)*1000:.1f}ms")
    print(f"Result: {missing_recs}")
    
    print("\n3. Testing user interactions:")
    await cache.update_user_interaction("alice", "gaming_chair", 4.0)
    await cache.update_user_interaction("alice", "coffee_maker", 3.0)
    
    interactions = await cache.get_user_interactions("alice")
    print(f"Alice's interactions: {interactions}")
    
    print("\n4. Testing cache invalidation:")
    cached_after_interaction = await cache.get_user_recommendations("alice")
    print(f"Alice's recs after interaction (should be None): {cached_after_interaction}")
    
    print("\n5. Testing item similarity cache:")
    similar_items = [("macbook", 0.8), ("ipad", 0.7), ("airpods", 0.6)]
    await cache.set_item_similarity("iphone", similar_items, ttl=86400)
    
    cached_similar = await cache.get_item_similarity("iphone")
    print(f"Similar to iPhone: {cached_similar}")
    
    print("\n6. Cache statistics:")
    stats = cache.get_cache_stats()
    print(f"Cache stats: {stats}")
    
    await cache.close()

if __name__ == "__main__":
    asyncio.run(test_cache_system())