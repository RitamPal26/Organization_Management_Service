from pydantic_settings import BaseSettings
from pydantic import field_validator, ConfigDict
import secrets


class Settings(BaseSettings):
    MONGODB_URI: str
    DATABASE_NAME: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ENVIRONMENT: str = "development"
    
    @field_validator('SECRET_KEY')
    @classmethod
    def validate_secret_key(cls, v):
        if len(v) < 32:
            raise ValueError('SECRET_KEY must be at least 32 characters long')
        if v == "your-secret-key-change-this":
            raise ValueError('Please change the default SECRET_KEY')
        return v
    
    @field_validator('MONGODB_URI')
    @classmethod
    def validate_mongodb_uri(cls, v):
        if not v.startswith(('mongodb://', 'mongodb+srv://')):
            raise ValueError('Invalid MongoDB URI format')
        return v
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True
    )


settings = Settings()


def generate_secret_key():
    return secrets.token_urlsafe(32)
