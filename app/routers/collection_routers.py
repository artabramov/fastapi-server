"""Collection routes."""

from fastapi import APIRouter, Depends
from app.schemas.collection_schemas import CollectionInsertRequest, CollectionInsertResponse
from sqlalchemy.orm import Session
from app.session import get_session
from app.cache import get_cache
from app.helpers.repository_helper import RepositoryHelper
from redis import Redis
from app.auth import auth_admin
from app.models.collection_models import Collection

router = APIRouter()


@router.post('/collection', tags=['collections'], response_model=CollectionInsertResponse)
async def collection_insert(session: Session = Depends(get_session), cache: Redis = Depends(get_cache),
                            schema: CollectionInsertRequest = Depends(), current_user=Depends(auth_admin)):
    """Insert a new collection."""
    repository_helper = RepositoryHelper(session, cache)
    collection_repository = await repository_helper.get_repository(Collection.__tablename__)
    collection = await collection_repository.insert(current_user.id, schema.collection_name, schema.collection_summary)
    return {
        "collection_id": collection.id,
    }
