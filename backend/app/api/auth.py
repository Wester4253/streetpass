from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, constr
from app.db import crud
from app.core.security import create_access_token
from app.core.config import settings
from app.core.dependencies import get_db
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from typing import Optional

router = APIRouter(tags=["auth"])

class RegisterRequest(BaseModel):
    username: constr(min_length=3, max_length=32, pattern=r'^[a-zA-Z0-9_-]+$')
    password: constr(min_length=8)

class RegisterResponse(BaseModel):
    id: str
    username: str
    token: str

@router.post("/register", response_model=RegisterResponse)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    if len(data.password) < 8:
        raise HTTPException(status_code=400, detail="Password too short (min 8 chars)")
    if crud.get_user_by_username(db, data.username):
        raise HTTPException(status_code=400, detail="Username taken")
    user = crud.create_user(db, data.username, data.password)
    token = create_access_token({"sub": user.id}, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    return RegisterResponse(id=user.id, username=user.username, token=token)

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    token: str
    user: dict

@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = crud.verify_user_password(db, data.username, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user.id}, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    return LoginResponse(token=token, user={"id": user.id, "username": user.username, "avatar_url": f"/api/avatar/{user.id}"})
