import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.core.security import create_access_token
from app.db.models import User
from main import app
from app.db.session import SessionLocal
import os
import io
from PIL import Image

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
    user = User(username="testuser", password_hash="testhash")
    db.add(user)
    db.commit()
    db.refresh(user)
    yield user
    db.delete(user)
    db.commit()

@pytest.fixture
def auth_headers(test_user):
    token = create_access_token({"sub": test_user.id})
    return {"Authorization": f"Bearer {token}"}

def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_profile(test_user, auth_headers):
    response = client.get("/api/profile", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == test_user.username

def test_avatar_upload(test_user, auth_headers):
    # Create a test image
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    files = {"file": ("test.png", img_bytes, "image/png")}
    response = client.post("/api/upload-avatar", headers=auth_headers, files=files)
    assert response.status_code == 200
    data = response.json()
    assert "avatar_url" in data
    
    # Clean up
    avatar_path = f"avatars/{test_user.id}.png"
    if os.path.exists(avatar_path):
        os.remove(avatar_path)

def test_full_friend_flow(db: Session):
    # Register two users
    response1 = client.post("/api/register", json={
        "username": "user1",
        "password": "password123"
    })
    assert response1.status_code == 200
    user1_token = response1.json()["token"]
    user1_id = response1.json()["id"]
    
    response2 = client.post("/api/register", json={
        "username": "user2",
        "password": "password123"
    })
    assert response2.status_code == 200
    user2_token = response2.json()["token"]
    user2_id = response2.json()["id"]
    
    # User1 adds User2 as friend
    response = client.post(
        "/api/add-friend",
        headers={"Authorization": f"Bearer {user1_token}"},
        json={"friend_id": user2_id}
    )
    assert response.status_code == 200
    
    # Check User1's friends list
    response = client.get(
        "/api/friends",
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    assert response.status_code == 200
    friends = response.json()
    assert len(friends) == 1
    assert friends[0]["id"] == user2_id