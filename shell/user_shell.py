import asyncio
import json
import aiohttp
from typing import Dict, List, Optional

class RecommendationShell:
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        self.current_user = None
        self.session = None
        self.items_catalog = {
            "iphone": {"name": "iPhone 15", "category": "electronics", "price": "$999"},
            "macbook": {"name": "MacBook Pro", "category": "electronics", "price": "$1999"},
            "gaming_chair": {"name": "Gaming Chair", "category": "furniture", "price": "$299"},
            "coffee_maker": {"name": "Coffee Maker", "category": "kitchen", "price": "$89"},
            "kitchen_knife": {"name": "Kitchen Knife Set", "category": "kitchen", "price": "$79"},
            "cookbook": {"name": "Cooking Cookbook", "category": "books", "price": "$25"},
            "airpods": {"name": "AirPods Pro", "category": "electronics", "price": "$249"},
            "ipad": {"name": "iPad Air", "category": "electronics", "price": "$599"},
        }
    
    async def start(self):
        self.session = aiohttp.ClientSession()
        
        print("=" * 60)
        print("REAL-TIME RECOMMENDATION ENGINE")
        print("=" * 60)
        print("Welcome! This system learns from your interactions in real-time.")
        print("Try rating items and see how recommendations change instantly!")
        print()
        
        await self._check_server_connection()
        
        while True:
            try:
                if not self.current_user:
                    await self._login_menu()
                else:
                    await self._main_menu()
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except EOFError:
                break
        
        await self.session.close()
    
    async def _check_server_connection(self):
        try:
            async with self.session.get(f"{self.api_url}/health") as resp:
                if resp.status == 200:
                    health = await resp.json()
                    print(f"Connected to recommendation server")
                    print(f"   Server uptime: {health['uptime_seconds']}s")
                    print(f"   Requests served: {health['requests_served']}")
                else:
                    print("Server health check failed")
        except Exception as e:
            print(f"Cannot connect to server at {self.api_url}")
            print(f"   Make sure to run: python test_api_server.py")
            print(f"   Error: {e}")
            exit(1)
    
    async def _login_menu(self):
        print("\n" + "=" * 40)
        print("USER LOGIN")
        print("=" * 40)
        print("1. Login as existing user")
        print("2. Create new user") 
        print("3. Quick demo users")
        print("4. Exit")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == "1":
            await self._existing_user_login()
        elif choice == "2":
            await self._new_user_login()
        elif choice == "3":
            await self._demo_users()
        elif choice == "4":
            exit(0)
        else:
            print("Invalid choice. Please try again.")
    
    async def _existing_user_login(self):
        user_id = input("Enter your username: ").strip()
        if user_id:
            self.current_user = user_id
            print(f"Welcome back, {user_id}!")
            await self._show_user_history()
    
    async def _new_user_login(self):
        user_id = input("Choose a username: ").strip()
        if user_id:
            self.current_user = user_id
            print(f"Welcome, {user_id}! You're a new user.")
            print("Rate a few items to get personalized recommendations!")
    
    async def _demo_users(self):
        print("\nDemo users with existing data:")
        print("1. alice (likes Apple products)")
        print("2. bob (likes tech + gaming)")
        print("3. carol (likes cooking)")
        
        choice = input("Choose demo user (1-3): ").strip()
        users = {"1": "alice", "2": "bob", "3": "carol"}
        
        if choice in users:
            self.current_user = users[choice]
            print(f"Logged in as {self.current_user}")
            await self._show_user_history()
    
    async def _show_user_history(self):
        print(f"\nGetting {self.current_user}'s recommendation profile...")
        await self._get_recommendations_preview()
    
    async def _main_menu(self):
        print(f"\n" + "=" * 50)
        print(f"RECOMMENDATION ENGINE - User: {self.current_user}")
        print("=" * 50)
        print("1. Get my recommendations")
        print("2. Rate an item")
        print("3. Browse items by category") 
        print("4. Find similar items")
        print("5. View popular items")
        print("6. System performance stats")
        print("7. Switch user")
        print("8. Exit")
        
        choice = input(f"\n{self.current_user}> ").strip()
        
        if choice == "1":
            await self._get_recommendations()
        elif choice == "2":
            await self._rate_item()
        elif choice == "3":
            await self._browse_categories()
        elif choice == "4":
            await self._find_similar()
        elif choice == "5":
            await self._view_popular()
        elif choice == "6":
            await self._view_stats()
        elif choice == "7":
            self.current_user = None
        elif choice == "8":
            exit(0)
        else:
            print("Invalid choice. Please try again.")
    
    async def _get_recommendations(self):
        count = input("How many recommendations? (default 5): ").strip()
        count = int(count) if count.isdigit() else 5
        
        print(f"\nGetting {count} personalized recommendations for {self.current_user}...")
        
        try:
            async with self.session.get(f"{self.api_url}/recommendations/{self.current_user}?count={count}") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    await self._display_recommendations(data)
                else:
                    print(f"Error: {resp.status}")
        except Exception as e:
            print(f"Error getting recommendations: {e}")
    
    async def _get_recommendations_preview(self):
        try:
            async with self.session.get(f"{self.api_url}/recommendations/{self.current_user}?count=3") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    recs = data['recommendations']
                    print(f"Top recommendations: {', '.join([r['item'] for r in recs])}")
                    print(f"Source: {data['source']} | Response time: {data['api_response_time_ms']}ms")
        except:
            print("Getting fresh recommendations...")
    
    async def _display_recommendations(self, data):
        print(f"\nRECOMMENDATIONS FOR {self.current_user.upper()}")
        print("-" * 50)
        
        for i, rec in enumerate(data['recommendations'], 1):
            item_info = self.items_catalog.get(rec['item'], {"name": rec['item'], "category": "unknown", "price": "N/A"})
            print(f"{i}. {item_info['name']}")
            print(f"   Score: {rec['score']:.3f} | Strategy: {rec['strategy']}")
            print(f"   Category: {item_info['category']} | Price: {item_info['price']}")
            print()
        
        print(f"Source: {data['source']} | Response time: {data['api_response_time_ms']}ms")
        
        action = input("\nWould you like to rate any of these items? (y/n): ").lower()
        if action == 'y':
            await self._rate_from_recommendations(data['recommendations'])
    
    async def _rate_from_recommendations(self, recommendations):
        print("\nRate items (1-5 stars):")
        for i, rec in enumerate(recommendations, 1):
            item_info = self.items_catalog.get(rec['item'], {"name": rec['item']})
            print(f"{i}. {item_info['name']}")
        
        choice = input("Enter item number to rate (or press Enter to skip): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(recommendations):
            item_id = recommendations[int(choice)-1]['item']
            await self._rate_specific_item(item_id)
    
    async def _rate_item(self):
        print("\nRATE AN ITEM")
        print("Available items:")
        
        for i, (item_id, info) in enumerate(self.items_catalog.items(), 1):
            print(f"{i}. {info['name']} ({info['category']}) - {info['price']}")
        
        choice = input("\nEnter item number: ").strip()
        if choice.isdigit():
            items = list(self.items_catalog.keys())
            if 1 <= int(choice) <= len(items):
                item_id = items[int(choice)-1]
                await self._rate_specific_item(item_id)
    
    async def _rate_specific_item(self, item_id):
        item_info = self.items_catalog.get(item_id, {"name": item_id})
        rating = input(f"Rate {item_info['name']} (1-5 stars): ").strip()
        
        if rating.isdigit() and 1 <= int(rating) <= 5:
            print(f"Recording rating: {item_info['name']} = {rating} stars...")
            
            try:
                payload = {
                    "user_id": self.current_user,
                    "item_id": item_id,
                    "rating": int(rating)
                }
                
                async with self.session.post(f"{self.api_url}/interactions", json=payload) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        print(f"Rating recorded! Response time: {data['api_response_time_ms']}ms")
                        print("Your recommendations have been updated in real-time!")
                    else:
                        print(f"Error recording rating: {resp.status}")
            except Exception as e:
                print(f"Error: {e}")
        else:
            print("Invalid rating. Please enter 1-5.")
    
    async def _browse_categories(self):
        categories = ["electronics", "kitchen", "furniture", "books"]
        print("\n📱 BROWSE BY CATEGORY")
        for i, cat in enumerate(categories, 1):
            print(f"{i}. {cat.title()}")
        
        choice = input("Choose category (1-4): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(categories):
            category = categories[int(choice)-1]
            await self._show_popular_in_category(category)
    
    async def _show_popular_in_category(self, category):
        try:
            async with self.session.get(f"{self.api_url}/popular?category={category}&count=5") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"\n🔥 POPULAR {category.upper()} ITEMS")
                    print("-" * 40)
                    
                    for i, item in enumerate(data['popular_items'], 1):
                        item_info = self.items_catalog.get(item['item'], {"name": item['item'], "price": "N/A"})
                        print(f"{i}. {item_info['name']} - {item_info['price']}")
                        print(f"   Popularity score: {item['score']:.2f}")
                    
                    print(f"\nSource: {data['source']} | Response time: {data['api_response_time_ms']}ms")
        except Exception as e:
            print(f"Error: {e}")
    
    async def _find_similar(self):
        item_name = input("Enter item name to find similar items: ").strip().lower()
        
        item_id = None
        for iid, info in self.items_catalog.items():
            if item_name in info['name'].lower() or item_name == iid:
                item_id = iid
                break
        
        if item_id:
            try:
                async with self.session.get(f"{self.api_url}/similar/{item_id}?count=3") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        item_info = self.items_catalog[item_id]
                        
                        print(f"\nITEMS SIMILAR TO {item_info['name'].upper()}")
                        print("-" * 40)
                        
                        for i, item in enumerate(data['similar_items'], 1):
                            similar_info = self.items_catalog.get(item['item'], {"name": item['item'], "price": "N/A"})
                            print(f"{i}. {similar_info['name']} - {similar_info['price']}")
                            print(f"   Similarity: {item['score']:.3f}")
                        
                        print(f"\nSource: {data['source']} | Response time: {data['api_response_time_ms']}ms")
            except Exception as e:
                print(f"Error: {e}")
        else:
            print("Item not found. Try: iphone, macbook, gaming chair, etc.")
    
    async def _view_popular(self):
        await self._show_popular_in_category("all")
    
    async def _view_stats(self):
        try:
            async with self.session.get(f"{self.api_url}/stats") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"\nSYSTEM PERFORMANCE STATS")
                    print("-" * 40)
                    print(f"Service uptime: {data['service_uptime_seconds']}s")
                    print(f"Total API requests: {data['total_api_requests']}")
                    print(f"Cache hit rate: {data['performance']['cache_hit_rate']}")
                    print(f"Recommendation requests: {data['performance']['recommendation_requests']}")
                    print(f"Memory cache size: {data['performance']['cache_performance']['cache_size']} items")
        except Exception as e:
            print(f"Error: {e}")

async def main():
    shell = RecommendationShell()
    await shell.start()

if __name__ == "__main__":
    asyncio.run(main())