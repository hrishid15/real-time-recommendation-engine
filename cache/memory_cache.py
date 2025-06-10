import asyncio
import json
import time
from typing import Dict, List, Tuple, Optional, Any

class MemoryCache:
    def __init__(self):
        self.cache = {}
        self.cache_stats = {"hits": 0, "misses": 0}
    
    async def connect(self):
        print("Using in-memory cache")
    
    async def close(self):
        pass
    
    async def get_user_recommendations(self, user_id: str) -> Optional[List[Dict]]:
        key = f"user_recs:{user_id}"
        
        if key in self.cache:
            data, expiry = self.cache[key]
            if time.time() < expiry:
                self.cache_stats["hits"] += 1
                return json.loads(data)
            else:
                del self.cache[key]
        
        self.cache_stats["misses"] += 1
        return None
    
    async def set_user_recommendations(self, user_id: str, recommendations: List[Tuple[str, float, str]], 
                                     ttl: int = 300):
        key = f"user_recs:{user_id}"
        data = [{"item": item, "score": score, "strategy": strategy} 
                for item, score, strategy in recommendations]
        
        self.cache[key] = (json.dumps(data), time.time() + ttl)
    
    async def get_user_profile(self, user_id: str) -> Optional[Dict]:
        key = f"user_profile:{user_id}"
        
        if key in self.cache:
            data, expiry = self.cache[key]
            if time.time() < expiry:
                self.cache_stats["hits"] += 1
                return json.loads(data)
            else:
                del self.cache[key]
        
        self.cache_stats["misses"] += 1
        return None
    
    async def set_user_profile(self, user_id: str, profile: Dict, ttl: int = 3600):
        key = f"user_profile:{user_id}"
        self.cache[key] = (json.dumps(profile), time.time() + ttl)
    
    async def get_item_similarity(self, item_id: str) -> Optional[List[Dict]]:
        key = f"item_sim:{item_id}"
        
        if key in self.cache:
            data, expiry = self.cache[key]
            if time.time() < expiry:
                self.cache_stats["hits"] += 1
                return json.loads(data)
            else:
                del self.cache[key]
        
        self.cache_stats["misses"] += 1
        return None
    
    async def set_item_similarity(self, item_id: str, similar_items: List[Tuple[str, float]], 
                                ttl: int = 86400):
        key = f"item_sim:{item_id}"
        data = [{"item": item, "score": score} for item, score in similar_items]
        self.cache[key] = (json.dumps(data), time.time() + ttl)
    
    async def invalidate_user_cache(self, user_id: str):
        keys_to_delete = [
            f"user_recs:{user_id}",
            f"user_profile:{user_id}"
        ]
        
        for key in keys_to_delete:
            if key in self.cache:
                del self.cache[key]
    
    async def update_user_interaction(self, user_id: str, item_id: str, rating: float):
        interaction_key = f"user_interactions:{user_id}"
        
        interactions = []
        if interaction_key in self.cache:
            data, expiry = self.cache[interaction_key]
            if time.time() < expiry:
                interactions = json.loads(data)
        
        interactions.append({
            "item_id": item_id,
            "rating": rating,
            "timestamp": time.time()
        })
        
        interactions = interactions[-50:]
        
        self.cache[interaction_key] = (json.dumps(interactions), time.time() + 7200)
        await self.invalidate_user_cache(user_id)
    
    async def get_user_interactions(self, user_id: str) -> List[Dict]:
        key = f"user_interactions:{user_id}"
        
        if key in self.cache:
            data, expiry = self.cache[key]
            if time.time() < expiry:
                return json.loads(data)
        
        return []
    
    def get_cache_stats(self) -> Dict[str, Any]:
        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = self.cache_stats["hits"] / total_requests if total_requests > 0 else 0
        
        return {
            "hits": self.cache_stats["hits"],
            "misses": self.cache_stats["misses"],
            "hit_rate": f"{hit_rate:.2%}",
            "cache_size": len(self.cache)
        }
    
    async def get_popular_items(self, category: str = "all") -> Optional[List[Dict]]:
        key = f"popular:{category}"
        
        if key in self.cache:
            data, expiry = self.cache[key]
            if time.time() < expiry:
                self.cache_stats["hits"] += 1
                return json.loads(data)
            else:
                del self.cache[key]
        
        self.cache_stats["misses"] += 1
        return None

    async def set_popular_items(self, category: str, items: List[Tuple[str, float]], 
                            ttl: int = 1800):
        key = f"popular:{category}"
        data = [{"item": item, "score": score} for item, score in items]
        self.cache[key] = (json.dumps(data), time.time() + ttl)