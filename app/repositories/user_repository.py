from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserInsert


def create_user(db: Session, user: UserInsert):
    db_user = User(user_login=user.user_login, user_pass=user.user_pass, first_name=user.first_name, last_name=user.last_name)
    db.add(db_user)
    try:
        db.commit()
    except Exception as e:
        pass
    db.refresh(db_user)
    return db_user
