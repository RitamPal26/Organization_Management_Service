from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
from app.core.database import db
from app.api.routes import organization, admin

from fastapi.exceptions import RequestValidationError
from pymongo.errors import PyMongoError
from app.middleware.error_handler import (
    validation_exception_handler,
    pymongo_exception_handler,
    generic_exception_handler
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await db.connect()
    yield
    # Shutdown
    await db.disconnect()


app = FastAPI(
    title="Organization Management API",
    description="Multi-tenant organization management service with dynamic collection creation",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(PyMongoError, pymongo_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Security: Trust only specific hosts in production
# app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1"])

# CORS middleware with stricter settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: specify exact origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    max_age=600,
)

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

# Include routers
app.include_router(
    organization.router,
    prefix="/org",
    tags=["Organization Management"]
)

app.include_router(
    admin.router,
    prefix="/admin",
    tags=["Authentication"]
)


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Organization Management Service API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    try:
        # Check database connection
        await db.client.admin.command('ping')
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}
