from pydantic import BaseModel, Field
from fastapi import Query


class MetaSchema(BaseModel):
    meta_key: str
    meta_value: str = Field(Query(..., max_length=10))
