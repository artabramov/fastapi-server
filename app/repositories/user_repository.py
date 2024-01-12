from app.models.user_models import User, UserMeta, UserRole, USER_PASS_ATTEMPTS_LIMIT, USER_PASS_SUSPENDED_TIME, USER_MFA_ATTEMPTS_LIMIT
from app.managers.entity_manager import EntityManager
from app.errors import E
from app.helpers.mfa_helper import MFAHelper
from app.helpers.jwt_helper import JWTHelper
from app.dotenv import get_config
from fastapi import HTTPException
from app.helpers.hash_helper import HashHelper
from fastapi.exceptions import RequestValidationError
from app.repositories.meta_repository import MetaRepository
import time

config = get_config()
jwt_helper = JWTHelper(config.JWT_SECRET, config.JWT_ALGORITHM)
hash_helper = HashHelper(config.HASH_SALT)


class UserRepository:

    def __init__(self, entity_manager: EntityManager, cache_manager) -> None:
        """Init User Repository."""
        self.entity_manager = entity_manager
        self.cache_manager = cache_manager

    async def register(self, user_login: str, user_pass: str, first_name: str, last_name: str) -> User:
        """Register a new user."""
        if await self.entity_manager.exists(User, user_login__eq=user_login):
            raise RequestValidationError({"loc": ["query", "user_login"], "input": user_login,
                                          "type": "value_exists", "msg": E.value_exists})

        try:
            jti = await jwt_helper.generate_jti()
            mfa_key = await MFAHelper.generate_mfa_key()
            await MFAHelper.create_mfa_image(user_login, mfa_key)

            pass_hash = await hash_helper.hash(user_pass)
            user = User(user_login, pass_hash, first_name, last_name)

            await user.setattr("jti", jti)
            await user.setattr("mfa_key", mfa_key)
            await self.entity_manager.insert(user, commit=True)

        except Exception as e:
            await MFAHelper.delete_mfa_image(mfa_key)
            await self.entity_manager.rollback()
            raise e

        return user

    async def login(self, user_login: str, user_pass: str):
        """Login, first step."""
        user = await self.entity_manager.select_by(User, user_login__eq=user_login)

        if not user:
            raise RequestValidationError({"loc": ["query", "user_login"], "input": user_login,
                                          "type": "value_invalid", "msg": E.value_invalid})

        elif user.user_role.name == UserRole.none.name:
            raise RequestValidationError({"loc": ["query", "user_login"], "input": user_login,
                                          "type": "login_denied", "msg": E.login_denied})

        elif user.suspended_date >= time.time():
            raise RequestValidationError({"loc": ["query", "user_login"], "input": user_login,
                                          "type": "login_suspended", "msg": E.login_suspended})

        elif user.pass_hash == await hash_helper.hash(user_pass):
            user.suspended_date = 0
            user.pass_attempts = 0
            user.pass_accepted = True
            await self.entity_manager.update(user, commit=True)
            await self.cache_manager.delete(user)

        else:
            user.suspended_date = 0
            user.pass_attempts = user.pass_attempts + 1
            user.pass_accepted = False
            if user.pass_attempts >= USER_PASS_ATTEMPTS_LIMIT:
                user.suspended_date = int(time.time()) + USER_PASS_SUSPENDED_TIME
                user.pass_attempts = 0

            await self.entity_manager.update(user, commit=True)
            await self.cache_manager.delete(user)

            raise RequestValidationError({"loc": ["query", "user_pass"], "input": user_pass,
                                          "type": "value_invalid", "msg": E.value_invalid})

    async def token_select(self, user_login: str, user_totp: str, exp: int = None) -> str:
        """Login, second step."""
        user = await self.entity_manager.select_by(User, user_login__eq=user_login)

        if not user:
            raise RequestValidationError({"loc": ["query", "user_login"], "input": user_login,
                                          "type": "login_invalid", "msg": E.login_invalid})

        elif not user.pass_accepted:
            raise RequestValidationError({"loc": ["query", "user_login"], "input": user_login,
                                          "type": "login_denied", "msg": E.login_denied})

        mfa_key = await user.getattr("mfa_key")
        if user_totp == await MFAHelper.get_mfa_totp(mfa_key):
            await MFAHelper.delete_mfa_image(mfa_key)
            user.mfa_attempts = 0
            user.pass_accepted = False
            await self.entity_manager.update(user, commit=True)
            await self.cache_manager.delete(user)
            
            jti = await user.getattr("jti")
            user_token = await jwt_helper.encode_token(user.id, user.user_role.name, user.user_login, jti, exp)
            return user_token

        else:
            user.mfa_attempts = user.mfa_attempts + 1
            if user.mfa_attempts >= USER_MFA_ATTEMPTS_LIMIT:
                user.mfa_attempts = 0
                user.pass_accepted = False

            await self.entity_manager.update(user, commit=True)
            await self.cache_manager.delete(user)

            raise RequestValidationError({"loc": ["query", "user_totp"], "input": user_totp,
                                          "type": "value_invalid", "msg": E.value_invalid})
        
    async def token_delete(self, user: User):
        jti = await jwt_helper.generate_jti()
        await user.setattr("jti", jti)
        await self.entity_manager.update(user, commit=True)
        await self.cache_manager.delete(user)

    async def select(self, user_id: int) -> User:
        """Select user."""
        user = await self.cache_manager.get(User, user_id)
        if not user:
            user = await self.entity_manager.select(User, user_id)

        if not user:
            raise HTTPException(status_code=404)

        await self.cache_manager.set(user)
        return user

    async def update(self, user: User, first_name: str, last_name: str, user_summary: str = None, user_contacts: str = None):
        """Update an user."""
        user.first_name = first_name
        user.last_name = last_name
        await self.entity_manager.update(user)

        meta_repository = MetaRepository(self.entity_manager)
        await meta_repository.set(UserMeta, user.id, "user_summary", user_summary)

        await self.entity_manager.commit()
        await self.cache_manager.delete(user)

    async def select_all(self, schema):
        kwargs = {key[0]: key[1] for key in schema if key[1]}

        if "user_contacts__ilike" in kwargs:
            kwargs["id__in"] = await self.entity_manager.subquery(UserMeta, "user_id", meta_key__eq="user_contacts",
                                                                  meta_value__ilike=kwargs["user_contacts__ilike"])

        users = await self.entity_manager.select_all(User, **kwargs)
        for user in users:
            await self.cache_manager.set(user)
        return users

    async def count_all(self, schema):
        kwargs = {key[0]: key[1] for key in schema if key[1]}
        users_count = await self.entity_manager.count_all(User, **kwargs)
        return users_count
