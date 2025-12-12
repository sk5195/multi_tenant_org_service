from fastapi import APIRouter, Depends, Query

from app.db.mongo import master_db, tenant_db
from app.routes.deps import get_current_admin
from app.schemas.org import (
    OrgCreateRequest,
    OrgCreateResponse,
    OrgDeleteRequest,
    OrgGetResponse,
    OrgUpdateRequest,
)
from app.services.org_service import OrgService

router = APIRouter(prefix="/org", tags=["org"])


@router.post("/create", response_model=OrgCreateResponse)
async def create_organization(payload: OrgCreateRequest) -> OrgCreateResponse:
    service = OrgService(master_db=master_db(), tenant_db=tenant_db())
    result = await service.create_org(
        organization_name=payload.organization_name,
        email=payload.email,
        password=payload.password,
    )
    return OrgCreateResponse(
        id=str(result["org_id"]),
        organization_name=result["name"],
        slug=result["slug"],
        collection_name=result["collection_name"],
        admin_id=str(result["admin_id"]),
        created_at=result["created_at"],
    )


@router.get("/get", response_model=OrgGetResponse)
async def get_organization_by_name(organization_name: str = Query(min_length=1, max_length=200)) -> OrgGetResponse:
    service = OrgService(master_db=master_db(), tenant_db=tenant_db())
    org = await service.get_org_by_name(organization_name=organization_name)

    return OrgGetResponse(
        id=str(org["_id"]),
        organization_name=org["name"],
        slug=org["slug"],
        collection_name=org["collection_name"],
        admin_id=str(org["admin_id"]),
        created_at=org["created_at"],
        updated_at=org.get("updated_at"),
    )


@router.put("/update", response_model=OrgGetResponse)
async def update_organization(payload: OrgUpdateRequest, current_admin: dict = Depends(get_current_admin)) -> OrgGetResponse:
    service = OrgService(master_db=master_db(), tenant_db=tenant_db())
    org = await service.update_org(
        organization_name=payload.organization_name,
        new_organization_name=payload.new_organization_name,
        email=payload.email,
        password=payload.password,
        current_admin=current_admin,
    )

    return OrgGetResponse(
        id=str(org["_id"]),
        organization_name=org["name"],
        slug=org["slug"],
        collection_name=org["collection_name"],
        admin_id=str(org["admin_id"]),
        created_at=org["created_at"],
        updated_at=org.get("updated_at"),
    )


@router.delete("/delete")
async def delete_organization(payload: OrgDeleteRequest, current_admin: dict = Depends(get_current_admin)) -> dict:
    service = OrgService(master_db=master_db(), tenant_db=tenant_db())
    await service.delete_org(organization_name=payload.organization_name, current_admin=current_admin)

    return {"status": "deleted", "organization_name": payload.organization_name}
