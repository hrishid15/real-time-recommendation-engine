import sqlite3
import json
import time
import asyncio
from typing import Dict, List, Optional
import aiosqlite

class DatabaseManager:
    def __init__(self, db_path: str = "recommendation_engine.db"):
        self.db_path = db_path
        self.connection = None
    
    async def initialize(self):
        self.connection = await aiosqlite.connect(self.db_path)
        await self._create_tables()
        print(f"Database initialized at {self.db_path}")
    
    async def _create_tables(self):
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_interactions INTEGER DEFAULT 0
            )
        """)
        
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS items (
                item_id TEXT PRIMARY KEY,
                category TEXT NOT NULL,
                brand TEXT NOT NULL,
                description TEXT NOT NULL,
                average_rating REAL DEFAULT 0.0,
                total_ratings INTEGER DEFAULT 0
            )
        """)
        
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS user_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                item_id TEXT NOT NULL,
                rating REAL NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, item_id)
            )
        """)
        
        await self.connection.execute("CREATE INDEX IF NOT EXISTS idx_interactions_user ON user_interactions(user_id)")
        await self.connection.execute("CREATE INDEX IF NOT EXISTS idx_interactions_item ON user_interactions(item_id)")
        
        await self.connection.commit()
    
    async def create_or_update_user(self, user_id: str):
        await self.connection.execute("""
            INSERT INTO users (user_id, last_active)
            VALUES (?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET
                last_active = CURRENT_TIMESTAMP
        """, (user_id,))
        await self.connection.commit()
    
    async def get_user_stats(self, user_id: str) -> Optional[Dict]:
        cursor = await self.connection.execute("""
            SELECT u.*, COUNT(ui.id) as interaction_count
            FROM users u
            LEFT JOIN user_interactions ui ON u.user_id = ui.user_id
            WHERE u.user_id = ?
            GROUP BY u.user_id
        """, (user_id,))
        
        row = await cursor.fetchone()
        if row:
            return {
                "user_id": row[0],
                "created_at": row[1],
                "last_active": row[2],
                "total_interactions": row[3],
                "interaction_count": row[4] or 0
            }
        return None
    
    async def create_or_update_item(self, item_data: Dict):
        await self.connection.execute("""
            INSERT INTO items (item_id, category, brand, description)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(item_id) DO UPDATE SET
                category = excluded.category,
                brand = excluded.brand,
                description = excluded.description
        """, (
            item_data['item_id'],
            item_data['category'],
            item_data['brand'],
            item_data['description']
        ))
        await self.connection.commit()
    
    async def get_all_items(self) -> List[Dict]:
        cursor = await self.connection.execute("""
            SELECT i.*, AVG(ui.rating) as avg_rating, COUNT(ui.id) as rating_count
            FROM items i
            LEFT JOIN user_interactions ui ON i.item_id = ui.item_id
            GROUP BY i.item_id
            ORDER BY avg_rating DESC
        """)
        
        rows = await cursor.fetchall()
        return [{
            "item_id": row[0],
            "category": row[1],
            "brand": row[2],
            "description": row[3],
            "current_avg_rating": row[6] or 0.0,
            "current_rating_count": row[7] or 0
        } for row in rows]
    
    async def record_interaction(self, user_id: str, item_id: str, rating: float):
        await self.create_or_update_user(user_id)
        
        await self.connection.execute("""
            INSERT INTO user_interactions (user_id, item_id, rating)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, item_id) DO UPDATE SET
                rating = excluded.rating,
                timestamp = CURRENT_TIMESTAMP
        """, (user_id, item_id, rating))
        
        await self.connection.execute("""
            UPDATE users SET 
                total_interactions = (
                    SELECT COUNT(*) FROM user_interactions WHERE user_id = ?
                ),
                last_active = CURRENT_TIMESTAMP
            WHERE user_id = ?
        """, (user_id, user_id))
        
        await self.connection.commit()
    
    async def get_user_interactions(self, user_id: str, limit: int = 50) -> List[Dict]:
        cursor = await self.connection.execute("""
            SELECT ui.item_id, ui.rating, ui.timestamp
            FROM user_interactions ui
            WHERE ui.user_id = ?
            ORDER BY ui.timestamp DESC
            LIMIT ?
        """, (user_id, limit))
        
        rows = await cursor.fetchall()
        return [{
            "item_id": row[0],
            "rating": row[1],
            "timestamp": row[2]
        } for row in rows]
    
    async def get_all_interactions(self) -> List[Dict]:
        cursor = await self.connection.execute("""
            SELECT user_id, item_id, rating
            FROM user_interactions
            ORDER BY timestamp
        """)
        
        rows = await cursor.fetchall()
        return [{
            "user_id": row[0],
            "item_id": row[1],
            "rating": row[2]
        } for row in rows]
    
    async def close(self):
        if self.connection:
            await self.connection.close()