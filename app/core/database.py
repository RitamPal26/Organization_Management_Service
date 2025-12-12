from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings
from typing import Optional


class Database:
    client: Optional[AsyncIOMotorClient] = None
    
    @classmethod
    async def connect(cls):
        """Establish MongoDB connection"""
        cls.client = AsyncIOMotorClient(settings.MONGODB_URI)
        try:
            await cls.client.admin.command('ping')
            print("✅ MongoDB connected successfully")
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
            raise
    
    @classmethod
    async def disconnect(cls):
        """Close MongoDB connection"""
        if cls.client:
            cls.client.close()
            print("MongoDB connection closed")
    
    @classmethod
    def get_master_db(cls) -> AsyncIOMotorDatabase:
        """Get master database instance"""
        if not cls.client:
            raise Exception("Database not connected. Call connect() first.")
        return cls.client[settings.DATABASE_NAME]
    
    @classmethod
    def get_org_collection(cls, org_collection_name: str):
        """Get organization-specific collection"""
        if not cls.client:
            raise Exception("Database not connected. Call connect() first.")
        return cls.client[settings.DATABASE_NAME][org_collection_name]


# Create instance
db = Database()
