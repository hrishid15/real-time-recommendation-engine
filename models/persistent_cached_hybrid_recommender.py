import time
from typing import Dict, List, Tuple, Optional
from models.hybrid_recommender import HybridRecommender
from cache.memory_cache import MemoryCache
from database.database_manager import DatabaseManager

class PersistentCachedHybridRecommender:
    def __init__(self, db_path: str = "recommendation_engine.db"):
        self.recommender = HybridRecommender()
        self.cache = MemoryCache()
        self.db = DatabaseManager(db_path)
        self.performance_stats = {"cache_hits": 0, "cache_misses": 0}
    
    async def initialize(self, interactions: List[Dict] = None, items_data: List[Dict] = None):
        await self.db.initialize()
        await self.cache.connect()
        
        if items_data:
            for item in items_data:
                await self.db.create_or_update_item(item)
        
        if interactions:
            for interaction in interactions:
                await self.db.record_interaction(
                    interaction['user_id'],
                    interaction['item_id'],
                    interaction['rating']
                )
        
        await self._load_and_train_from_database()
        await self._precompute_popular_items()
        await self._precompute_item_similarities()
        
        print("Persistent cached hybrid recommender initialized")
    
    async def _load_and_train_from_database(self):
        interactions = await self.db.get_all_interactions()
        items_data = []
        
        all_items = await self.db.get_all_items()
        for item in all_items:
            items_data.append({
                "item_id": item["item_id"],
                "category": item["category"],
                "brand": item["brand"],
                "description": item["description"]
            })
        
        if interactions and items_data:
            ml_interactions = [
                {
                    "user_id": interaction["user_id"],
                    "item_id": interaction["item_id"],
                    "rating": interaction["rating"]
                }
                for interaction in interactions
            ]
            
            self.recommender.fit(ml_interactions, items_data)
            print(f"Trained models with {len(ml_interactions)} interactions and {len(items_data)} items")
        else:
            print("No data found in database")
    
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
        
        user_interactions = await self.db.get_user_interactions(user_id, limit=50)
        
        ml_interactions = [
            {
                "item_id": interaction["item_id"],
                "rating": interaction["rating"]
            }
            for interaction in user_interactions
        ]
        
        recommendations = self.recommender.get_recommendations(
            user_id, ml_interactions, num_recommendations * 2
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
        
        await self.db.record_interaction(user_id, item_id, rating)
        await self.cache.update_user_interaction(user_id, item_id, rating)
        self.recommender.update_user_interaction(user_id, item_id, rating)
        
        response_time = (time.time() - start_time) * 1000
        
        return {
            "user_id": user_id,
            "item_id": item_id,
            "rating": rating,
            "status": "recorded",
            "cache_invalidated": True,
            "persisted": True,
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
        
        items = await self.db.get_all_items()
        
        if category != "all":
            items = [item for item in items if item["category"] == category]
        
        popular_items = [
            (item["item_id"], item["current_avg_rating"] * (1 + item["current_rating_count"] * 0.1))
            for item in items
        ]
        popular_items.sort(key=lambda x: x[1], reverse=True)
        
        await self.cache.set_popular_items(category, popular_items, ttl=1800)
        
        response_time = (time.time() - start_time) * 1000
        
        return {
            "category": category,
            "popular_items": [
                {"item": item, "score": score}
                for item, score in popular_items[:num_items]
            ],
            "source": "computed",
            "response_time_ms": f"{response_time:.2f}"
        }
    
    async def _precompute_popular_items(self):
        items = await self.db.get_all_items()
        categories = set(item["category"] for item in items)
        
        for category in categories:
            category_items = [item for item in items if item["category"] == category]
            popular = [
                (item["item_id"], item["current_avg_rating"] * (1 + item["current_rating_count"] * 0.1))
                for item in category_items
            ]
            popular.sort(key=lambda x: x[1], reverse=True)
            await self.cache.set_popular_items(category, popular, ttl=3600)
        
        all_popular = [
            (item["item_id"], item["current_avg_rating"] * (1 + item["current_rating_count"] * 0.1))
            for item in items
        ]
        all_popular.sort(key=lambda x: x[1], reverse=True)
        await self.cache.set_popular_items("all", all_popular, ttl=3600)
    
    async def _precompute_item_similarities(self):
        items = await self.db.get_all_items()
        
        for item in items:
            item_id = item["item_id"]
            if hasattr(self.recommender.content_based, 'items') and item_id in self.recommender.content_based.items:
                similar_items = self.recommender.content_based.get_similar_items(item_id, 10)
                await self.cache.set_item_similarity(item_id, similar_items, ttl=86400)
    
    def get_performance_stats(self) -> Dict:
        cache_stats = self.cache.get_cache_stats()
        total_requests = self.performance_stats["cache_hits"] + self.performance_stats["cache_misses"]
        
        return {
            "recommendation_requests": total_requests,
            "cache_hit_rate": cache_stats["hit_rate"],
            "cache_performance": cache_stats,
            "system_performance": self.performance_stats,
            "database_connected": self.db.connection is not None
        }
    
    async def close(self):
        await self.cache.close()
        await self.db.close()