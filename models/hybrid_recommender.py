from typing import Dict, List, Tuple
from .collaborative_filtering import CollaborativeFilter
from .content_based import ContentBasedFilter

class HybridRecommender:
    def __init__(self):
        self.collaborative = CollaborativeFilter()
        self.content_based = ContentBasedFilter()
        self.is_trained = False
    
    def fit(self, interactions: List[Dict], items_data: List[Dict]):
        self.collaborative.fit(interactions)
        self.content_based.fit(items_data)
        self.is_trained = True
        print("Hybrid model trained successfully")
    
    def get_recommendations(self, user_id: str, user_interactions: List[Dict] = None, 
                          num_recommendations: int = 5) -> List[Tuple[str, float, str]]:
        if not self.is_trained:
            return []
        
        strategy = self._choose_strategy(user_id, user_interactions)
        
        if strategy == "collaborative":
            recs = self.collaborative.get_recommendations(user_id, num_recommendations)
            return [(item, score, "collaborative") for item, score in recs]
        
        elif strategy == "content":
            recs = self.content_based.get_recommendations(user_interactions or [], num_recommendations)
            return [(item, score, "content") for item, score in recs]
        
        elif strategy == "hybrid":
            return self._blend_recommendations(user_id, user_interactions, num_recommendations)
        
        else:
            return self._get_popular_fallback(num_recommendations)
    
    def _choose_strategy(self, user_id: str, user_interactions: List[Dict] = None) -> str:
        user_in_collab = user_id in self.collaborative.users if self.collaborative.users else False
        has_interactions = user_interactions and len(user_interactions) > 0
        
        if user_in_collab and has_interactions and len(user_interactions) >= 3:
            return "hybrid"
        elif user_in_collab:
            return "collaborative" 
        elif has_interactions:
            return "content"
        else:
            return "popular"
    
    def _blend_recommendations(self, user_id: str, user_interactions: List[Dict], 
                             num_recommendations: int) -> List[Tuple[str, float, str]]:
        collab_recs = self.collaborative.get_recommendations(user_id, num_recommendations * 2)
        content_recs = self.content_based.get_recommendations(user_interactions, num_recommendations * 2)
        
        collab_dict = {item: score for item, score in collab_recs}
        content_dict = {item: score for item, score in content_recs}
        
        all_items = set(collab_dict.keys()) | set(content_dict.keys())
        
        blended_recs = []
        for item in all_items:
            collab_score = collab_dict.get(item, 0)
            content_score = content_dict.get(item, 0)
            
            interaction_count = len(user_interactions)
            if interaction_count >= 10:
                weight_collab = 0.7
                weight_content = 0.3
            elif interaction_count >= 5:
                weight_collab = 0.5
                weight_content = 0.5
            else:
                weight_collab = 0.3
                weight_content = 0.7
            
            final_score = (weight_collab * collab_score) + (weight_content * content_score)
            strategy = "hybrid"
            
            blended_recs.append((item, final_score, strategy))
        
        blended_recs.sort(key=lambda x: x[1], reverse=True)
        return blended_recs[:num_recommendations]
    
    def _get_popular_fallback(self, num_recommendations: int) -> List[Tuple[str, float, str]]:
        popular_recs = self.content_based._get_popular_items(num_recommendations)
        return [(item, score, "popular") for item, score in popular_recs]
    
    def update_user_interaction(self, user_id: str, item_id: str, rating: float):
        if user_id in self.collaborative.users:
            user_idx = self.collaborative.users[user_id]
            if item_id in self.collaborative.items:
                item_idx = self.collaborative.items[item_id]
                self.collaborative.user_item_matrix[user_idx, item_idx] = rating
                self.collaborative._calculate_user_similarity()