# API Reference

Complete API documentation for Organization Management Service.

## Base URL

```
http://localhost:8000
```

## Authentication

Protected endpoints require JWT token in Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Endpoints

### 1. Create Organization

**Endpoint:** `POST /org/create`

**Authentication:** Not required

**Request Body:**
```
{
  "organization_name": "acme_corp",
  "email": "admin@acme.com",
  "password": "SecurePass123"
}
```

**Response:** `201 Created`
```
{
  "organization_name": "acme_corp",
  "collection_name": "org_acme_corp",
  "admin_email": "admin@acme.com",
  "created_at": "2025-12-12T10:00:00"
}
```

**What it does:**
- Validates organization name uniqueness
- Creates organization metadata in master database
- Creates admin user with hashed password
- Dynamically creates MongoDB collection `org_<name>`

**Errors:**
- `400` - Organization or email already exists
- `422` - Validation error (invalid email, short password)

---

### 2. Admin Login

**Endpoint:** `POST /admin/login`

**Authentication:** Not required

**Request Body:**
```
{
  "email": "admin@acme.com",
  "password": "SecurePass123"
}
```

**Response:** `200 OK`
```
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "admin_email": "admin@acme.com",
  "organization_name": "acme_corp",
  "organization_id": "507f1f77bcf86cd799439011"
}
```

**Token Expiration:** 30 minutes (configurable)

**Errors:**
- `401` - Invalid email or password

---

### 3. Get Organization

**Endpoint:** `GET /org/get`

**Authentication:** Not required

**Query Parameters:**
- `organization_name` (required): Name of the organization

**Example:**
```
GET /org/get?organization_name=acme_corp
```

**Response:** `200 OK`
```
{
  "organization_name": "acme_corp",
  "collection_name": "org_acme_corp",
  "admin_email": "admin@acme.com",
  "created_at": "2025-12-12T10:00:00"
}
```

**Errors:**
- `404` - Organization not found

---

### 4. Update Organization

**Endpoint:** `PUT /org/update`

**Authentication:** Required (JWT token)

**Request Body:**
```
{
  "organization_name": "acme_corporation",
  "email": "admin@acme.com",
  "password": "NewPassword123"
}
```

**Response:** `200 OK`
```
{
  "organization_name": "acme_corporation",
  "collection_name": "org_acme_corporation",
  "admin_email": "admin@acme.com",
  "created_at": "2025-12-12T10:00:00"
}
```

**What it does:**
1. Validates JWT token and extracts admin info
2. Creates new collection `org_<new_name>`
3. Migrates all documents from old collection
4. Updates organization and admin metadata
5. Deletes old collection

**Errors:**
- `400` - New organization name already exists
- `401` - Invalid or expired token
- `403` - Not authorized to update this organization

---

### 5. Delete Organization

**Endpoint:** `DELETE /org/delete`

**Authentication:** Required (JWT token)

**Request Body:**
```
{
  "organization_name": "acme_corporation"
}
```

**Response:** `200 OK`
```
{
  "message": "Organization 'acme_corporation' deleted successfully"
}
```

**What it does:**
1. Validates JWT token
2. Verifies admin owns this organization
3. Drops dynamic collection
4. Deletes admin from master database
5. Deletes organization from master database

**Errors:**
- `401` - Invalid or expired token
- `403` - You can only delete your own organization
- `404` - Organization not found

---

## Rate Limiting

All endpoints are rate limited to **100 requests per minute per IP address**.

**Response when exceeded:** `429 Too Many Requests`
```
{
  "detail": "Too many requests. Please try again later."
}
```

## Error Response Format

All errors follow consistent format:
```
{
  "detail": "Error message describing what went wrong"
}
```
