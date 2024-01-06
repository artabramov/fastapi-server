"""User routes."""

from fastapi import APIRouter, Depends
from app.schemas.user_schema import UserRegister, UserSelect, UsersList
from sqlalchemy.orm import Session
from app.session import get_session
from app.cache import get_cache
from app.helpers.repository_helper import RepositoryHelper
from redis import Redis
from app.dotenv import get_config
from app.helpers.mfa_helper import MFA_IMAGE_RELATIVE_URL, MFA_IMAGE_EXTENSION

config = get_config()

router = APIRouter()


@router.post('/user', tags=['users'])
async def user_register(session: Session = Depends(get_session), cache: Redis = Depends(get_cache),
                        user_schema: UserRegister = Depends()):
    """Register a new user."""
    repository_helper = RepositoryHelper(session, cache)
    user_repository = await repository_helper.get_repository(user_schema)
    user = await user_repository.register(user_schema)
    return {
        "mfa_key": await user.getattr("mfa_key"),
        'mfa_image': config.BASE_URL + MFA_IMAGE_RELATIVE_URL + await user.getattr("mfa_key") + "." + MFA_IMAGE_EXTENSION,
    }


@router.get('/user/{id}', tags=['users'])
async def user_select(session: Session = Depends(get_session), cache: Redis = Depends(get_cache),
                      user_schema: UserSelect = Depends()):
    """Select a user."""
    repository_helper = RepositoryHelper(session, cache)
    user_repository = await repository_helper.get_repository(user_schema)
    user = await user_repository.select(user_schema)
    return {
        "user": await user.to_dict(),
    }


@router.get('/users', tags=['users'])
async def users_list(session: Session = Depends(get_session), cache: Redis = Depends(get_cache),
                     user_schema: UsersList = Depends()):
    """Select a user."""
    repository_helper = RepositoryHelper(session, cache)
    user_repository = await repository_helper.get_repository(user_schema)
    users = await user_repository.select_all(user_schema)
    count = await user_repository.count_all(user_schema)
    return {
        "users": [await user.to_dict() for user in users],
        "count": count,
    }
