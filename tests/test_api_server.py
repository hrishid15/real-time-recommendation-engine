import asyncio
from api.recommendation_server import RecommendationAPI

async def run_server():
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
    
    api = RecommendationAPI(port=8000)
    await api.initialize(interactions, items_data)
    await api.start()
    
    print("\nAPI Server is running! Try these commands in another terminal:")
    print("curl http://localhost:8000/health")
    print("curl http://localhost:8000/recommendations/alice")
    print("curl http://localhost:8000/similar/iphone")
    print("curl http://localhost:8000/popular?category=electronics")
    print("curl -X POST http://localhost:8000/interactions -H 'Content-Type: application/json' -d '{\"user_id\": \"alice\", \"item_id\": \"gaming_chair\", \"rating\": 5}'")
    print("curl http://localhost:8000/stats")
    
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down server...")
        await api.close()

if __name__ == "__main__":
    asyncio.run(run_server())