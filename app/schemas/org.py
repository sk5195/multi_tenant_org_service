from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class OrgCreateRequest(BaseModel):
    organization_name: str = Field(min_length=1, max_length=200)
    email: EmailStr
    password: str = Field(min_length=8, max_length=200)


class OrgCreateResponse(BaseModel):
    id: str
    organization_name: str
    slug: str
    collection_name: str
    admin_id: str
    created_at: datetime


class OrgGetResponse(BaseModel):
    id: str
    organization_name: str
    slug: str
    collection_name: str
    admin_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class OrgUpdateRequest(BaseModel):
    organization_name: str = Field(min_length=1, max_length=200)
    email: EmailStr
    password: str = Field(min_length=8, max_length=200)
    new_organization_name: Optional[str] = Field(default=None, min_length=1, max_length=200)


class OrgDeleteRequest(BaseModel):
    organization_name: str = Field(min_length=1, max_length=200)
