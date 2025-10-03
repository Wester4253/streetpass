from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from app.core.config import Settings, settings
from app.core.middleware import RateLimiter
from app.db.session import init_db
from app.api import auth, users, friends

# Initialize FastAPI app
app = FastAPI(
    title="StreetPass",
    version="1.0.0",
    description="A lightweight StreetPass-style social app",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# Rate limiting
app.add_middleware(RateLimiter, requests_per_minute=60)

# Error handling
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Static files
app.mount("/", StaticFiles(directory=settings.STATIC_DIR, html=True), name="static")

# Routers
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(friends.router, prefix="/api")

@app.on_event("startup")
def on_startup():
    print(f"\n[StreetPass] Starting server at http://{settings.BACKEND_HOST}:{settings.BACKEND_PORT}\n")
    print(f"Environment: {settings.ENV}")
    print(f"Database: {settings.DATABASE_URL}")

    # Create required directories
    Path(settings.AVATAR_DIR).mkdir(parents=True, exist_ok=True)
    Path(settings.STATIC_DIR).mkdir(parents=True, exist_ok=True)

    # Initialize database
    init_db()

@app.get("/api/health")
def health():
    return {"status": "ok"}
