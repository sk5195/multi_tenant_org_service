from fastapi import HTTPException, status

from app.core.security import create_access_token, verify_password


class AuthService:
    def __init__(self, *, master_db):
        self._admins = master_db["admins"]

    async def login(self, *, email: str, password: str) -> str:
        admin = await self._admins.find_one({"email": email})
        if not admin:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        if not verify_password(password, admin.get("password_hash", "")):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        return create_access_token(
            subject=str(admin["_id"]),
            org_id=str(admin["org_id"]),
            email=admin["email"],
        )
