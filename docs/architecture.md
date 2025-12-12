# Organization Management Service - Architecture


## Overview


Multi-tenant backend system built with FastAPI and MongoDB Atlas. Uses collection-per-tenant pattern for data isolation with JWT-based authentication.


## System Architecture


![System Architecture](diagram.mermaid)


## Architecture Components


### 1. API Layer (`app/api/routes/`)
- `POST /org/create` - Create organization with admin user
- `GET /org/get` - Retrieve organization details
- `PUT /org/update` - Update organization with data migration (auth required)
- `DELETE /org/delete` - Delete organization and data (auth required)
- `POST /admin/login` - Authenticate and receive JWT token


### 2. Middleware Layer
- **JWT Authentication** (`app/api/deps.py`) - Token validation for protected endpoints
- **Rate Limiter** (`app/middleware/rate_limit.py`) - 100 requests/minute per IP
- **Security Headers** (`app/main.py`) - X-Frame-Options, HSTS, CSP


### 3. Service Layer (`app/services/`)
- **OrganizationService** - Business logic, dynamic collection management, data migration
- **AuthService** - Credential validation, JWT token generation


### 4. Repository Layer (`app/repositories/`)
- **OrganizationRepository** - Database operations for organizations and admins
- Abstracts MongoDB interactions from business logic


### 5. Utilities (`app/utils/`)
- **SecurityUtils** - bcrypt password hashing, JWT creation/validation (HS256)
- **Custom Exceptions** - HTTP error responses (404, 400, 401, 403)


## Database Design


### Master Database Collections


**organizations**
```
{
  "organization_name": "acme_corp",
  "collection_name": "org_acme_corp",
  "admin_id": "ObjectId",
  "created_at": "ISODate"
}
```


**admins**
```
{
  "email": "admin@acme.com",
  "hashed_password": "bcrypt_hash",
  "organization_id": "ObjectId",
  "organization_name": "acme_corp"
}
```


### Dynamic Collections
- Pattern: `org_<organization_name>`
- Created programmatically per tenant
- Optional JSON schema validation


## Key Flows


### Create Organization
1. Validate uniqueness
2. Hash password with bcrypt
3. Store org metadata in `organizations` collection
4. Store admin in `admins` collection
5. Create dynamic collection `org_<name>`


### Login & Authentication
1. Fetch admin by email
2. Verify password with bcrypt
3. Generate JWT with admin_id, org_id, email
4. Return token (expires in 30 minutes)


### Update Organization
1. Validate JWT token
2. Create new collection with updated name
3. Migrate all documents from old to new collection
4. Update metadata in master database
5. Drop old collection


### Delete Organization
1. Validate JWT token and ownership
2. Drop dynamic collection
3. Delete admin from `admins`
4. Delete organization from `organizations`


## Security Implementation


**Password Security:** bcrypt with salt, no plain text storage


**JWT Authentication:** HS256 algorithm, 30-minute expiration, contains admin_id + org_id


**Rate Limiting:** 100 requests/minute per IP, prevents abuse


**Security Headers:** X-Frame-Options (DENY), X-Content-Type-Options (nosniff), HSTS


## Design Choices & Rationale


### 1. Collection-per-Tenant Pattern
**Choice:** Each organization gets a dedicated MongoDB collection


**Rationale:**
- Simple to implement and understand for assignment demonstration
- Clear data isolation without complex filtering logic
- Easy to visualize multi-tenancy concept
- Straightforward per-tenant backup/restore


**Trade-offs:**
- Limited to ~5,000 organizations before hitting MongoDB collection limits
- Resource overhead (metadata, indexes) per collection
- Not suitable for production at scale


### 2. FastAPI Framework
**Choice:** FastAPI over Django


**Rationale:**
- Native async/await support for non-blocking MongoDB operations
- Automatic OpenAPI documentation (Swagger UI)
- Pydantic validation reduces boilerplate code
- Better performance for I/O-bound operations


### 3. Motor (Async MongoDB Driver)
**Choice:** Motor instead of PyMongo


**Rationale:**
- Compatible with FastAPI's async architecture
- Non-blocking database calls improve concurrency
- Better resource utilization under load


### 4. JWT over Session-based Auth
**Choice:** Stateless JWT tokens


**Rationale:**
- No server-side session storage required
- Scales horizontally without shared state
- Token contains user context (admin_id, org_id)
- Suitable for API-first architecture


### 5. Layered Architecture
**Choice:** API → Service → Repository → Database


**Rationale:**
- Clear separation of concerns
- Business logic isolated from data access
- Easy to test individual layers
- Facilitates future architecture changes


### 6. Class-based Services & Repositories
**Choice:** Object-oriented design with classes


**Rationale:**
- Meets assignment requirement for class-based design
- Encapsulates related functionality
- Easier dependency injection
- Better code organization


## Multi-Tenant Architecture Analysis


### Current Implementation: Collection-per-Tenant


**Pros:**
- Simple data isolation
- Easy to understand
- Good for demos and small deployments


**Cons:**
- **Scalability:** Max 5,000-10,000 collections per MongoDB cluster
- **Resource overhead:** Each collection has metadata/index overhead
- **Performance:** Collection creation adds latency to requests
- **Operations:** Fragmented backups and monitoring


**Suitable for:** < 1,000 organizations, prototypes, MVP



**2. Database-per-Tenant**
- Each organization gets separate database
- Better isolation than collection-per-tenant
- Still limited to ~10,000 databases
- Good for medium-scale B2B SaaS


**3. Hybrid Approach**
- Small tenants share collection with tenant_id
- Large tenants get dedicated databases
- Optimizes cost vs performance
- More complex to implement


## Project Structure


```
app/
├── api/routes/          # REST endpoints
├── services/            # Business logic
├── repositories/        # Data access layer
├── models/              # MongoDB models
├── schemas/             # Pydantic validation
├── middleware/          # Rate limiting, etc.
├── utils/               # Security, exceptions
└── core/                # Config, database
```


## Future Improvements


1. **Caching:** Add Redis for session management and frequently accessed data
2. **Background Jobs:** Use Celery for async data migrations
3. **Monitoring:** Implement Prometheus metrics and health checks
4. **Audit Logs:** Track all organization changes for compliance
5. **RBAC:** Support multiple admin roles per organization
6. **Migration Path:** Design transition from collection-per-tenant to shared collection


## Additional questions


#### Question: Do I think this is a good architecture with a scalable design?

**1. Scalability Bottleneck:** The "Collection-per-Tenant" pattern hits a hard ceiling. MongoDB performance degrades significantly when managing thousands of collections due to namespace limits and index overhead.

**2. Resource Intensity:** Each dynamic collection consumes file descriptors and memory for metadata, regardless of the data size.

**3. Operational Complexity:** Managing backups, monitoring, and schema migrations becomes fragmented across thousands of individual collections rather than a centralized schema.


 #### Question: What can be the trade-offs with the tech stack and design choices?

 **Benefit:** FastAPI's native async support paired with Motor allows for high-concurrency I/O, while MongoDB's flexible schema handles varying tenant data structures easily.

 **Cost:** We lose the strict ACID transaction guarantees and relational integrity constraints (foreign keys) standard in SQL databases like PostgreSQL, pushing data validation logic into the application layer.