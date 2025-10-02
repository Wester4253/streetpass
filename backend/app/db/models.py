"""
SQLAlchemy database models for the StreetPass application.
"""
from datetime import datetime
import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, UniqueConstraint, func, event
from sqlalchemy.orm import declarative_base, relationship, validates
import re

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(32), unique=True, nullable=False, index=True)
    password_hash = Column(String(128), nullable=False)
    avatar_filename = Column(String(256), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    friends = relationship("Friend", back_populates="user", cascade="all, delete-orphan")

    @validates('username')
    def validate_username(self, key, username):
        if not re.match(r'^[a-zA-Z0-9_-]{3,32}$', username):
            raise ValueError('Username must be 3-32 chars, alphanumeric plus _-')
        return username

class Friend(Base):
    __tablename__ = "friends"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    friend_id = Column(String, ForeignKey("users.id"), nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    __table_args__ = (
        UniqueConstraint("user_id", "friend_id", name="uq_user_friend"),
    )
    user = relationship("User", foreign_keys=[user_id], back_populates="friends")

    @validates('friend_id')
    def validate_friend(self, key, friend_id):
        if friend_id == self.user_id:
            raise ValueError('Cannot friend yourself')
        return friend_id

# Event listeners for automatic timestamps
@event.listens_for(User, 'before_update')
def receive_before_update(mapper, connection, target):
    target.updated_at = datetime.utcnow()
