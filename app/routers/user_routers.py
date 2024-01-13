"""User routes."""

from fastapi import APIRouter, Depends
from app.schemas.user_schemas import UserRegister, UserLogin, TokenSelect, UserUpdate, UsersList, RoleUpdate, UserSelectRequest, UserSelectResponse
from sqlalchemy.orm import Session
from app.session import get_session
from app.cache import get_cache
from app.helpers.repository_helper import RepositoryHelper
from redis import Redis
from app.dotenv import get_config
from app.helpers.mfa_helper import MFA_IMAGE_RELATIVE_URL, MFA_IMAGE_EXTENSION
from app.auth import auth_admin, auth_editor, auth_writer, auth_reader
from app.models.user_models import User
from fastapi.exceptions import RequestValidationError
from app.errors import E

config = get_config()
router = APIRouter()


@router.get('/auth/login', tags=['auth'])
async def user_login(session: Session = Depends(get_session), cache: Redis = Depends(get_cache),
                     schema: UserLogin = Depends()):
    """Login."""
    repository_helper = RepositoryHelper(session, cache)
    user_repository = await repository_helper.get_repository(User.__tablename__)
    user = await user_repository.login(schema.user_login, schema.user_pass)
    return {}


@router.get('/auth/token', tags=['auth'])
async def token_select(session: Session = Depends(get_session), cache: Redis = Depends(get_cache),
                       schema: TokenSelect = Depends()):
    """Get JWT token."""
    repository_helper = RepositoryHelper(session, cache)
    user_repository = await repository_helper.get_repository(User.__tablename__)
    user_token = await user_repository.token_select(schema.user_login, schema.user_totp, schema.exp)
    return {
        "user_token": user_token,
    }


@router.delete('/auth/token', tags=['auth'])
async def token_delete(session: Session = Depends(get_session), cache: Redis = Depends(get_cache),
                       current_user=Depends(auth_reader)):
    """Delete JWT token."""
    repository_helper = RepositoryHelper(session, cache)
    user_repository = await repository_helper.get_repository(User.__tablename__)
    await user_repository.token_delete(current_user)
    return {}


@router.post('/user', tags=['users'])
async def user_register(session: Session = Depends(get_session), cache: Redis = Depends(get_cache),
                        schema: UserRegister = Depends()):
    """Register a new user."""
    repository_helper = RepositoryHelper(session, cache)
    user_repository = await repository_helper.get_repository(User.__tablename__)
    user = await user_repository.register(schema.user_login, schema.user_pass, schema.first_name, schema.last_name)
    return {
        "user_id": user.id,
        "mfa_key": await user.getattr("mfa_key"),
        'mfa_image': config.BASE_URL + MFA_IMAGE_RELATIVE_URL + await user.getattr("mfa_key") + "." + MFA_IMAGE_EXTENSION,
    }


@router.get('/user/{id}', tags=['users'], response_model=UserSelectResponse)
async def user_select(session: Session = Depends(get_session), cache: Redis = Depends(get_cache),
                      schema: UserSelectRequest = Depends(), current_user=Depends(auth_reader)):
    """Select a user."""
    repository_helper = RepositoryHelper(session, cache)
    user_repository = await repository_helper.get_repository(User.__tablename__)
    user = await user_repository.select(schema.id)
    return user


@router.put('/user', tags=['users'])
async def user_update(session: Session = Depends(get_session), cache: Redis = Depends(get_cache),
                      schema: UserUpdate = Depends(), current_user=Depends(auth_reader)):
    """Update current user."""
    repository_helper = RepositoryHelper(session, cache)
    user_repository = await repository_helper.get_repository(User.__tablename__)
    await user_repository.update(current_user, schema.first_name, schema.last_name, user_summary=schema.user_summary,
                                 user_contacts=schema.user_contacts)
    return {}


@router.delete('/user/{user_id}', tags=['users'])
async def user_delete(user_id: int, session: Session = Depends(get_session), cache: Redis = Depends(get_cache),
                      current_user=Depends(auth_admin)):
    """Delete user."""
    if current_user.id == user_id:
        raise RequestValidationError({"loc": ["path", "user_id"], "input": user_id,
                                     "type": "value_locked", "msg": E.value_locked})

    repository_helper = RepositoryHelper(session, cache)
    user_repository = await repository_helper.get_repository(User.__tablename__)
    user = await user_repository.select(user_id)
    await user_repository.delete(user)
    return {}


@router.put('/user/{user_id}/role', tags=['users'])
async def role_update(user_id: int, session: Session = Depends(get_session), cache: Redis = Depends(get_cache),
                      current_user=Depends(auth_admin), schema: RoleUpdate = Depends()):
    """Update user role."""
    if current_user.id == user_id:
        raise RequestValidationError({"loc": ["path", "user_id"], "input": user_id,
                                     "type": "value_locked", "msg": E.value_locked})

    repository_helper = RepositoryHelper(session, cache)
    user_repository = await repository_helper.get_repository(User.__tablename__)
    user = await user_repository.select(user_id)
    await user_repository.role_update(user, schema.user_role)
    return {}


@router.get('/users', tags=['users'])
async def users_list(session: Session = Depends(get_session), cache: Redis = Depends(get_cache),
                     schema: UsersList = Depends(), current_user=Depends(auth_reader)):
    """Get users list."""
    repository_helper = RepositoryHelper(session, cache)
    user_repository = await repository_helper.get_repository(User.__tablename__)
    users = await user_repository.select_all(schema)
    count = await user_repository.count_all(schema)
    return {
        "users": [await user.to_dict() for user in users],
        "count": count,
    }
