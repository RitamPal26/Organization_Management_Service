from motor.motor_asyncio import AsyncIOMotorCollection
from typing import Optional, List, Dict, Any
from abc import ABC, abstractmethod


class BaseRepository(ABC):
    """Base repository with common database operations"""
    
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection
    
    async def find_one(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find single document"""
        return await self.collection.find_one(query)
    
    async def find_many(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find multiple documents"""
        cursor = self.collection.find(query)
        return await cursor.to_list(length=None)
    
    async def insert_one(self, document: Dict[str, Any]) -> str:
        """Insert single document and return inserted ID"""
        result = await self.collection.insert_one(document)
        return str(result.inserted_id)
    
    async def update_one(self, query: Dict[str, Any], update: Dict[str, Any]) -> bool:
        """Update single document"""
        result = await self.collection.update_one(query, {"$set": update})
        return result.modified_count > 0
    
    async def delete_one(self, query: Dict[str, Any]) -> bool:
        """Delete single document"""
        result = await self.collection.delete_one(query)
        return result.deleted_count > 0
    
    async def count_documents(self, query: Dict[str, Any]) -> int:
        """Count documents matching query"""
        return await self.collection.count_documents(query)
