import numpy as np
from typing import Dict, List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class ContentBasedFilter:
    def __init__(self):
        self.item_features = {}
        self.item_similarity = None
        self.items = []
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.feature_matrix = None
    
    def fit(self, items_data: List[Dict]):
        self.items = [item['item_id'] for item in items_data]
        
        for item in items_data:
            self.item_features[item['item_id']] = item
        
        feature_texts = []
        for item in items_data:
            text = f"{item['category']} {item['brand']} {item['description']}"
            feature_texts.append(text)
        
        self.feature_matrix = self.vectorizer.fit_transform(feature_texts)
        self.item_similarity = cosine_similarity(self.feature_matrix)
        
        print(f"Content model trained with {len(items_data)} items")
    
    def get_recommendations(self, user_interactions: List[Dict], num_recommendations: int = 5) -> List[Tuple[str, float]]:
        if not user_interactions:
            return self._get_popular_items(num_recommendations)
        
        user_profile = self._build_user_profile(user_interactions)
        
        feature_matrix_dense = np.asarray(self.feature_matrix.todense())
        similarities = cosine_similarity(user_profile, feature_matrix_dense)[0]
        
        rated_items = {interaction['item_id'] for interaction in user_interactions}
        
        recommendations = []
        for i, item_id in enumerate(self.items):
            if item_id not in rated_items:
                recommendations.append((item_id, similarities[i]))
        
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations[:num_recommendations]
    
    def _build_user_profile(self, interactions: List[Dict]):
        liked_items = [interaction['item_id'] for interaction in interactions if interaction['rating'] >= 4]
        
        if not liked_items:
            return np.zeros((1, self.feature_matrix.shape[1]))
        
        liked_indices = [self.items.index(item) for item in liked_items if item in self.items]
        
        if not liked_indices:
            return np.zeros((1, self.feature_matrix.shape[1]))
        
        liked_features = self.feature_matrix[liked_indices]
        user_profile = np.mean(np.asarray(liked_features.todense()), axis=0)
        return user_profile.reshape(1, -1)
    
    def get_similar_items(self, item_id: str, num_similar: int = 5) -> List[Tuple[str, float]]:
        if item_id not in self.items:
            return []
        
        item_idx = self.items.index(item_id)
        similarities = self.item_similarity[item_idx]
        
        similar_items = []
        for i, similarity in enumerate(similarities):
            if i != item_idx:
                similar_items.append((self.items[i], similarity))
        
        similar_items.sort(key=lambda x: x[1], reverse=True)
        return similar_items[:num_similar]
    
    def _get_popular_items(self, num_items: int) -> List[Tuple[str, float]]:
        return [(item, 0.5) for item in self.items[:num_items]]