from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings

class Database:
    client: AsyncIOMotorClient = None
    
    @classmethod
    async def connect(cls):
        cls.client = AsyncIOMotorClient(settings.MONGODB_URI)
        try:
            await cls.client.admin.command('ping')
            print("✅ MongoDB connected successfully")
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
    
    @classmethod
    async def disconnect(cls):
        if cls.client:
            cls.client.close()
    
    @classmethod
    def get_db(cls):
        return cls.client[settings.DATABASE_NAME]

db = Database()
