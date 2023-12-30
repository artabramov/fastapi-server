"""User routes."""

from fastapi import APIRouter, Depends
from app.schemas.user_schema import UserInsert, UserSelect
from sqlalchemy.orm import Session
from app.db import get_db
from app.cache import get_cache
from app.helpers.repository_provider import RepositoryProvider
from redis import Redis

router = APIRouter()


@router.post('/user', response_model=UserSelect, tags=['users'])
async def user_insert(db: Session = Depends(get_db), cache: Redis = Depends(get_cache),
                      user_schema: UserInsert = Depends()):
    """Insert a user."""
    repository_provider = RepositoryProvider(db, cache)
    user_repository = await repository_provider.get(UserInsert)
    user = await user_repository.insert(user_schema)
    return user


@router.get('/user/{id}', response_model=UserSelect, tags=['users'])
async def user_select(id: int, db: Session = Depends(get_db), cache: Redis = Depends(get_cache)):
    """Select a user."""
    repository_provider = RepositoryProvider(db, cache)
    user_repository = await repository_provider.get(UserSelect)
    user = await user_repository.select(id)
    return user
