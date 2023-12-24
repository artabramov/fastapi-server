"""User routes."""

from fastapi import APIRouter, Depends
from app.schemas.user_schemas import UserInsert, UserSelect
from sqlalchemy.orm import Session
from app.db import get_db
from app.helpers.repository_provider import RepositoryProvider

router = APIRouter()


@router.post('/user', response_model=UserSelect)
async def user_insert(db: Session = Depends(get_db), schema: UserInsert = Depends()):
    """Insert a new user."""
    repository_provider = RepositoryProvider(db)
    user_repository = repository_provider.get(schema)
    return user_repository.insert(db, schema)


@router.get('/user', tags=['users'])
async def user_select():
    """Select a user."""
    return {'full_name': 'John Doe'}
