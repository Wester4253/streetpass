import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.core.security import create_access_token
from app.db.models import User, Friend
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
def users(db: Session):
    user1 = User(username="user1", password_hash="hash1")
    user2 = User(username="user2", password_hash="hash2")
    db.add_all([user1, user2])
    db.commit()
    db.refresh(user1)
    db.refresh(user2)
    yield user1, user2
    db.query(Friend).delete()
    db.query(User).delete()
    db.commit()

@pytest.fixture
def user1_token(users):
    user1, _ = users
    return create_access_token({"sub": user1.id})

def test_add_friend(users, user1_token):
    user1, user2 = users
    response = client.post(
        "/api/add-friend",
        headers={"Authorization": f"Bearer {user1_token}"},
        json={"friend_id": user2.id}
    )
    assert response.status_code == 200
    data = response.json()
    assert user2.id in data["friends"]

def test_add_nonexistent_friend(users, user1_token):
    response = client.post(
        "/api/add-friend",
        headers={"Authorization": f"Bearer {user1_token}"},
        json={"friend_id": "nonexistent"}
    )
    assert response.status_code == 404

def test_get_friends(db: Session, users, user1_token):
    user1, user2 = users
    # Create friendship
    friendship = Friend(user_id=user1.id, friend_id=user2.id)
    db.add(friendship)
    db.commit()
    
    response = client.get(
        "/api/friends",
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == user2.id