from app.models.user import User
from app.models.user_meta import UserMeta
from app.schemas.user_schema import UserInsert #, UserSelect
from app.managers.entity_manager import EntityManager
from app.errors.value_exists import ValueExists


class UserRepository():

    def __init__(self, entity_manager: EntityManager, cache_manager) -> None:
        self.entity_manager = entity_manager
        self.cache_manager = cache_manager

    async def insert(self, schema: UserInsert):
        if await self.entity_manager.exists(User, user_login__eq=schema.user_login):
            raise ValueExists(loc=("query", "user_login"), input=schema.user_login)

        try:
            user = User(user_login=schema.user_login, user_pass=schema.user_pass, first_name=schema.first_name,
                        last_name=schema.last_name)
            await self.entity_manager.insert(user, commit=True)

            for meta_key in User._meta_keys:
                meta_value = getattr(schema, meta_key)
                if meta_value:
                    user_meta = UserMeta(user.id, meta_key, meta_value)
                    await self.entity_manager.insert(user_meta)

            await self.entity_manager.commit()
            self.cache_manager.set(user)

        except Exception as e:
            await self.entity_manager.rollback()
            raise e

        return user

    async def select(self, id: int):
        # user = await self.cache_manager.get(User, id)
        user = None
        if not user:
            user = await self.entity_manager.select(User, id)
        return user

    async def select_all(self, schema):
        kwargs = {key[0]: key[1] for key in schema if key[1]}

        if "user_contacts__ilike" in kwargs:
            kwargs["id__in"] = await self.entity_manager.subquery(UserMeta, "user_id", meta_key__eq="user_contacts",
                                                                  meta_value__ilike=kwargs["user_contacts__ilike"])

        users = await self.entity_manager.select_all(User, **kwargs)
        return users

    async def count_all(self, schema):
        kwargs = {key[0]: key[1] for key in schema if key[1]}
        users_count = await self.entity_manager.count_all(User, **kwargs)
        return users_count
