from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Response
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db import crud
from app.core.security import decode_access_token
from app.core.config import settings
from pydantic import BaseModel
import os
from PIL import Image
import io
import qrcode

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(lambda authorization: authorization.headers.get("authorization", "").replace("Bearer ", ""))):
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    db = SessionLocal()
    user = crud.get_user_by_id(db, payload["sub"])
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

class ProfileResponse(BaseModel):
    id: str
    username: str
    avatar_url: str
    created_at: str

@router.get("/profile", response_model=ProfileResponse)
def profile(user=Depends(get_current_user)):
    return ProfileResponse(
        id=user.id,
        username=user.username,
        avatar_url=f"/api/avatar/{user.id}",
        created_at=user.created_at.isoformat(),
    )

@router.post("/upload-avatar")
def upload_avatar(file: UploadFile = File(...), user=Depends(get_current_user)):
    if file.content_type not in ["image/png", "image/jpeg"]:
        raise HTTPException(status_code=400, detail="Invalid file type")
    contents = file.file.read()
    if len(contents) > settings.MAX_AVATAR_SIZE:
        raise HTTPException(status_code=400, detail="File too large")
    # Save as PNG
    img = Image.open(io.BytesIO(contents)).convert("RGBA")
    avatar_path = os.path.join(settings.AVATAR_DIR, f"{user.id}.png")
    img.save(avatar_path, format="PNG")
    db = SessionLocal()
    db_user = crud.get_user_by_id(db, user.id)
    db_user.avatar_filename = f"{user.id}.png"
    db.commit()
    return {"avatar_url": f"/api/avatar/{user.id}"}

@router.get("/avatar/{user_id}")
def get_avatar(user_id: str):
    avatar_path = os.path.join(settings.AVATAR_DIR, f"{user_id}.png")
    if not os.path.exists(avatar_path):
        # Return default avatar
        default_path = os.path.join(settings.STATIC_DIR, "icons", "default.png")
        if not os.path.exists(default_path):
            return Response(status_code=404)
        with open(default_path, "rb") as f:
            return Response(content=f.read(), media_type="image/png")
    with open(avatar_path, "rb") as f:
        return Response(content=f.read(), media_type="image/png")

@router.get("/qr/{user_id}")
def get_qr(user_id: str):
    # QR encodes JSON: {"id": user_id}
    qr = qrcode.QRCode(box_size=6, border=2)
    qr.add_data(f'{{"id":"{user_id}"}}')
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return Response(content=buf.getvalue(), media_type="image/png")
