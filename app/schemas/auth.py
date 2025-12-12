from pydantic import BaseModel, EmailStr, ConfigDict


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "admin@acme.com",
                "password": "SecurePass123"
            }
        }
    )


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    admin_email: str
    organization_name: str
    organization_id: str
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "admin_email": "admin@acme.com",
                "organization_name": "acme_corp",
                "organization_id": "507f1f77bcf86cd799439011"
            }
        }
    )


class TokenPayload(BaseModel):
    admin_id: str
    email: str
    organization_id: str
    organization_name: str
    exp: int
