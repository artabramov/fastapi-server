from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user_schemas import UserInsert


class UserRepository():

    def __init__(self, entity_manager: object) -> None:
        self.entity_manager = entity_manager

    def insert(self, db: Session, schema: UserInsert):
        user = User(user_login=schema.user_login, user_pass=schema.user_pass, first_name=schema.first_name,
                    last_name=schema.last_name)
        self.entity_manager.insert(user, commit=True)
        # db.add(user)
        # db.commit()
        # db.refresh(user)
        return user
