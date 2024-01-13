from typing import Annotated
from fastapi import Depends
from fastapi.security import HTTPBearer
from app.errors import E
from app.helpers.jwt_helper import JWTHelper
from jwt.exceptions import ExpiredSignatureError, PyJWTError
from app.dotenv import get_config
from app.session import get_session
from app.cache import get_cache
from app.managers.entity_manager import EntityManager
from app.managers.cache_manager import CacheManager
from app.models.user_models import User
from fastapi import HTTPException

JWT_ERROR_LOC = ("header", "Authorization")

config = get_config()
jwt_helper = JWTHelper(config.JWT_SECRET, config.JWT_ALGORITHM)
jwt_schema = HTTPBearer()


async def _auth_user(user_token):
    if not user_token.credentials:
        raise HTTPException(status_code=403, detail=E.jwt_empty)
    
    try:
        jwt_payload = await jwt_helper.decode_token(user_token.credentials)

    except ExpiredSignatureError:
        raise HTTPException(status_code=403, detail=E.jwt_expired)

    except PyJWTError:
        raise HTTPException(status_code=403, detail=E.jwt_invalid)

    cache = next(get_cache())
    cache_manager = CacheManager(cache)
    user = await cache_manager.get(User, jwt_payload["user_id"])

    if not user:
        session = next(get_session())
        entity_manager = EntityManager(session)
        user = await entity_manager.select_by(User, id__eq=jwt_payload["user_id"])

    if not user:
        raise HTTPException(status_code=403, detail=E.jwt_rejected)

    await cache_manager.set(user)
    jti = await user.decrypt_attr("jti")

    if jwt_payload["jti"] != jti:
        raise HTTPException(status_code=403, detail=E.jwt_rejected)

    return user


async def auth_admin(user_token: Annotated[str, Depends(jwt_schema)]):
    user = await _auth_user(user_token)
    if not user.can_admin:
        raise HTTPException(status_code=403, detail=E.jwt_denied)

    return user


async def auth_editor(user_token: Annotated[str, Depends(jwt_schema)]):
    user = await _auth_user(user_token)
    if not user.can_edit:
        raise HTTPException(status_code=403, detail=E.jwt_denied)

    return user


async def auth_writer(user_token: Annotated[str, Depends(jwt_schema)]):
    user = await _auth_user(user_token)
    if not user.can_write:
        raise HTTPException(status_code=403, detail=E.jwt_denied)

    return user


async def auth_reader(user_token: Annotated[str, Depends(jwt_schema)]):
    user = await _auth_user(user_token)
    if not user.can_read:
        raise HTTPException(status_code=403, detail=E.jwt_denied)

    return user
