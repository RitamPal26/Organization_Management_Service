from app.repositories.organization import OrganizationRepository
from app.utils.security import SecurityUtils
from app.utils.exceptions import UnauthorizedException
from app.schemas.auth import LoginRequest, LoginResponse
from datetime import timedelta
from app.core.config import settings


class AuthService:
    """Service class for authentication logic"""
    
    def __init__(self):
        self.repo = OrganizationRepository()
    
    async def login(self, request: LoginRequest) -> LoginResponse:
        """Authenticate admin and return JWT token"""
        
        # Get admin by email
        admin = await self.repo.get_admin_by_email(request.email)
        if not admin:
            raise UnauthorizedException("Invalid email or password")
        
        # Verify password
        if not SecurityUtils.verify_password(request.password, admin["hashed_password"]):
            raise UnauthorizedException("Invalid email or password")
        
        # Get organization details
        org = await self.repo.get_by_id(admin["organization_id"])
        if not org:
            raise UnauthorizedException("Organization not found")
        
        # Create JWT token
        token_data = {
            "admin_id": str(admin["_id"]),
            "email": admin["email"],
            "organization_id": admin["organization_id"],
            "organization_name": admin["organization_name"]
        }
        
        access_token = SecurityUtils.create_access_token(
            data=token_data,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            admin_email=admin["email"],
            organization_name=admin["organization_name"],
            organization_id=admin["organization_id"]
        )
    
    async def verify_token(self, token: str) -> dict:
        """Verify JWT token and return payload"""
        payload = SecurityUtils.decode_access_token(token)
        if not payload:
            raise UnauthorizedException("Invalid or expired token")
        
        return payload
