from models.content_based import ContentBasedFilter

def test_content_filtering():
    print("=== Testing Content-Based Filtering ===")
    
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
    
    alice_interactions = [
        {"item_id": "iphone", "rating": 5},
        {"item_id": "macbook", "rating": 4},
        {"item_id": "coffee_maker", "rating": 3},
    ]
    
    dave_interactions = [
        {"item_id": "iphone", "rating": 1},
        {"item_id": "cookbook", "rating": 5},
        {"item_id": "kitchen_knife", "rating": 4},
    ]
    
    content_filter = ContentBasedFilter()
    content_filter.fit(items_data)
    
    print("\nContent-based recommendations for Alice:")
    alice_recs = content_filter.get_recommendations(alice_interactions, 3)
    for item, score in alice_recs:
        print(f"  {item}: {score:.3f}")
    
    print("\nContent-based recommendations for Dave:")
    dave_recs = content_filter.get_recommendations(dave_interactions, 3)
    for item, score in dave_recs:
        print(f"  {item}: {score:.3f}")
    
    print("\nItems similar to iPhone:")
    similar_to_iphone = content_filter.get_similar_items("iphone", 3)
    for item, score in similar_to_iphone:
        print(f"  {item}: {score:.3f}")

if __name__ == "__main__":
    test_content_filtering()