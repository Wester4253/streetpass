from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Generator
from app.db.session import SessionLocal
from app.core.security import decode_access_token
from app.db import crud

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    token: str = Depends(lambda x: x.headers.get("authorization", "").replace("Bearer ", "")),
    db: Session = Depends(get_db)
):
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = crud.get_user_by_id(db, payload["sub"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user