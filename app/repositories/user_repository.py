from app.models.user import User
from app.models.user_meta import UserMeta
from app.schemas.user_schema import UserInsert #, UserSelect
from app.managers.entity_manager import EntityManager
from app.errors.value_exists import ValueExists
from app.helpers.mfa_helper import MFAHelper
from app.helpers.jwt_helper import JWTHelper
from app.dotenv import get_config

config = get_config()
jwt_helper = JWTHelper(config.JWT_SECRET, config.JWT_ALGORITHM)


class UserRepository():

    def __init__(self, entity_manager: EntityManager, cache_manager) -> None:
        """Init User Repository."""
        self.entity_manager = entity_manager
        self.cache_manager = cache_manager

    async def register(self, user_schema: UserInsert):
        """Register a new user."""
        if await self.entity_manager.exists(User, user_login__eq=user_schema.user_login):
            raise ValueExists(loc=("query", "user_login"), input=user_schema.user_login)

        try:
            jti = await jwt_helper.generate_jti()
            mfa_key = await MFAHelper.generate_mfa_key()
            await MFAHelper.create_mfa_image(user_schema.user_login, mfa_key)

            user = User(user_schema.user_login, user_schema.first_name, user_schema.last_name)
            await user.setattr("jti", jti)
            await user.setattr("user_pass", user_schema.user_pass)
            await user.setattr("mfa_key", mfa_key)
            await self.entity_manager.insert(user)

            for meta_key in User._meta_keys:
                if hasattr(user_schema, meta_key):
                    meta_value = getattr(user_schema, meta_key)
                    user_meta = UserMeta(user.id, meta_key, meta_value)
                    await self.entity_manager.insert(user_meta)

            await self.entity_manager.commit()
            await self.cache_manager.set(user)

        except Exception as e:
            await MFAHelper.delete_mfa_image(mfa_key)
            await self.entity_manager.rollback()
            raise e

        return user

    async def select(self, user_id: int):
        user = await self.cache_manager.get(User, user_id)
        if not user:
            user = await self.entity_manager.select(User, user_id)
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
