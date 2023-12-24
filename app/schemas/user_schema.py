from pydantic import BaseModel, Field
from fastapi import Query
from typing import Optional, List, Dict
from app.schemas.meta_schema import MetaSchema


class UserInsert(BaseModel):
    user_login: str = Field(Query(..., min_length=2, max_length=10))
    user_pass: str
    first_name: str
    last_name: str
    # meta
    meta: Dict[str, MetaSchema]
    # user_summary: Optional[str] = None
    # user_contacts: Optional[str] = None


class UserSelect(BaseModel):
    id: int
    user_login: str
    first_name: str
    last_name: str
    meta: List[MetaSchema]

    class Config:
        orm_mode = True
