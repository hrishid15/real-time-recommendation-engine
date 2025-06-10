import time
from typing import Dict, List, Tuple, Optional
from .hybrid_recommender import HybridRecommender
from cache.memory_cache import MemoryCache

class CachedHybridRecommender:
    def __init__(self):
        self.recommender = HybridRecommender()
        self.cache = MemoryCache()
        self.performance_stats = {"cache_hits": 0, "cache_misses": 0, "avg_response_time": 0}
    
    async def initialize(self, interactions: List[Dict], items_data: List[Dict]):
        await self.cache.connect()
        self.recommender.fit(interactions, items_data)
        
        await self._precompute_popular_items(items_data)
        await self._precompute_item_similarities(items_data)
        
        print("Cached hybrid recommender initialized")
    
    async def get_recommendations(self, user_id: str, num_recommendations: int = 5) -> Dict:
        start_time = time.time()
        
        cached_recs = await self.cache.get_user_recommendations(user_id)
        
        if cached_recs:
            self.performance_stats["cache_hits"] += 1
            response_time = (time.time() - start_time) * 1000
            
            return {
                "recommendations": cached_recs[:num_recommendations],
                "user_id": user_id,
                "source": "cache",
                "response_time_ms": f"{response_time:.2f}",
                "timestamp": time.time()
            }
        
        self.performance_stats["cache_misses"] += 1
        
        user_interactions = await self.cache.get_user_interactions(user_id)
        
        recommendations = self.recommender.get_recommendations(
            user_id, user_interactions, num_recommendations * 2
        )
        
        await self.cache.set_user_recommendations(user_id, recommendations, ttl=300)
        
        response_time = (time.time() - start_time) * 1000
        
        return {
            "recommendations": [
                {"item": item, "score": score, "strategy": strategy}
                for item, score, strategy in recommendations[:num_recommendations]
            ],
            "user_id": user_id,
            "source": "computed",
            "response_time_ms": f"{response_time:.2f}",
            "timestamp": time.time()
        }
    
    async def record_user_interaction(self, user_id: str, item_id: str, rating: float):
        start_time = time.time()
        
        await self.cache.update_user_interaction(user_id, item_id, rating)
        
        self.recommender.update_user_interaction(user_id, item_id, rating)
        
        response_time = (time.time() - start_time) * 1000
        
        return {
            "user_id": user_id,
            "item_id": item_id,
            "rating": rating,
            "status": "recorded",
            "cache_invalidated": True,
            "response_time_ms": f"{response_time:.2f}"
        }
    
    async def get_similar_items(self, item_id: str, num_similar: int = 5) -> Dict:
        start_time = time.time()
        
        cached_similar = await self.cache.get_item_similarity(item_id)
        
        if cached_similar:
            response_time = (time.time() - start_time) * 1000
            return {
                "item_id": item_id,
                "similar_items": cached_similar[:num_similar],
                "source": "cache",
                "response_time_ms": f"{response_time:.2f}"
            }
        
        similar_items = self.recommender.content_based.get_similar_items(item_id, num_similar * 2)
        
        await self.cache.set_item_similarity(item_id, similar_items, ttl=86400)
        
        response_time = (time.time() - start_time) * 1000
        
        return {
            "item_id": item_id,
            "similar_items": [
                {"item": item, "score": score}
                for item, score in similar_items[:num_similar]
            ],
            "source": "computed",
            "response_time_ms": f"{response_time:.2f}"
        }
    
    async def get_popular_items(self, category: str = "all", num_items: int = 10) -> Dict:
        start_time = time.time()
        
        cached_popular = await self.cache.get_popular_items(category)
        
        if cached_popular:
            response_time = (time.time() - start_time) * 1000
            return {
                "category": category,
                "popular_items": cached_popular[:num_items],
                "source": "cache",
                "response_time_ms": f"{response_time:.2f}"
            }
        
        popular_items = self.recommender.content_based._get_popular_items(num_items)
        
        await self.cache.set_popular_items(category, popular_items, ttl=1800)
        
        response_time = (time.time() - start_time) * 1000
        
        return {
            "category": category,
            "popular_items": [
                {"item": item, "score": score}
                for item, score in popular_items
            ],
            "source": "computed",
            "response_time_ms": f"{response_time:.2f}"
        }
    
    async def _precompute_popular_items(self, items_data: List[Dict]):
        categories = set(item["category"] for item in items_data)
        
        for category in categories:
            category_items = [
                (item["item_id"], 0.8) for item in items_data 
                if item["category"] == category
            ]
            await self.cache.set_popular_items(category, category_items, ttl=3600)
        
        all_items = [(item["item_id"], 0.7) for item in items_data]
        await self.cache.set_popular_items("all", all_items, ttl=3600)
    
    async def _precompute_item_similarities(self, items_data: List[Dict]):
        for item in items_data:
            item_id = item["item_id"]
            similar_items = self.recommender.content_based.get_similar_items(item_id, 10)
            await self.cache.set_item_similarity(item_id, similar_items, ttl=86400)
    
    def get_performance_stats(self) -> Dict:
        cache_stats = self.cache.get_cache_stats()
        total_requests = self.performance_stats["cache_hits"] + self.performance_stats["cache_misses"]
        
        return {
            "recommendation_requests": total_requests,
            "cache_hit_rate": cache_stats["hit_rate"],
            "cache_performance": cache_stats,
            "system_performance": self.performance_stats
        }
    
    async def close(self):
        await self.cache.close()