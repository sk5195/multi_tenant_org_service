from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import settings

_client: Optional[AsyncIOMotorClient] = None


def connect_to_mongo() -> None:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(settings.mongodb_uri)


def close_mongo_connection() -> None:
    global _client
    if _client is not None:
        _client.close()
        _client = None


def master_db() -> AsyncIOMotorDatabase:
    if _client is None:
        raise RuntimeError("Mongo client not initialized")
    return _client[settings.master_db_name]


def tenant_db() -> AsyncIOMotorDatabase:
    if _client is None:
        raise RuntimeError("Mongo client not initialized")
    return _client[settings.tenant_db_name]


async def ensure_master_indexes() -> None:
    db = master_db()
    await db["organizations"].create_index("name", unique=True)
    await db["organizations"].create_index("slug", unique=True)
    await db["admins"].create_index("email", unique=True)
    await db["admins"].create_index("org_id")
