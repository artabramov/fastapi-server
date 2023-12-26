"""User routes."""

from fastapi import APIRouter, Depends
from app.schemas.user_schema import UserInsert, UserSelect
from sqlalchemy.orm import Session
from app.db import get_db
from app.helpers.repository_provider import RepositoryProvider

router = APIRouter()


@router.post('/user', response_model=UserSelect, tags=['users'])
async def user_insert(db: Session = Depends(get_db), user_schema: UserInsert = Depends()):
    """Insert a user."""
    repository_provider = RepositoryProvider(db)
    user_repository = repository_provider.get(UserInsert)
    user = user_repository.insert(user_schema)
    return user


@router.get('/user/{id}', response_model=UserSelect, tags=['users'])
async def user_select(id: int, db: Session = Depends(get_db)):
    """Select a user."""
    repository_provider = RepositoryProvider(db)
    user_repository = repository_provider.get(UserSelect)
    user = user_repository.select(id)
    return user