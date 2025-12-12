# Organization Management Service

A multi-tenant organization management backend service built with FastAPI and MongoDB. Supports dynamic collection creation per organization with secure JWT-based authentication.

## Documentation

- [API Reference](docs/api.md) - Endpoint details and examples
- [Architecture](docs/architecture.md) - System design and technical decisions
- [Database Schema](docs/database.md) - Data models and structure

## Features

- Multi-tenant architecture with isolated data storage
- JWT-based authentication with bcrypt password hashing
- Dynamic MongoDB collection creation per organization
- RESTful API with automatic OpenAPI documentation
- Rate limiting and security headers
- Comprehensive test suite

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
