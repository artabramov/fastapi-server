from pydantic import BaseModel, Field
from fastapi import Query
from typing import Optional, List, Dict, Literal
from app.models.user_models import UserRole


class UserRegister(BaseModel):
    user_login: str = Field(Query(..., min_length=2, max_length=10))
    user_pass: str
    first_name: str = Field(Query(..., min_length=2, max_length=40))
    last_name: str


class UserLogin(BaseModel):
    user_login: str
    user_pass: str


class UserToken(BaseModel):
    user_login: str
    user_totp: str
    exp: Optional[int] = None


class UserUpdate(BaseModel):
    first_name: str = Field(Query(..., min_length=2, max_length=40))
    last_name: str = Field(Query(..., min_length=2, max_length=40))
    # meta
    user_summary: Optional[str] = None
    user_contacts: Optional[str] = None


class UsersList(BaseModel):
    user_role__eq: Optional[str] = None
    user_login__eq: Optional[str] = None
    full_name__ilike: Optional[str] = None
    user_contacts__ilike: Optional[str] = None
    offset: int = 0
    limit: int = Field(1, ge=1, le=168)
    order_by: Literal["id", "created_date", "updated_date", "user_login", "first_name", "last_name"] = "id"
    order: Literal["asc", "desc"] = "desc"
