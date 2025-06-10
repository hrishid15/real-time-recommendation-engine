from models.collaborative_filtering import CollaborativeFilter

def test_basic_recommendations():
    print("=== Testing Collaborative Filtering ===")
    
    sample_data = [
        {"user_id": "alice", "item_id": "iphone", "rating": 5},
        {"user_id": "alice", "item_id": "macbook", "rating": 4},
        {"user_id": "alice", "item_id": "coffee_maker", "rating": 3},
        
        {"user_id": "bob", "item_id": "iphone", "rating": 5},
        {"user_id": "bob", "item_id": "macbook", "rating": 4},
        {"user_id": "bob", "item_id": "gaming_chair", "rating": 5},
        
        {"user_id": "carol", "item_id": "coffee_maker", "rating": 4},
        {"user_id": "carol", "item_id": "kitchen_knife", "rating": 5},
        {"user_id": "carol", "item_id": "cookbook", "rating": 4},
        
        {"user_id": "dave", "item_id": "iphone", "rating": 1},
        {"user_id": "dave", "item_id": "cookbook", "rating": 5},
        {"user_id": "dave", "item_id": "kitchen_knife", "rating": 4},
    ]
    
    recommender = CollaborativeFilter()
    recommender.fit(sample_data)
    
    print("\nRecommendations for Alice:")
    alice_recs = recommender.get_recommendations("alice", 3)
    for item, score in alice_recs:
        print(f"  {item}: {score:.2f}")
    
    print("\nRecommendations for Bob:")
    bob_recs = recommender.get_recommendations("bob", 3)
    for item, score in bob_recs:
        print(f"  {item}: {score:.2f}")
    
    print("\nRecommendations for new user:")
    new_user_recs = recommender.get_recommendations("unknown_user", 3)
    for item, score in new_user_recs:
        print(f"  {item}: {score:.2f}")

    print("\nRecommendations for Dave:")
    dave_recs = recommender.get_recommendations("dave", 3)
    for item, score in dave_recs:
        print(f"  {item}: {score:.2f}")

if __name__ == "__main__":
    test_basic_recommendations()