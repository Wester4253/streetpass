from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db import crud
from app.core.security import decode_access_token
from app.core.config import settings
from pydantic import BaseModel
from app.api.users import get_current_user

router = APIRouter()

class AddFriendRequest(BaseModel):
    friend_id: str

@router.post("/add-friend")
def add_friend(data: AddFriendRequest, user=Depends(get_current_user)):
    db = SessionLocal()
    friend = crud.get_user_by_id(db, data.friend_id)
    if not friend:
        raise HTTPException(status_code=404, detail="Friend not found")
    if not crud.add_friend(db, user.id, data.friend_id):
        raise HTTPException(status_code=400, detail="Already friends or invalid")
    # Return updated friends list
    friends = crud.get_friends(db, user.id)
    return {"friends": friends}

class FriendInfo(BaseModel):
    id: str
    username: str
    avatar_url: str
    added_at: str

@router.get("/friends", response_model=list[FriendInfo])
def get_friends(user=Depends(get_current_user)):
    db = SessionLocal()
    friend_ids = crud.get_friends(db, user.id)
    friends = []
    for fid in friend_ids:
        f = crud.get_user_by_id(db, fid)
        if f:
            friends.append(FriendInfo(
                id=f.id,
                username=f.username,
                avatar_url=f"/api/avatar/{f.id}",
                added_at=f.created_at.isoformat(),
            ))
    return friends
