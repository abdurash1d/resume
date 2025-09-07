import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.base import Base, get_db
from app.models.user import User
from app.core.security import create_access_token, get_password_hash

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override get_db for testing
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Client fixture
@pytest.fixture(scope="module")
def client():
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create test client
    with TestClient(app) as test_client:
        yield test_client
    
    # Clean up
    Base.metadata.drop_all(bind=engine)

# Test user fixture
@pytest.fixture(scope="function")
def test_user(client):
    db = next(override_get_db())
    user_email = "test@example.com"
    user_password = "testpass123"
    
    # Delete user if it exists from a previous run
    existing_user = db.query(User).filter(User.email == user_email).first()
    if existing_user:
        db.delete(existing_user)
        db.commit()

    user = User(
        email=user_email,
        hashed_password=get_password_hash(user_password),
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# Auth token fixture
@pytest.fixture(scope="function")
def auth_token(test_user):
    return create_access_token(data={"sub": test_user.email})

def test_create_resume(client, test_user, auth_token):
    """Test creating a new resume"""
    resume_data = {
        "title": "Test Resume",
        "content": "This is a test resume content."
    }
    
    response = client.post(
        "/api/resumes",
        json=resume_data,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Resume"
    assert data["content"] == "This is a test resume content."
    assert data["user_id"] == test_user.id

def test_get_resumes(client, test_user, auth_token):
    """Test getting all resumes for a user"""
    response = client.get(
        "/api/resumes",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# Add more test cases for other endpoints (get by id, update, delete, improve)
