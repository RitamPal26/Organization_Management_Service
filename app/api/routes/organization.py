from fastapi import APIRouter, Depends, status, Query
from app.schemas.organization import (
    CreateOrganizationRequest,
    UpdateOrganizationRequest,
    OrganizationResponse,
    DeleteOrganizationRequest
)
from app.services.organization import OrganizationService
from app.api.deps import get_current_admin
from app.middleware.rate_limit import check_rate_limit
from typing import Dict

router = APIRouter()


@router.post(
    "/create",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Organization",
    description="Create new organization with admin user and dynamic collection",
    dependencies=[Depends(check_rate_limit)]
)
async def create_organization(request: CreateOrganizationRequest):
    """
    Create a new organization with the following:
    
    - **organization_name**: Unique organization name (3-50 characters)
    - **email**: Admin email address
    - **password**: Admin password (minimum 8 characters)
    
    This will:
    1. Validate organization name uniqueness
    2. Create a dynamic MongoDB collection for the organization
    3. Create an admin user with hashed password
    4. Store metadata in master database
    """
    org_service = OrganizationService()
    return await org_service.create_organization(request)


@router.get(
    "/get",
    response_model=OrganizationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Organization",
    description="Retrieve organization details by name",
    dependencies=[Depends(check_rate_limit)]
)
async def get_organization(
    organization_name: str = Query(..., description="Name of the organization to retrieve")
):
    """
    Get organization details from master database.
    
    - **organization_name**: Name of the organization
    
    Returns organization metadata including collection name and admin email.
    """
    org_service = OrganizationService()
    return await org_service.get_organization(organization_name)


@router.put(
    "/update",
    response_model=OrganizationResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Organization",
    description="Update organization name and sync data to new collection",
    dependencies=[Depends(check_rate_limit)]
)
async def update_organization(
    request: UpdateOrganizationRequest,
    current_admin: Dict = Depends(get_current_admin)
):
    """
    Update organization with new name (authenticated endpoint).
    
    - **organization_name**: New organization name
    - **email**: Admin email (for verification)
    - **password**: Admin password (will be updated)
    
    This will:
    1. Validate new organization name uniqueness
    2. Create new collection with new name
    3. Sync existing data from old collection to new
    4. Update metadata in master database
    5. Delete old collection
    
    **Requires JWT token in Authorization header.**
    """
    org_service = OrganizationService()
    return await org_service.update_organization(request, current_admin["email"])


@router.delete(
    "/delete",
    status_code=status.HTTP_200_OK,
    summary="Delete Organization",
    description="Delete organization and its collection (authenticated)",
    dependencies=[Depends(check_rate_limit)]
)
async def delete_organization(
    request: DeleteOrganizationRequest,
    current_admin: Dict = Depends(get_current_admin)
):
    """
    Delete organization and all its associated data (authenticated endpoint).
    
    - **organization_name**: Name of organization to delete
    
    This will:
    1. Verify admin owns this organization
    2. Delete the dynamic collection
    3. Delete admin user
    4. Delete organization metadata
    
    **Requires JWT token in Authorization header.**
    **Only the organization's admin can delete it.**
    """
    org_service = OrganizationService()
    return await org_service.delete_organization(request.organization_name, current_admin["email"])
