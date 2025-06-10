import asyncio
import json
import time
from aiohttp import web, ClientError
from typing import Dict, Any
from models.cached_hybrid_recommender import CachedHybridRecommender

class RecommendationAPI:
    def __init__(self, host: str = "localhost", port: int = 8000):
        self.host = host
        self.port = port
        self.recommender = CachedHybridRecommender()
        self.app = self._create_app()
        self.request_count = 0
        self.start_time = time.time()
    
    def _create_app(self):
        app = web.Application()
        
        app.router.add_get('/health', self.health_check)
        app.router.add_get('/recommendations/{user_id}', self.get_recommendations)
        app.router.add_post('/interactions', self.record_interaction)
        app.router.add_get('/similar/{item_id}', self.get_similar_items)
        app.router.add_get('/popular', self.get_popular_items)
        app.router.add_get('/stats', self.get_system_stats)
        
        return app
    
    async def initialize(self, interactions: list, items_data: list):
        await self.recommender.initialize(interactions, items_data)
        print(f"Recommendation API initialized on {self.host}:{self.port}")
    
    async def start(self):
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        print(f"Server started on http://{self.host}:{self.port}")
    
    async def health_check(self, request):
        return web.json_response({
            "status": "healthy",
            "service": "recommendation-engine",
            "uptime_seconds": int(time.time() - self.start_time),
            "requests_served": self.request_count
        })
    
    async def get_recommendations(self, request):
        start_time = time.time()
        self.request_count += 1
        
        try:
            user_id = request.match_info['user_id']
            num_recs = int(request.query.get('count', 5))
            
            if num_recs > 50:
                return web.json_response({
                    "error": "Maximum 50 recommendations allowed"
                }, status=400)
            
            result = await self.recommender.get_recommendations(user_id, num_recs)
            
            response_time = (time.time() - start_time) * 1000
            result['api_response_time_ms'] = f"{response_time:.2f}"
            
            return web.json_response(result)
            
        except Exception as e:
            return web.json_response({
                "error": f"Failed to get recommendations: {str(e)}"
            }, status=500)
    
    async def record_interaction(self, request):
        start_time = time.time()
        self.request_count += 1
        
        try:
            data = await request.json()
            
            required_fields = ['user_id', 'item_id', 'rating']
            for field in required_fields:
                if field not in data:
                    return web.json_response({
                        "error": f"Missing required field: {field}"
                    }, status=400)
            
            user_id = data['user_id']
            item_id = data['item_id']
            rating = float(data['rating'])
            
            if not (1 <= rating <= 5):
                return web.json_response({
                    "error": "Rating must be between 1 and 5"
                }, status=400)
            
            result = await self.recommender.record_user_interaction(user_id, item_id, rating)
            
            response_time = (time.time() - start_time) * 1000
            result['api_response_time_ms'] = f"{response_time:.2f}"
            
            return web.json_response(result)
            
        except json.JSONDecodeError:
            return web.json_response({
                "error": "Invalid JSON in request body"
            }, status=400)
        except ValueError as e:
            return web.json_response({
                "error": f"Invalid data: {str(e)}"
            }, status=400)
        except Exception as e:
            return web.json_response({
                "error": f"Failed to record interaction: {str(e)}"
            }, status=500)
    
    async def get_similar_items(self, request):
        start_time = time.time()
        self.request_count += 1
        
        try:
            item_id = request.match_info['item_id']
            num_similar = int(request.query.get('count', 5))
            
            if num_similar > 20:
                return web.json_response({
                    "error": "Maximum 20 similar items allowed"
                }, status=400)
            
            result = await self.recommender.get_similar_items(item_id, num_similar)
            
            response_time = (time.time() - start_time) * 1000
            result['api_response_time_ms'] = f"{response_time:.2f}"
            
            return web.json_response(result)
            
        except Exception as e:
            return web.json_response({
                "error": f"Failed to get similar items: {str(e)}"
            }, status=500)
    
    async def get_popular_items(self, request):
        start_time = time.time()
        self.request_count += 1
        
        try:
            category = request.query.get('category', 'all')
            num_items = int(request.query.get('count', 10))
            
            if num_items > 50:
                return web.json_response({
                    "error": "Maximum 50 popular items allowed"
                }, status=400)
            
            result = await self.recommender.get_popular_items(category, num_items)
            
            response_time = (time.time() - start_time) * 1000
            result['api_response_time_ms'] = f"{response_time:.2f}"
            
            return web.json_response(result)
            
        except Exception as e:
            return web.json_response({
                "error": f"Failed to get popular items: {str(e)}"
            }, status=500)
    
    async def get_system_stats(self, request):
        try:
            performance_stats = self.recommender.get_performance_stats()
            
            system_stats = {
                "service_uptime_seconds": int(time.time() - self.start_time),
                "total_api_requests": self.request_count,
                "performance": performance_stats
            }
            
            return web.json_response(system_stats)
            
        except Exception as e:
            return web.json_response({
                "error": f"Failed to get stats: {str(e)}"
            }, status=500)
    
    async def close(self):
        await self.recommender.close()