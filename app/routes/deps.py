from bson import ObjectId
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.security import decode_token
from app.db.mongo import master_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/admin/login")


async def get_current_admin(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        payload = decode_token(token)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    admins = master_db()["admins"]
    try:
        admin_id = ObjectId(sub)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    admin = await admins.find_one({"_id": admin_id})
    if not admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    return admin
