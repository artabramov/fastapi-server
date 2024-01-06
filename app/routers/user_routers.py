"""User routes."""

from fastapi import APIRouter, Depends
from app.schemas.user_schema import UserInsert, UserSelect, UserSearch, UserList, UserId
from sqlalchemy.orm import Session
from app.session import get_session
from app.cache import get_cache
from app.helpers.repository_helper import RepositoryHelper
from redis import Redis

router = APIRouter()


@router.post('/user', response_model=UserSelect, tags=['users'])
async def user_register(session: Session = Depends(get_session), cache: Redis = Depends(get_cache),
                        user_schema: UserInsert = Depends()):
    """Register a new user."""
    repository_helper = RepositoryHelper(session, cache)
    user_repository = await repository_helper.get_repository(user_schema)
    user = await user_repository.register(user_schema)
    return user


@router.get('/user/{id}', response_model=UserSelect, tags=['users'])
async def user_select(session: Session = Depends(get_session), cache: Redis = Depends(get_cache),
                      user_schema: UserId = Depends()):
    """Select a user."""
    repository_helper = RepositoryHelper(session, cache)
    user_repository = await repository_helper.get_repository(user_schema)
    user = await user_repository.select(user_schema.id)
    return user


@router.get('/users', response_model=UserList, tags=['users'])
async def users_list(session: Session = Depends(get_session), cache: Redis = Depends(get_cache),
                     user_schema: UserSearch = Depends()):
    """Select a user."""
    repository_helper = RepositoryHelper(session, cache)
    user_repository = await repository_helper.get_repository(user_schema)
    users = await user_repository.select_all(user_schema)
    count = await user_repository.count_all(user_schema)
    return {"users": users, "count": count}
