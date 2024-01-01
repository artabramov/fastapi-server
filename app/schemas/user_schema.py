from pydantic import BaseModel, Field
from fastapi import Query
from typing import Optional, List, Dict
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


class UsersList(UserSelect):
    users: List[UserSelect] = []
