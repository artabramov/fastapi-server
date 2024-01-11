from app.models.user_models import User, UserMeta, UserRole, USER_PASS_ATTEMPTS_LIMIT, USER_PASS_SUSPENDED_TIME, USER_MFA_ATTEMPTS_LIMIT
from app.schemas.user_schemas import UserRegister, UserLogin, UserSignin, UserSelect, UsersList
from app.managers.entity_manager import EntityManager
from app.error import E
from app.helpers.mfa_helper import MFAHelper
from app.helpers.jwt_helper import JWTHelper
from app.dotenv import get_config
from fastapi import HTTPException
from app.helpers.meta_helper import MetaHelper
from app.helpers.hash_helper import HashHelper
import time

config = get_config()
jwt_helper = JWTHelper(config.JWT_SECRET, config.JWT_ALGORITHM)
hash_helper = HashHelper(config.HASH_SALT)


class UserRepository():

    def __init__(self, entity_manager: EntityManager, cache_manager) -> None:
        """Init User Repository."""
        self.entity_manager = entity_manager
        self.cache_manager = cache_manager

    async def register(self, user_schema: UserRegister):
        """Register a new user."""
        if await self.entity_manager.exists(User, user_login__eq=user_schema.user_login):
            raise E(("query", "user_login"), "value_exists")

        try:
            jti = await jwt_helper.generate_jti()
            mfa_key = await MFAHelper.generate_mfa_key()
            await MFAHelper.create_mfa_image(user_schema.user_login, mfa_key)

            pass_hash = await hash_helper.hash(user_schema.user_pass)
            user = User(user_schema.user_login, pass_hash, user_schema.first_name, user_schema.last_name)

            await user.setattr("jti", jti)
            await user.setattr("mfa_key", mfa_key)
            await self.entity_manager.insert(user)

            await MetaHelper.set(self.entity_manager, User, user.id, user_schema, UserMeta)

            await self.entity_manager.commit()
            await self.cache_manager.set(user)

        except Exception as e:
            await MFAHelper.delete_mfa_image(mfa_key)
            await self.entity_manager.rollback()
            raise e

        return user

    async def login(self, schema: UserLogin):
        """Login, first step."""
        users = await self.entity_manager.select_all(User, user_login__eq=schema.user_login)
        user = users[0] if users else None

        if not user:
            raise E(("query", "user_login"), "value_not_found")

        elif user.user_role.name == UserRole.none.name:
            raise E(("query", "user_login"), "access_denied")

        elif user.suspended_date >= time.time():
            raise E(("query", "user_pass"), "attempts_suspended")

        elif user.pass_hash == await hash_helper.hash(schema.user_pass):
            user.suspended_date = 0
            user.pass_attempts = 0
            user.pass_accepted = True
            await self.entity_manager.update(user, commit=True)

        else:
            user.suspended_date = 0
            user.pass_attempts = user.pass_attempts + 1
            user.pass_accepted = False
            if user.pass_attempts >= USER_PASS_ATTEMPTS_LIMIT:
                user.suspended_date = int(time.time()) + USER_PASS_SUSPENDED_TIME
                user.pass_attempts = 0

            await self.entity_manager.update(user, commit=True)
            raise E(("query", "user_pass"), "value_invalid")

    async def signin(self, schema: UserSignin) -> str:
        """Login, second step."""
        users = await self.entity_manager.select_all(User, user_login__eq=schema.user_login)
        user = users[0] if users else None

        if not user:
            raise E(("query", "user_login"), "value_not_found")

        elif not user.pass_accepted:
            raise E(("query", "user_totp"), "access_denied")

        mfa_key = await user.getattr("mfa_key")
        if schema.user_totp == await MFAHelper.get_mfa_totp(mfa_key):
            await MFAHelper.delete_mfa_image(mfa_key)
            user.mfa_attempts = 0
            user.pass_accepted = False
            await self.entity_manager.update(user, commit=True)
            
            jti = await user.getattr("jti")
            user_token = await jwt_helper.encode_token(user.id, user.user_role.name, user.user_login, jti, schema.exp)
            return user_token

        else:
            user.mfa_attempts = user.mfa_attempts + 1
            if user.mfa_attempts >= USER_MFA_ATTEMPTS_LIMIT:
                user.mfa_attempts = 0
                user.pass_accepted = False

            await self.entity_manager.update(user, commit=True)
            raise E(("query", "user_totp"), "value_invalid")


    async def select(self, user_schema: UserSelect):
        """Select user."""
        user = await self.cache_manager.get(User, user_schema.id)
        if not user:
            user = await self.entity_manager.select(User, user_schema.id)

        if not user:
            raise HTTPException(status_code=404)

        return user

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
