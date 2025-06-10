from models.hybrid_recommender import HybridRecommender

def test_hybrid_system():
    print("=== Testing Hybrid Recommendation System ===")
    
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
    
    hybrid = HybridRecommender()
    hybrid.fit(interactions, items_data)
    
    alice_interactions = [
        {"item_id": "iphone", "rating": 5},
        {"item_id": "macbook", "rating": 4},
        {"item_id": "coffee_maker", "rating": 3},
    ]
    
    print("\nAlice (hybrid strategy):")
    alice_recs = hybrid.get_recommendations("alice", alice_interactions, 4)
    for item, score, strategy in alice_recs:
        print(f"  {item}: {score:.3f} ({strategy})")
    
    print("\nNew user with one interaction (content strategy):")
    new_user_recs = hybrid.get_recommendations("new_user", [{"item_id": "iphone", "rating": 5}], 3)
    for item, score, strategy in new_user_recs:
        print(f"  {item}: {score:.3f} ({strategy})")
    
    print("\nBrand new user (popular strategy):")
    brand_new_recs = hybrid.get_recommendations("brand_new_user", [], 3)
    for item, score, strategy in brand_new_recs:
        print(f"  {item}: {score:.3f} ({strategy})")

if __name__ == "__main__":
    test_hybrid_system()