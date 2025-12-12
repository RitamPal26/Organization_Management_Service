## Overview

The system uses MongoDB with a master database for metadata and dynamic collections for tenant data isolation.

## Master Database Collections

### organizations

Stores organization metadata and references to dynamic collections.

**Collection Name:** `organizations`

**Schema:**
```
{
  "_id": ObjectId("507f1f77bcf86cd799439011"),
  "organization_name": "acme_corp",
  "collection_name": "org_acme_corp",
  "admin_id": "507f191e810c19729de860ea",
  "created_at": ISODate("2025-12-12T10:00:00Z"),
  "updated_at": ISODate("2025-12-12T10:00:00Z")
}
```

**Fields:**
- `_id`: Unique organization identifier
- `organization_name`: Unique organization name (used in URLs)
- `collection_name`: Name of dynamic collection for this organization
- `admin_id`: Reference to admin user in admins collection
- `created_at`: Organization creation timestamp
- `updated_at`: Last modification timestamp

**Indexes:**
- `organization_name`: Unique index for fast lookups

---

### admins

Stores admin user credentials and organization associations.

**Collection Name:** `admins`

**Schema:**
```
{
  "_id": ObjectId("507f191e810c19729de860ea"),
  "email": "admin@acme.com",
  "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyB7Ow5L6xTi",
  "organization_id": "507f1f77bcf86cd799439011",
  "organization_name": "acme_corp",
  "created_at": ISODate("2025-12-12T10:00:00Z")
}
```

**Fields:**
- `_id`: Unique admin identifier
- `email`: Admin email (unique)
- `hashed_password`: bcrypt-hashed password with salt
- `organization_id`: Reference to organization in organizations collection
- `organization_name`: Denormalized for faster queries
- `created_at`: Admin creation timestamp

**Indexes:**
- `email`: Unique index for login lookups
- `organization_id`: Index for organization-based queries

**Security:**
- Passwords are hashed using bcrypt with automatic salt generation
- Plain text passwords are never stored

---

## Dynamic Collections

Each organization gets a dedicated collection for data isolation.

**Naming Pattern:** `org_<organization_name>`

**Examples:**
- `org_acme_corp`
- `org_xyz_company`
- `org_techstartup`

**Schema Validation:**

Collections are created with optional JSON schema validation:
```
{
  validator: {
    $jsonSchema: {
      bsonType: "object",
      description: "Organization-specific data collection"
    }
  }
}
```

**Purpose:**
- Isolates tenant data
- Simplifies per-tenant backup/restore
- Provides clear data boundaries

**Trade-offs:**
- Limited scalability (max ~5,000 collections recommended)
- Resource overhead per collection

---

## Data Flow Examples

### Creating Organization

1. Check if organization name exists in `organizations`
2. Check if admin email exists in `admins`
3. Insert document into `organizations`
4. Insert document into `admins` with hashed password
5. Create dynamic collection `org_<name>`
6. Update organization document with admin_id reference

### Updating Organization

1. Fetch old organization data from `organizations`
2. Create new collection `org_<new_name>`
3. Copy all documents from old collection to new
4. Update `organizations` collection with new name and collection_name
5. Update `admins` collection with new organization_name
6. Drop old collection

### Deleting Organization

1. Verify admin owns organization
2. Drop dynamic collection `org_<name>`
3. Delete document from `admins`
4. Delete document from `organizations`

---

## Connection Configuration

**Environment Variables:**
```
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
DATABASE_NAME=master_db
```

**Connection Pooling:**
- Motor handles connection pooling automatically
- Default pool size: 100 connections
- Async operations prevent blocking

**Database Client:**
- Initialized at application startup
- Closed at application shutdown
- Single client instance shared across application

