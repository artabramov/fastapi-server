"""Pydantic schemas for collection model."""

from pydantic import BaseModel, Field
from fastapi import Query


class CollectionInsertRequest(BaseModel):
    """Pydantic schema for collection insertion request."""

    collection_name: str = Field(Query(..., min_length=1, max_length=128))
    collection_summary: str = Field(Query(..., min_length=1, max_length=512))


class CollectionInsertResponse(BaseModel):
    """Pydantic schema for collection insertion response."""

    collection_id: int
