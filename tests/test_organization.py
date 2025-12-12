import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import db


async def cleanup_test_data():
    """Clean up test organizations and admins from database"""
    try:
        master_db = db.get_master_db()
        test_orgs = [
            "test_company_pytest",
            "duplicate_test", 
            "login_test",
            "get_test"
        ]
        
        test_emails = [
            "test@pytest.com",
            "dup@test.com",
            "dup2@test.com",
            "login@test.com",
            "get@test.com"
        ]
        
        for org_name in test_orgs:
            # Delete organization document
            await master_db.organizations.delete_many({"organization_name": org_name})
            
            # Delete organization's collection if exists
            collection_name = f"org_{org_name}"
            collections = await master_db.list_collection_names()
            if collection_name in collections:
                await master_db.drop_collection(collection_name)
        
        # Delete all test admin users
        for email in test_emails:
            await master_db.admins.delete_many({"email": email})
        
        print("✅ Test data cleaned up successfully")
        
    except Exception as e:
        print(f"❌ Cleanup error: {e}")


@pytest_asyncio.fixture(scope="module", autouse=True)
async def setup_database():
    """Setup database connection before tests and cleanup after"""
    await db.connect()
    
    # Clean up any leftover test data from previous runs
    await cleanup_test_data()
    
    yield
    
    # Clean up after all tests complete
    await cleanup_test_data()
    await db.disconnect()


@pytest.fixture(scope="module")
def client():
    """Create test client"""
    with TestClient(app) as test_client:
        yield test_client


def test_create_organization(client):
    """Test organization creation"""
    response = client.post(
        "/org/create",
        json={
            "organization_name": "test_company_pytest",
            "email": "test@pytest.com",
            "password": "TestPassword123"
        }
    )
    
    assert response.status_code == 201, f"Expected 201, got {response.status_code}. Response: {response.json()}"
    data = response.json()
    assert data["organization_name"] == "test_company_pytest"
    assert data["admin_email"] == "test@pytest.com"


def test_create_duplicate_organization(client):
    """Test duplicate organization creation fails"""
    # Create first
    response1 = client.post(
        "/org/create",
        json={
            "organization_name": "duplicate_test",
            "email": "dup@test.com",
            "password": "TestPass123"
        }
    )
    assert response1.status_code == 201
    
    # Try to create duplicate
    response2 = client.post(
        "/org/create",
        json={
            "organization_name": "duplicate_test",
            "email": "dup2@test.com",
            "password": "TestPass123"
        }
    )
    assert response2.status_code == 400
    assert "already exists" in response2.json()["detail"]


def test_admin_login(client):
    """Test admin login"""
    # Create organization first
    response1 = client.post(
        "/org/create",
        json={
            "organization_name": "login_test",
            "email": "login@test.com",
            "password": "LoginPass123"
        }
    )
    assert response1.status_code == 201
    
    # Login
    response2 = client.post(
        "/admin/login",
        json={
            "email": "login@test.com",
            "password": "LoginPass123"
        }
    )
    assert response2.status_code == 200
    data = response2.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_get_organization(client):
    """Test get organization"""
    # Create organization first
    response1 = client.post(
        "/org/create",
        json={
            "organization_name": "get_test",
            "email": "get@test.com",
            "password": "GetPass123"
        }
    )
    assert response1.status_code == 201
    
    # Get organization
    response2 = client.get("/org/get?organization_name=get_test")
    assert response2.status_code == 200
    data = response2.json()
    assert data["organization_name"] == "get_test"


def test_invalid_password_login(client):
    """Test login with wrong password"""
    response = client.post(
        "/admin/login",
        json={
            "email": "login@test.com",
            "password": "WrongPassword"
        }
    )
    assert response.status_code == 401
