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
        if await self.entity_manager.exists(User, user_login=schema.user_login):
            raise ValueExists(loc=("query", "user_login"), input=schema.user_login)

        try:
            user = User(user_login=schema.user_login, user_pass=schema.user_pass, first_name=schema.first_name,
                        last_name=schema.last_name)
            await self.entity_manager.insert(user)

            for meta_key in User._meta_keys:
                meta_value = getattr(schema, meta_key)
                if meta_value:
                    user_meta = UserMeta(user.id, meta_key, meta_value)
                    self.entity_manager.insert(user_meta)

            self.entity_manager.commit()
            self.cache_manager.set(user)

        except Exception as e:
            self.entity_manager.rollback()
            raise e

        return user

    async def select(self, id: int):
        user = await self.cache_manager.get(User, id)
        if not user:
            user = await self.entity_manager.select(User, id=id)
        return user
