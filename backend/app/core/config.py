import os
from dotenv import load_dotenv
from typing import List

load_dotenv()

class Settings:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "changeme")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///streetpass.db")
    ALLOWED_HOSTS: List[str] = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 1440))
    CORS_ORIGINS: List[str] = os.getenv("CORS_ORIGINS", "http://localhost").split(",")
    MAX_AVATAR_SIZE: int = int(os.getenv("MAX_AVATAR_SIZE", 500000))
    AVATAR_DIR: str = os.path.abspath(os.getenv("AVATAR_DIR", "avatars"))
    STATIC_DIR: str = os.path.abspath(os.getenv("STATIC_DIR", "app/static"))

settings = Settings()

def init_directories():
    os.makedirs(settings.AVATAR_DIR, exist_ok=True)
