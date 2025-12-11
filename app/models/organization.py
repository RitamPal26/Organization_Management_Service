from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class OrganizationModel(BaseModel):
    """MongoDB document structure for organizations in master DB"""
    organization_name: str
    collection_name: str
    admin_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class AdminModel(BaseModel):
    """MongoDB document structure for admin users in master DB"""
    email: str
    hashed_password: str
    organization_id: str
    organization_name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
