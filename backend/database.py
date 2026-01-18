from motor.motor_asyncio import AsyncIOMotorClient
from config import settings

class Database:
    client: AsyncIOMotorClient = None

db = Database()

async def connect_to_mongo():
    try:
        db.client = AsyncIOMotorClient(settings.mongodb_uri)
        await db.client.admin.command('ping')
        print("Connected to MongoDB")
    except Exception as e:
        print(f"⚠️  MongoDB connection failed: {e}")
        print("⚠️  Running in mock mode - recommendations will use sample data")
        db.client = None

async def close_mongo_connection():
    if db.client:
        db.client.close()
        print("Disconnected from MongoDB")

def get_database():
    # Return None if not connected - services will handle mock mode
    if db.client is None:
        print("⚠️  Database not available - using mock data")
        return None
    return db.client[settings.mongodb_db_name]
