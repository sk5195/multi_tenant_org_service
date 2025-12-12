from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import HTTPException, status
from pymongo.errors import DuplicateKeyError

from app.core.security import hash_password
from app.core.tenancy import org_collection_name, slugify_org_name


class OrgService:
    def __init__(self, *, master_db, tenant_db):
        self._orgs = master_db["organizations"]
        self._admins = master_db["admins"]
        self._tenant_db = tenant_db

    async def create_org(self, *, organization_name: str, email: str, password: str) -> dict[str, Any]:
        existing = await self._orgs.find_one({"name": organization_name})
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Organization already exists")

        slug = slugify_org_name(organization_name)
        collection_name = org_collection_name(organization_name)

        if await self._tenant_db.list_collection_names(filter={"name": collection_name}):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Organization collection already exists")

        await self._tenant_db.create_collection(collection_name)

        now = datetime.now(timezone.utc)
        org_doc: dict[str, Any] = {
            "name": organization_name,
            "slug": slug,
            "collection_name": collection_name,
            "tenant_db_name": self._tenant_db.name,
            "created_at": now,
            "updated_at": None,
            "admin_id": None,
        }
        org_insert = await self._orgs.insert_one(org_doc)

        admin_doc = {
            "email": email,
            "password_hash": hash_password(password),
            "org_id": org_insert.inserted_id,
            "created_at": now,
        }
        try:
            admin_insert = await self._admins.insert_one(admin_doc)
        except DuplicateKeyError:
            await self._orgs.delete_one({"_id": org_insert.inserted_id})
            await self._tenant_db.drop_collection(collection_name)
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already in use")
        except Exception:
            await self._orgs.delete_one({"_id": org_insert.inserted_id})
            await self._tenant_db.drop_collection(collection_name)
            raise

        await self._orgs.update_one({"_id": org_insert.inserted_id}, {"$set": {"admin_id": admin_insert.inserted_id}})

        return {
            "org_id": org_insert.inserted_id,
            "admin_id": admin_insert.inserted_id,
            "name": organization_name,
            "slug": slug,
            "collection_name": collection_name,
            "created_at": now,
        }

    async def get_org_by_name(self, *, organization_name: str) -> dict[str, Any]:
        org = await self._orgs.find_one({"name": organization_name})
        if not org:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
        return org

    async def update_org(
        self,
        *,
        organization_name: str,
        new_organization_name: Optional[str],
        email: str,
        password: str,
        current_admin: dict,
    ) -> dict[str, Any]:
        org = await self._orgs.find_one({"name": organization_name})
        if not org:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

        if str(current_admin["org_id"]) != str(org["_id"]):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")

        now = datetime.now(timezone.utc)

        new_name = new_organization_name.strip() if new_organization_name else None
        if new_name and new_name != org["name"]:
            if await self._orgs.find_one({"name": new_name}):
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Organization name already exists")

            new_slug = slugify_org_name(new_name)
            new_collection = org_collection_name(new_name)

            if await self._tenant_db.list_collection_names(filter={"name": new_collection}):
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Target collection already exists")

            old_collection = org["collection_name"]
            await self._tenant_db.create_collection(new_collection)

            new_coll = self._tenant_db[new_collection]
            old_coll = self._tenant_db[old_collection]

            try:
                batch: list[dict[str, Any]] = []
                async for doc in old_coll.find({}):
                    doc.pop("_id", None)
                    batch.append(doc)
                    if len(batch) >= 1000:
                        await new_coll.insert_many(batch)
                        batch = []
                if batch:
                    await new_coll.insert_many(batch)

                await self._tenant_db.drop_collection(old_collection)

                await self._orgs.update_one(
                    {"_id": org["_id"]},
                    {
                        "$set": {
                            "name": new_name,
                            "slug": new_slug,
                            "collection_name": new_collection,
                            "updated_at": now,
                        }
                    },
                )
                org = await self._orgs.find_one({"_id": org["_id"]})
            except Exception:
                await self._tenant_db.drop_collection(new_collection)
                raise

        admin_updates: dict[str, Any] = {
            "email": email,
            "password_hash": hash_password(password),
        }

        try:
            await self._admins.update_one({"_id": current_admin["_id"]}, {"$set": admin_updates})
        except DuplicateKeyError:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already in use")

        return await self._orgs.find_one({"_id": org["_id"]})

    async def delete_org(self, *, organization_name: str, current_admin: dict) -> None:
        org = await self._orgs.find_one({"name": organization_name})
        if not org:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

        if str(current_admin["org_id"]) != str(org["_id"]):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")

        await self._tenant_db.drop_collection(org["collection_name"])
        await self._admins.delete_many({"org_id": org["_id"]})
        await self._orgs.delete_one({"_id": org["_id"]})
