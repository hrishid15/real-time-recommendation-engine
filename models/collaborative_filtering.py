import numpy as np
from typing import Dict, List, Tuple
import pandas as pd

class CollaborativeFilter:
    def __init__(self):
        self.user_item_matrix = None
        self.user_similarity = None
        self.users = {}
        self.items = {}
    
    def fit(self, interactions: List[Dict]):
        df = pd.DataFrame(interactions)
        
        unique_users = df['user_id'].unique()
        unique_items = df['item_id'].unique()
        
        self.users = {user: idx for idx, user in enumerate(unique_users)}
        self.items = {item: idx for idx, item in enumerate(unique_items)}
        
        n_users = len(unique_users)
        n_items = len(unique_items)
        self.user_item_matrix = np.zeros((n_users, n_items))
        
        for _, row in df.iterrows():
            user_idx = self.users[row['user_id']]
            item_idx = self.items[row['item_id']]
            self.user_item_matrix[user_idx, item_idx] = row['rating']
        
        self._calculate_user_similarity()
        
        print(f"Model trained with {n_users} users and {n_items} items")
    
    def _calculate_user_similarity(self):
        from sklearn.metrics.pairwise import cosine_similarity
        
        user_norms = np.linalg.norm(self.user_item_matrix, axis=1)
        user_norms[user_norms == 0] = 1
        
        self.user_similarity = cosine_similarity(self.user_item_matrix)
    
    def get_recommendations(self, user_id: str, num_recommendations: int = 5) -> List[Tuple[str, float]]:
        if user_id not in self.users:
            return self._get_popular_items(num_recommendations)
        
        user_idx = self.users[user_id]
        user_ratings = self.user_item_matrix[user_idx]
        
        similarities = self.user_similarity[user_idx]
        
        unrated_items = np.where(user_ratings == 0)[0]
        
        recommendations = []
        
        for item_idx in unrated_items:
            predicted_rating = self._predict_rating(user_idx, item_idx, similarities)
            
            if predicted_rating > 0:
                item_id = self._get_item_id(item_idx)
                recommendations.append((item_id, predicted_rating))
        
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations[:num_recommendations]
    
    def _predict_rating(self, user_idx: int, item_idx: int, similarities: np.ndarray) -> float:
        rated_users = np.where(self.user_item_matrix[:, item_idx] > 0)[0]
        
        if len(rated_users) == 0:
            return 0.0
        
        numerator = 0
        denominator = 0
        
        for other_user in rated_users:
            if other_user != user_idx:
                similarity = similarities[other_user]
                rating = self.user_item_matrix[other_user, item_idx]
                
                numerator += similarity * rating
                denominator += abs(similarity)
        
        return numerator / denominator if denominator > 0 else 0.0
    
    def _get_popular_items(self, num_items: int) -> List[Tuple[str, float]]:
        if self.user_item_matrix is None:
            return []
        
        item_ratings = np.mean(self.user_item_matrix, axis=0)
        top_items = np.argsort(item_ratings)[::-1][:num_items]
        
        return [(self._get_item_id(idx), item_ratings[idx]) for idx in top_items if item_ratings[idx] > 0]
    
    def _get_item_id(self, item_idx: int) -> str:
        for item_id, idx in self.items.items():
            if idx == item_idx:
                return item_id
        return ""