from typing import Annotated
from fastapi import Depends
from fastapi.security import HTTPBearer
from app.error import E
from app.helpers.jwt_helper import JWTHelper
from jwt.exceptions import ExpiredSignatureError, PyJWTError
from app.dotenv import get_config
from app.session import get_session
from app.managers.entity_manager import EntityManager
from app.models.user_models import User

BEARER_ERROR_LOC = ("header", "Authorization")

config = get_config()
jwt_helper = JWTHelper(config.JWT_SECRET, config.JWT_ALGORITHM)
jwt_schema = HTTPBearer()


async def get_current_user(bearer: Annotated[str, Depends(jwt_schema)]):
    if not bearer.credentials:
        raise E(BEARER_ERROR_LOC, "token_empty")
    
    try:
        token_payload = await jwt_helper.decode_token(bearer.credentials)

    except ExpiredSignatureError:
        raise E(BEARER_ERROR_LOC, "token_expired")

    except PyJWTError:
        raise E(BEARER_ERROR_LOC, "token_invalid")

    session = next(get_session())
    entity_manager = EntityManager(session)

    user = await entity_manager.select_by(User, id__eq=token_payload["user_id"])
    if not user:
        raise E(BEARER_ERROR_LOC, "token_rejected")

    jti = await user.getattr("jti")
    if token_payload["jti"] != jti:
        raise E(BEARER_ERROR_LOC, "token_rejected")

    return user


def check_permissions(user, user_role):
    pass
