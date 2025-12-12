from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.database import db
from app.api.routes import organization, admin


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

# CORS middleware (optional, for frontend integration)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        "docs": "/docs",
        "endpoints": {
            "create_org": "POST /org/create",
            "get_org": "GET /org/get?organization_name=<name>",
            "update_org": "PUT /org/update (requires auth)",
            "delete_org": "DELETE /org/delete (requires auth)",
            "login": "POST /admin/login"
        }
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "database": "connected"}
