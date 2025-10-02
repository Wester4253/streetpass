from sqlalchemy.orm import Session
from app.db import models
from app.core.security import hash_password, verify_password
from datetime import datetime
import uuid

# User CRUD

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_id(db: Session, user_id: str):
    return db.query(models.User).filter(models.User.id == user_id).first()

def create_user(db: Session, username: str, password: str):
    user = models.User(
        username=username,
        password_hash=hash_password(password),
        created_at=datetime.utcnow(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def verify_user_password(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if user and verify_password(password, user.password_hash):
        return user
    return None

# Friend CRUD

def add_friend(db: Session, user_id: str, friend_id: str):
    if user_id == friend_id:
        return None
    # Check if already friends
    exists = db.query(models.Friend).filter_by(user_id=user_id, friend_id=friend_id).first()
    if exists:
        return None
    # Add both directions
    f1 = models.Friend(user_id=user_id, friend_id=friend_id, added_at=datetime.utcnow())
    f2 = models.Friend(user_id=friend_id, friend_id=user_id, added_at=datetime.utcnow())
    db.add_all([f1, f2])
    db.commit()
    return True

def get_friends(db: Session, user_id: str):
    friends = db.query(models.Friend).filter_by(user_id=user_id).all()
    return [f.friend_id for f in friends]
