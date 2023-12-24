from fastapi import APIRouter, Depends
from app.models.user import User
from app.schemas.user import UserInsert, UserSelect
from app.repositories.user_repository import create_user
from sqlalchemy.orm import Session
from app.db import get_db

router = APIRouter()


@router.post('/user', response_model=UserSelect)
async def user_insert(user: UserInsert = Depends(), db: Session = Depends(get_db)):
    return create_user(db=db, user=user)


@router.get('/user', tags=['users'])
async def user_select():
    return {'full_name': 'John Doe'}
