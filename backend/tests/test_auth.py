import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.core.security import hash_password
from app.db.models import User
from main import app
from app.db.session import SessionLocal

client = TestClient(app)

@pytest.fixture
def db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def test_user(db: Session):
    user = User(
        username="testuser",
        password_hash=hash_password("testpass123")
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    yield user
    db.delete(user)
    db.commit()

def test_register_success():
    response = client.post(
        "/api/register",
        json={"username": "newuser", "password": "testpass123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "newuser"
    assert "token" in data

def test_register_duplicate_username(test_user):
    response = client.post(
        "/api/register",
        json={"username": "testuser", "password": "testpass123"}
    )
    assert response.status_code == 400

def test_login_success(test_user):
    response = client.post(
        "/api/login",
        json={"username": "testuser", "password": "testpass123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert data["user"]["username"] == "testuser"

def test_login_invalid_password(test_user):
    response = client.post(
        "/api/login",
        json={"username": "testuser", "password": "wrongpass"}
    )
    assert response.status_code == 401