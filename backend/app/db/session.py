"""
Database initialization and connection management.
"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
from app.core.config import settings
from app.db.models import Base
import sqlite3
import os

def get_engine():
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        pool_pre_ping=True,
        pool_recycle=300,
    )
    
    # Enable foreign key support for SQLite
    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        if isinstance(dbapi_connection, sqlite3.Connection):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
    
    return engine

# Create global SessionLocal
engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize database, creating tables if they don't exist."""
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    
    # Create database directory if it doesn't exist
    db_dir = os.path.dirname(db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    
    # Create tables
    Base.metadata.create_all(bind=engine)
