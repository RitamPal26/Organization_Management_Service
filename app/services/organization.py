from app.repositories.organization import OrganizationRepository
from app.core.database import db
from app.utils.security import SecurityUtils
from app.utils.exceptions import (
    OrganizationAlreadyExistsException,
    OrganizationNotFoundException,
    ForbiddenException
)
from app.schemas.organization import (
    CreateOrganizationRequest,
    UpdateOrganizationRequest,
    OrganizationResponse
)
from typing import Optional, Dict, Any
from datetime import datetime


class OrganizationService:
    """Service class for organization business logic"""
    
    def __init__(self):
        self.repo = OrganizationRepository()
    
    async def create_organization(self, request: CreateOrganizationRequest) -> OrganizationResponse:
        """Create new organization with dynamic collection"""
        
        # Check if organization already exists
        existing_org = await self.repo.get_by_name(request.organization_name)
        if existing_org:
            raise OrganizationAlreadyExistsException(request.organization_name)
        
        # Check if admin email already exists
        existing_admin = await self.repo.get_admin_by_email(request.email)
        if existing_admin:
            raise OrganizationAlreadyExistsException(f"Admin with email {request.email}")
        
        # Generate collection name
        collection_name = f"org_{request.organization_name}"
        
        # Create organization document
        org_data = {
            "organization_name": request.organization_name,
            "collection_name": collection_name,
            "admin_id": "",  # Will be updated after admin creation
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Insert organization
        org_id = await self.repo.create_organization(org_data)
        
        # Create admin user
        admin_data = {
            "email": request.email,
            "hashed_password": SecurityUtils.hash_password(request.password),
            "organization_id": org_id,
            "organization_name": request.organization_name,
            "created_at": datetime.utcnow()
        }
        admin_id = await self.repo.create_admin(admin_data)
        
        # Update organization with admin_id
        await self.repo.update_organization(org_id, {"admin_id": admin_id})
        
        # Create dynamic collection for the organization
        await self._create_dynamic_collection(collection_name)
        
        return OrganizationResponse(
            organization_name=request.organization_name,
            collection_name=collection_name,
            admin_email=request.email,
            created_at=org_data["created_at"]
        )
    
    async def get_organization(self, org_name: str) -> OrganizationResponse:
        """Get organization by name"""
        
        org = await self.repo.get_by_name(org_name)
        if not org:
            raise OrganizationNotFoundException(org_name)
        
        # Get admin details
        admin = await self.repo.get_admin_by_id(org["admin_id"])
        
        return OrganizationResponse(
            organization_name=org["organization_name"],
            collection_name=org["collection_name"],
            admin_email=admin["email"] if admin else "N/A",
            created_at=org["created_at"]
        )
    
    async def update_organization(self, request: UpdateOrganizationRequest, current_admin_email: str) -> OrganizationResponse:
        """Update organization with new name and sync data to new collection"""
        
        # Get admin to find their organization
        admin = await self.repo.get_admin_by_email(current_admin_email)
        if not admin:
            raise ForbiddenException("Admin not found")
        
        old_org_name = admin["organization_name"]
        new_org_name = request.organization_name
        
        # If organization name is not changing, just update admin credentials
        if old_org_name == new_org_name:
            # Update admin password if provided
            await self.repo.admins_collection.update_one(
                {"email": current_admin_email},
                {"$set": {"hashed_password": SecurityUtils.hash_password(request.password)}}
            )
            return await self.get_organization(old_org_name)
        
        # Check if new organization name already exists
        existing_org = await self.repo.get_by_name(new_org_name)
        if existing_org:
            raise OrganizationAlreadyExistsException(new_org_name)
        
        # Get old organization
        old_org = await self.repo.get_by_name(old_org_name)
        if not old_org:
            raise OrganizationNotFoundException(old_org_name)
        
        old_collection_name = old_org["collection_name"]
        new_collection_name = f"org_{new_org_name}"
        
        # Create new collection
        await self._create_dynamic_collection(new_collection_name)
        
        # Sync data from old collection to new collection
        await self._sync_collection_data(old_collection_name, new_collection_name)
        
        # Update organization document
        org_id = str(old_org["_id"])
        await self.repo.update_organization(org_id, {
            "organization_name": new_org_name,
            "collection_name": new_collection_name,
            "updated_at": datetime.utcnow()
        })
        
        # Update admin document
        await self.repo.admins_collection.update_one(
            {"email": current_admin_email},
            {
                "$set": {
                    "organization_name": new_org_name,
                    "hashed_password": SecurityUtils.hash_password(request.password)
                }
            }
        )
        
        # Delete old collection
        await self._delete_dynamic_collection(old_collection_name)
        
        return OrganizationResponse(
            organization_name=new_org_name,
            collection_name=new_collection_name,
            admin_email=request.email,
            created_at=old_org["created_at"]
        )
    
    async def delete_organization(self, org_name: str, current_admin_email: str) -> Dict[str, str]:
        """Delete organization and its collection"""
        
        # Get admin to verify ownership
        admin = await self.repo.get_admin_by_email(current_admin_email)
        if not admin:
            raise ForbiddenException("Admin not found")
        
        # Check if admin owns this organization
        if admin["organization_name"] != org_name:
            raise ForbiddenException("You can only delete your own organization")
        
        # Get organization
        org = await self.repo.get_by_name(org_name)
        if not org:
            raise OrganizationNotFoundException(org_name)
        
        collection_name = org["collection_name"]
        
        # Delete dynamic collection
        await self._delete_dynamic_collection(collection_name)
        
        # Delete admin
        await self.repo.delete_admin(org_name)
        
        # Delete organization
        await self.repo.delete_organization(org_name)
        
        return {"message": f"Organization '{org_name}' deleted successfully"}
    
    async def _create_dynamic_collection(self, collection_name: str):
        """Create a new collection for organization"""
        master_db = db.get_master_db()
        
        # Check if collection already exists
        existing_collections = await master_db.list_collection_names()
        if collection_name not in existing_collections:
            # Create collection with validation schema (optional)
            await master_db.create_collection(
                collection_name,
                validator={
                    "$jsonSchema": {
                        "bsonType": "object",
                        "description": "Organization-specific data collection"
                    }
                }
            )
            print(f"✅ Created collection: {collection_name}")
    
    async def _sync_collection_data(self, old_collection: str, new_collection: str):
        """Sync data from old collection to new collection"""
        master_db = db.get_master_db()
        old_col = master_db[old_collection]
        new_col = master_db[new_collection]
        
        # Get all documents from old collection
        documents = await old_col.find().to_list(length=None)
        
        if documents:
            # Insert into new collection
            await new_col.insert_many(documents)
            print(f"✅ Synced {len(documents)} documents from {old_collection} to {new_collection}")
    
    async def _delete_dynamic_collection(self, collection_name: str):
        """Delete organization collection"""
        master_db = db.get_master_db()
        await master_db.drop_collection(collection_name)
        print(f"✅ Deleted collection: {collection_name}")
