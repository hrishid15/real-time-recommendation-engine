import asyncio
import sys
import signal
from api.recommendation_server import RecommendationAPI
from shell.user_shell import RecommendationShell

class RecommendationSystem:
    def __init__(self):
        self.api = None
        self.running = False
    
    async def start_system(self):
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
        
        print("Starting Real-time Recommendation Engine...")
        print("=" * 50)
        
        self.api = RecommendationAPI(port=8000)
        await self.api.initialize(interactions, items_data)
        await self.api.start()
        
        self.running = True
        
        print("Server started successfully!")
        print("Initializing user interface...")
        print("=" * 50)
        
        await asyncio.sleep(1)
        
        shell = RecommendationShell()
        await shell.start()
    
    async def stop_system(self):
        print("\nShutting down recommendation system...")
        if self.api:
            await self.api.close()
        self.running = False
        print("System stopped")

async def run_system():
    system = RecommendationSystem()
    
    try:
        await system.start_system()
    except KeyboardInterrupt:
        print("\nReceived interrupt signal...")
    finally:
        await system.stop_system()

def show_menu():
    print("Real-time Recommendation Engine")
    print("=" * 40)
    print("Choose an option:")
    print("1. Start system (server + shell)")
    print("2. Help")
    print("3. Exit")
    print("=" * 40)

async def show_help():
    print("\nHelp - Real-time Recommendation Engine")
    print("=" * 50)
    print("WHAT THIS SYSTEM DOES:")
    print("  - Provides personalized recommendations using ML")
    print("  - Learns from user interactions in real-time")
    print("  - Serves recommendations in <100ms")
    print("  - Uses hybrid collaborative + content-based filtering")
    print()
    print("OPTION 1: Start System")
    print("  - Starts the recommendation API server")
    print("  - Opens interactive user shell")
    print("  - Try logging in as alice, bob, or carol")
    print("  - Rate items and see recommendations change instantly")
    print()
    print("FEATURES:")
    print("  - Multi-user support with personalized recommendations")
    print("  - Real-time learning from user ratings")
    print("  - Item similarity and popularity features")
    print("  - Performance monitoring and caching")
    print("  - REST API for external integration")
    print()
    print("DEMO USERS:")
    print("  - alice: Likes Apple products and technology")
    print("  - bob: Likes technology and gaming equipment")  
    print("  - carol: Likes cooking and kitchen items")

async def main():
    while True:
        try:
            show_menu()
            choice = input("Enter choice (1-3): ").strip()
            
            if choice == "1":
                await run_system()
                break
            elif choice == "2":
                await show_help()
                input("\nPress Enter to continue...")
                print("\n" + "=" * 50 + "\n")
            elif choice == "3":
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.\n")
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except EOFError:
            break

if __name__ == "__main__":
    if sys.platform != "win32":
        def signal_handler(sig, frame):
            print("\nReceived interrupt signal, shutting down...")
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)