from sqlalchemy.orm import Session
from app.models.user import User
from app.models.user_meta import UserMeta
from app.schemas.user_schema import UserInsert, UserSelect
# from app.models.user_meta import USER_META_KEYS
from app.schemas.meta_schema import MetaSchema


class UserRepository():

    def __init__(self, entity_manager: object) -> None:
        self.entity_manager = entity_manager

    def insert(self, schema: UserInsert):
        user = User(user_login=schema.user_login, user_pass=schema.user_pass, first_name=schema.first_name,
                    last_name=schema.last_name)
        self.entity_manager.insert(user, commit=True)

        for _, meta_schema in schema.meta.items():
            MetaSchema.model_validate(meta_schema)
            user_meta = UserMeta(user.id, meta_schema.meta_key, meta_schema.meta_value)
            self.entity_manager.insert(user_meta, commit=True)

        # for meta_key in USER_META_KEYS:
        #     meta_value = schema.__getattribute__(meta_key)
        #     if meta_value:
        #         MetaSchema.model_validate(MetaSchema(meta_key=meta_key, meta_value=meta_value))
        #         user_meta = UserMeta(user.id, meta_key, schema.__getattribute__(meta_key))
        #         self.entity_manager.insert(user_meta, commit=True)
        return user

    def select(self, id: int):
        user = self.entity_manager.select(User, id=id)
        return user
