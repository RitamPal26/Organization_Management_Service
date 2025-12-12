# Organization Management Service

A multi-tenant organization management backend service built with FastAPI and MongoDB. Supports dynamic collection creation per organization with secure JWT-based authentication.

## Architecture

This project follows a **layered architecture** with clear separation of concerns:

- **API Layer**: FastAPI route handlers
- **Service Layer**: Business logic and dynamic collection management
- **Repository Layer**: Database operations
- **Models/Schemas**: Pydantic models for validation

For detailed system architecture, flow diagrams, and design decisions, see the [Architecture Documentation](docs/architecture.md).

## Features

- Create organizations with dynamic MongoDB collections
- Secure admin authentication with JWT tokens
- Password hashing using bcrypt
- Organization CRUD operations
- Data migration during organization updates
- Role-based access control (admin-only delete)

## Prerequisites

- Python 3.9+
- MongoDB Atlas account
- pip

## Installation & Setup

### 1. Clone the repository
```
git clone https://github.com/RitamPal26/Organization_Management_Service.git
cd Organization_Management_Service
```

### 2. Create virtual environment
```
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install dependencies
```
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the root directory:

```
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
DATABASE_NAME=master_db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 5. Run the application
```
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Interactive API documentation is available at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## API Endpoints

### Authentication

#### Login
```
POST /admin/login
Content-Type: application/json

{
  "email": "admin@example.com",
  "password": "SecurePass123"
}
```

**Response**: JWT token with admin and organization details

---

### Organization Management

#### Create Organization
```
POST /org/create
Content-Type: application/json

{
  "organization_name": "acme_corp",
  "email": "admin@acme.com",
  "password": "SecurePass123"
}
```

**Creates**:
- Organization entry in master database
- Admin user with hashed password
- Dynamic collection `org_acme_corp`

---

#### Get Organization
```
GET /org/get?organization_name=acme_corp
```

**Returns**: Organization metadata and admin email

---

#### Update Organization
```
PUT /org/update
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "organization_name": "acme_corporation",
  "email": "admin@acme.com",
  "password": "NewPassword123"
}
```

**Performs**:
- Creates new collection with updated name
- Migrates existing data
- Deletes old collection

---

#### Delete Organization
```
DELETE /org/delete
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "organization_name": "acme_corporation"
}
```

**Deletes**:
- Organization collection
- Admin user
- Organization metadata

**Note**: Only the organization's admin can delete it.

---

## Project Structure

```
organization-management/
├── app/
│   ├── api/
│   │   ├── deps.py              # JWT authentication dependency
│   │   └── routes/
│   │       ├── admin.py         # Auth endpoints
│   │       └── organization.py  # Org endpoints
│   ├── core/
│   │   ├── config.py            # Settings & configuration
│   │   └── database.py          # MongoDB connection
│   ├── models/
│   │   └── organization.py      # MongoDB document models
│   ├── repositories/
│   │   ├── base.py              # Base repository class
│   │   └── organization.py      # Org data access layer
│   ├── schemas/
│   │   ├── auth.py              # Auth request/response schemas
│   │   └── organization.py      # Org request/response schemas
│   ├── services/
│   │   ├── auth.py              # Authentication logic
│   │   └── organization.py      # Business logic
│   ├── utils/
│   │   ├── exceptions.py        # Custom exceptions
│   │   └── security.py          # JWT & password hashing
│   └── main.py                  # FastAPI app initialization
├── .env                         # Environment variables
├── .gitignore
├── requirements.txt
└── README.md
```

## Security Features

- **Password Hashing**: bcrypt with salt
- **JWT Authentication**: HS256 algorithm
- **Token Expiration**: Configurable token lifetime
- **Input Validation**: Pydantic schema validation
- **Authorization**: Protected endpoints require valid JWT

## Database Schema

### Master Database Collections

**organizations**
```
{
  "_id": ObjectId,
  "organization_name": "acme_corp",
  "collection_name": "org_acme_corp",
  "admin_id": "admin_object_id",
  "created_at": ISODate,
  "updated_at": ISODate
}
```

**admins**
```
{
  "_id": ObjectId,
  "email": "admin@acme.com",
  "hashed_password": "bcrypt_hash",
  "organization_id": "org_object_id",
  "organization_name": "acme_corp",
  "created_at": ISODate
}
```

## Architectural Analysis

### Current Design: Collection-per-Tenant

**Pros**:
- Simple data isolation
- Easy to understand and implement
- Good for demos and small-scale applications

**Cons & Trade-offs**:
- **Scalability bottleneck**: MongoDB recommends max 5,000-10,000 collections per cluster
- **Resource overhead**: Each collection has file descriptors, index metadata, and memory overhead
- **Operational complexity**: Backups, migrations, and monitoring become fragmented
- **Performance degradation**: Collection creation at runtime causes latency spikes

### Recommended Production Architecture

**For better scalability, consider:**

1. **Database-per-Tenant**
   - Separate databases instead of collections
   - Better resource isolation
   - Easier backup strategies
   - Still limited but higher ceiling (~10k databases)

2. **Shared Collection with Tenant ID** (Most Scalable)
   - Single collection with `tenant_id` field
   - Compound indexes on `(tenant_id, _id)`
   - Scales to millions of tenants
   - Requires robust query filtering

3. **Hybrid Approach**
   - Small tenants share collections
   - Large enterprise tenants get dedicated databases
   - Best balance of cost and performance

**Tech Stack Improvements**:
- Add Redis for session management and caching
- Implement connection pooling optimization
- Use MongoDB transactions for data consistency
- Add rate limiting and request validation middleware

## Future Enhancements

- [ ] Add unit and integration tests
- [ ] Implement refresh token mechanism
- [ ] Implement audit logging
- [ ] Add Celery for async background tasks
- [ ] Containerize with Docker
- [ ] Add CI/CD pipeline
- [ ] Implement API rate limiting

## Additional questions

Do you think this is a good architecture with a scalable design? What can be the trade-offs with the tech stack and design choices?