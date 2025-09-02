# Resume Management System

A modern, FastAPI-based resume management system with JWT authentication and AI-powered resume improvements.

## 🔧 Recent Fixes & Updates

### Fixed Issues
1. **Database Connection**
   - Resolved PostgreSQL connection issues by ensuring proper port mapping (5433:5432)
   - Updated database URL in `.env` to use the correct port

2. **Docker Configuration**
   - Fixed permission issues with Docker volumes
   - Added proper environment variable handling
   - Configured health checks for database service

3. **Application Startup**
   - Resolved circular import issues in models and schemas
   - Fixed logging configuration to prevent startup errors
   - Added proper error handling for missing environment variables

4. **API Endpoints**
   - Ensured all endpoints are properly protected with JWT authentication
   - Fixed response models and error handling

### Project Structure Overview

```
.
├── app/
│   ├── api/                  # API route handlers
│   │   ├── __init__.py
│   │   ├── auth.py           # Authentication endpoints
│   │   └── resume.py         # Resume management endpoints
│   │
│   ├── core/                 # Core application configuration
│   │   ├── __init__.py
│   │   ├── config.py         # Application settings
│   │   └── logging_config.py # Logging configuration
│   │
│   ├── crud/                 # Database operations
│   │   ├── __init__.py
│   │   ├── resume.py         # Resume CRUD operations
│   │   └── user.py           # User CRUD operations
│   │
│   ├── db/                   # Database configuration
│   │   ├── __init__.py
│   │   └── base.py           # Database models and session
│   │
│   ├── models/               # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── resume.py         # Resume model
│   │   └── user.py           # User model
│   │
│   ├── schemas/              # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── resume.py         # Resume schemas
│   │   └── user.py           # User schemas
│   │
│   ├── static/               # Static files (CSS, JS, images)
│   ├── templates/            # HTML templates (Jinja2)
│   ├── main.py               # Application entry point
│   └── run.py                # Alternative entry point with PYTHONPATH fix
│
├── migrations/               # Database migrations (Alembic)
│   ├── versions/             # Migration scripts
│   ├── env.py                # Migration environment
│   └── script.py.mako        # Migration template
│
├── tests/                    # Test files
├── .dockerignore
├── .env.example              # Example environment variables
├── .gitignore
├── Dockerfile                # Production Dockerfile
├── docker-compose.yml        # Development environment
├── docker-compose.override.yml # Override for local development
├── alembic.ini               # Alembic configuration
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## ✨ Features

- 🔐 **Authentication**
  - User registration with email/password
  - JWT-based authentication
  - Protected API endpoints

- 📝 **Resume Management**
  - Create, read, update, and delete resumes
  - Track resume edit history
  - AI-powered resume improvements
  - Responsive web interface

- 🛠 **Technical Stack**
  - **Backend**: FastAPI
  - **Database**: PostgreSQL with SQLAlchemy ORM
  - **Authentication**: JWT (JSON Web Tokens)
  - **Frontend**: Jinja2 templates with Tailwind CSS
  - **Containerization**: Docker & Docker Compose
  - **Testing**: Pytest

- 📚 **API Documentation**
  - Interactive API docs at `/docs`
  - OpenAPI/Swagger support

## Prerequisites

- Docker and Docker Compose
- Python 3.9+

## Getting Started

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.9+ (for local development)

### With Docker (Recommended)

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd resume-app
   ```

2. Set up environment variables:
   ```bash
   cp .env.example .env
   # Update the .env file with your database credentials if needed
   ```

3. Build and start the application with Docker Compose:
   ```bash
   # Build the Docker images
   docker-compose build
   
   # Start the services in detached mode
   docker-compose up -d
   
   # View logs (optional)
   docker-compose logs -f
   ```
   
4. Access the application:
   - Web Interface: `http://localhost:8000`
   - API Documentation: `http://localhost:8000/docs`
   - Database: Running on port 5433 (PostgreSQL)

5. Common Docker commands:
   ```bash
   # Stop all services
   docker-compose down
   
   # Rebuild and restart
   docker-compose up -d --build
   
   # View running containers
   docker ps
   
   # View logs for a specific service
   docker-compose logs -f web
   ```

### Local Development Setup (Without Docker)

1. **Set up the database**:
   - Install PostgreSQL if not already installed
   - Create a new database named `resume_db`
   - Update the `.env` file with your database credentials

2. **Set up Python environment**:
   ```bash
   # Create and activate virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Update the .env file with your database credentials
   # Make sure to set DATABASE_URL to your local PostgreSQL instance
   ```

4. **Initialize the database**:
   ```bash
   # Run migrations
   alembic upgrade head
   
   # Create initial data (if needed)
   python init_db.py
   ```

5. **Run the application**:
   ```bash
   # Development server with auto-reload
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   
   # Or use the run.py script which handles PYTHONPATH
   python run.py
   ```
   
   The application will be available at `http://localhost:8000`

6. **Access the API documentation**:
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

## 📝 API Endpoints

### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login and get access token

### Resumes
- `GET /resumes/` - List all resumes for current user
- `POST /resumes/` - Create a new resume
- `GET /resumes/{resume_id}` - Get a specific resume
- `PUT /resumes/{resume_id}` - Update a resume
- `DELETE /resumes/{resume_id}` - Delete a resume
- `POST /resumes/{resume_id}/improve` - Improve resume content using AI

## 🧪 Running Tests

1. Ensure test database is running:
   ```bash
   docker-compose -f docker-compose.test.yml up -d
   ```

2. Run tests:
   ```bash
   pytest -v
   ```

## 🔧 Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# Application
DEBUG=True
PROJECT_NAME="Resume Manager"
API_V1_STR=/api

# Database
DATABASE_URL=postgresql://postgres:postgres@db:5432/resume_db
# For local development without Docker, use:
# DATABASE_URL=postgresql://postgres:postgres@localhost:5433/resume_db

# JWT Authentication
SECRET_KEY=your-secret-key-here  # Change this in production!
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS (Comma-separated list of origins)
BACKEND_CORS_ORIGINS=["http://localhost:8000", "http://127.0.0.1:8000"]

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json  # or 'plain'
```

### Important Notes:
1. The `SECRET_KEY` should be kept secret in production.
2. The default database credentials are for development only.
3. In production, set `DEBUG=False` and use proper CORS settings.
4. For Docker, the database host is `db` (as defined in docker-compose.yml).
5. For local development without Docker, update the `DATABASE_URL` to point to your local PostgreSQL instance.

## 📚 API Documentation

Once the application is running, you can access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🤝 Contributing

1. Fork the repository
2. Create a new branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
.
├── app/
│   ├── api/                  # API routes
│   ├── core/                 # Core functionality (security, config)
│   ├── crud/                 # Database operations
│   ├── db/                   # Database configuration
│   ├── models/               # SQLAlchemy models
│   ├── schemas/              # Pydantic models
│   ├── static/               # Static files
│   ├── templates/            # HTML templates
│   └── main.py               # Application entry point
├── migrations/               # Database migrations (Alembic)
├── tests/                    # Test files
├── .env.example              # Example environment variables
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```
# Database
DATABASE_URL=postgresql://postgres:postgres@db:5432/resume_db

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# App
DEBUG=True
```

## Running Tests

To run the tests, use the following command:

```bash
pytest
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
