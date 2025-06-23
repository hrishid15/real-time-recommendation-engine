import asyncio
import sys
sys.path.append('..')
from database.database_manager import DatabaseManager

async def test_database():
    print("Testing Database Layer")
    print("=" * 40)
    
    db = DatabaseManager("test_recommendations.db")
    await db.initialize()
    
    print("\n1. Adding items to database...")
    items = [
        {"item_id": "iphone", "category": "electronics", "brand": "apple", "description": "smartphone mobile phone"},
        {"item_id": "macbook", "category": "electronics", "brand": "apple", "description": "laptop computer"},
        {"item_id": "coffee_maker", "category": "kitchen", "brand": "cuisinart", "description": "coffee machine brewing"},
    ]
    
    for item in items:
        await db.create_or_update_item(item)
    print(f"Added {len(items)} items")
    
    print("\n2. Recording user interactions...")
    interactions = [
        ("alice", "iphone", 5.0),
        ("alice", "macbook", 4.0),
        ("bob", "iphone", 5.0),
        ("bob", "coffee_maker", 3.0),
    ]
    
    for user_id, item_id, rating in interactions:
        await db.record_interaction(user_id, item_id, rating)
    print(f"Recorded {len(interactions)} interactions")
    
    print("\n3. Checking user information...")
    alice_stats = await db.get_user_stats("alice")
    print(f"Alice stats: {alice_stats}")
    
    bob_stats = await db.get_user_stats("bob")
    print(f"Bob stats: {bob_stats}")
    
    print("\n4. Getting user interactions...")
    alice_interactions = await db.get_user_interactions("alice")
    print(f"Alice's interactions: {alice_interactions}")
    
    print("\n5. Getting all items...")
    all_items = await db.get_all_items()
    for item in all_items:
        print(f"  {item['item_id']}: {item['current_avg_rating']:.1f}/5 ({item['current_rating_count']} ratings)")
    
    print("\n6. Getting all interactions for ML...")
    all_interactions = await db.get_all_interactions()
    print(f"Total interactions for ML: {len(all_interactions)}")
    
    await db.close()
    print("\nDatabase test completed!")
    print(f"Database saved as: test_recommendations.db")

if __name__ == "__main__":
    asyncio.run(test_database())