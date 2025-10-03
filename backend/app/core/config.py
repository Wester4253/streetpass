"""
StreetPass configuration settings.
Edit this file directly to change settings.
No .env files needed.
"""
import os
from pathlib import Path
from typing import List

# Get base directory (where this config.py lives)
BASE_DIR = Path(__file__).parents[3]

class Settings:
    """
    All StreetPass settings in one place.
    Edit these values directly to configure the application.
    """

    # Server Settings
    BACKEND_HOST: str = "0.0.0.0"     # Listen on all interfaces
    BACKEND_PORT: int = 8010          # Backend API port

    # Frontend Settings
    FRONTEND_HOST: str = "0.0.0.0"    # Frontend server host
    FRONTEND_PORT: int = 8080         # Frontend server port

    # Security
    SECRET_KEY: str = "changeme-use-os-urandom-in-production"  # JWT signing key
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Database
    DATABASE_URL: str = f"sqlite:///{BASE_DIR}/backend/streetpass.db"

    # File Storage Paths
    AVATAR_DIR: str = str(BASE_DIR / "backend" / "avatars")
    STATIC_DIR: str = str(BASE_DIR / "frontend")
    MAX_AVATAR_SIZE: int = 500_000  # 500KB

    # Security and CORS
    ALLOWED_HOSTS: List[str] = [
        "localhost",
        "127.0.0.1",
        "*.ts.net"  # For Tailscale support
    ]

    CORS_ORIGINS: List[str] = [
        "http://localhost:8080",
        "http://127.0.0.1:8080"
    ]

    # Environment
    ENV: str = "development"  # or "production"
    DEBUG: bool = True

# Global settings instance
settings = Settings()

def init_directories() -> None:
    """Initialize required directories and validate settings."""
    # Create required directories
    os.makedirs(settings.AVATAR_DIR, exist_ok=True)
    os.makedirs(settings.STATIC_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(settings.DATABASE_URL.replace("sqlite:///", "")), exist_ok=True)

    # Validate critical settings
    if settings.SECRET_KEY == "changeme-supersecret":
        print("Warning: Using default SECRET_KEY. This is insecure!", file=sys.stderr)

    if settings.ENV == "production":
        if settings.DEBUG:
            print("Warning: DEBUG mode is enabled in production!", file=sys.stderr)
        if "localhost" in settings.ALLOWED_HOSTS:
            print("Warning: localhost in ALLOWED_HOSTS in production!", file=sys.stderr)

    # Log configuration in debug mode
    if settings.DEBUG:
        print(f"\nConfiguration:")
        print(f"- Environment: {settings.ENV}")
        print(f"- Backend: http://{settings.BACKEND_HOST}:{settings.BACKEND_PORT}")
        print(f"- Database: {settings.DATABASE_URL}")
        print(f"- Avatars: {settings.AVATAR_DIR}")
        print(f"- Static: {settings.STATIC_DIR}")
        print(f"- CORS Origins: {', '.join(settings.CORS_ORIGINS)}")
        print()
