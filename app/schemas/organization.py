from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class CreateOrganizationRequest(BaseModel):
    organization_name: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    
    class Config:
        json_schema_extra = {
            "example": {
                "organization_name": "acme_corp",
                "email": "admin@acme.com",
                "password": "SecurePass123"
            }
        }


class UpdateOrganizationRequest(BaseModel):
    organization_name: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    
    class Config:
        json_schema_extra = {
            "example": {
                "organization_name": "acme_corporation",
                "email": "admin@acme.com",
                "password": "SecurePass123"
            }
        }


class OrganizationResponse(BaseModel):
    organization_name: str
    collection_name: str
    admin_email: str
    created_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "organization_name": "acme_corp",
                "collection_name": "org_acme_corp",
                "admin_email": "admin@acme.com",
                "created_at": "2024-12-11T18:00:00"
            }
        }


class DeleteOrganizationRequest(BaseModel):
    organization_name: str = Field(..., min_length=3)
    
    class Config:
        json_schema_extra = {
            "example": {
                "organization_name": "acme_corp"
            }
        }
