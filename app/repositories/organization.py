from app.repositories.base import BaseRepository
from app.core.database import db
from typing import Optional, Dict, Any
from bson import ObjectId


class OrganizationRepository(BaseRepository):
    """Repository for organization operations"""
    
    def __init__(self):
        master_db = db.get_master_db()
        super().__init__(master_db["organizations"])
        self.admins_collection = master_db["admins"]
    
    async def get_by_name(self, org_name: str) -> Optional[Dict[str, Any]]:
        """Get organization by name"""
        return await self.find_one({"organization_name": org_name})
    
    async def get_by_id(self, org_id: str) -> Optional[Dict[str, Any]]:
        """Get organization by ID"""
        return await self.find_one({"_id": ObjectId(org_id)})
    
    async def create_organization(self, org_data: Dict[str, Any]) -> str:
        """Create new organization"""
        return await self.insert_one(org_data)
    
    async def update_organization(self, org_id: str, update_data: Dict[str, Any]) -> bool:
        """Update organization details"""
        return await self.update_one({"_id": ObjectId(org_id)}, update_data)
    
    async def delete_organization(self, org_name: str) -> bool:
        """Delete organization"""
        return await self.delete_one({"organization_name": org_name})
    
    async def create_admin(self, admin_data: Dict[str, Any]) -> str:
        """Create admin user"""
        result = await self.admins_collection.insert_one(admin_data)
        return str(result.inserted_id)
    
    async def get_admin_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get admin by email"""
        return await self.admins_collection.find_one({"email": email})
    
    async def get_admin_by_id(self, admin_id: str) -> Optional[Dict[str, Any]]:
        """Get admin by ID"""
        return await self.admins_collection.find_one({"_id": ObjectId(admin_id)})
    
    async def delete_admin(self, org_name: str) -> bool:
        """Delete admin user by organization"""
        result = await self.admins_collection.delete_one({"organization_name": org_name})
        return result.deleted_count > 0
