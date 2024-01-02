from pydantic import BaseModel, Field
from fastapi import Query
from typing import Optional, List, Dict, Literal
from app.models.user import UserRole


class UserInsert(BaseModel):
    user_login: str = Field(Query(..., min_length=2, max_length=10))
    user_pass: str
    first_name: str = Field(Query(..., min_length=2, max_length=40))
    last_name: str
    # meta
    user_summary: Optional[str] = None
    user_contacts: Optional[str] = None


class UserSelect(BaseModel):
    id: int
    user_role: UserRole
    user_login: str
    first_name: str
    last_name: str
    # meta
    user_summary: Optional[str] = None
    user_contacts: Optional[str] = None

    class Config:
        from_attributes = True
        json_encoders = {UserRole: lambda x: x.name}


class UserSearch(BaseModel):
    user_role__eq: Optional[str] = None
    user_login__eq: Optional[str] = None
    full_name__ilike: Optional[str] = None
    user_contacts__ilike: Optional[str] = None
    offset: int = 0
    limit: int = Field(1, ge=1, le=168)
    order_by: Literal["id", "created_date", "updated_date", "user_login", "first_name", "last_name"] = "id"
    order: Literal["asc", "desc"] = "desc"


class UserList(BaseModel):
    users: List[UserSelect] = []
    count: int
