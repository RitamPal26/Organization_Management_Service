from fastapi import APIRouter, status
from app.schemas.auth import LoginRequest, LoginResponse
from app.services.auth import AuthService

router = APIRouter()


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Admin Login",
    description="Authenticate admin user and receive JWT token"
)
async def admin_login(request: LoginRequest):
    """
    Admin login endpoint that validates credentials and returns JWT token.
    
    - **email**: Admin email address
    - **password**: Admin password
    
    Returns JWT token containing admin and organization information.
    """
    auth_service = AuthService()
    return await auth_service.login(request)
