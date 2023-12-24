from pydantic import BaseModel, Field
from fastapi import Query


class UserInsert(BaseModel):
    user_login: str = Field(Query(..., description='Latin characters and numbers from 2 to 40 symbols long.'))
    user_pass: str
    first_name: str
    last_name: str


class UserSelect(BaseModel):
    id: int
    user_login: str
    first_name: str
    last_name: str

    class Config:
        orm_mode = True
