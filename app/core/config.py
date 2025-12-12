import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    mongodb_uri: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    master_db_name: str = os.getenv("MASTER_DB_NAME", "master")
    tenant_db_name: str = os.getenv("TENANT_DB_NAME", "tenant_data")

    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "change-me")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))


settings = Settings()
