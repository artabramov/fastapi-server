from sqlalchemy.orm import Session
from app.models.user import User
from app.models.user_meta import UserMeta
from app.schemas.user_schema import UserInsert #, UserSelect
from app.managers.entity_manager import EntityManager
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from fastapi import status
from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError
from fastapi.exceptions import RequestValidationError


class UserRepository():

    def __init__(self, entity_manager: EntityManager) -> None:
        self.entity_manager = entity_manager

    def insert(self, schema: UserInsert):
        # try:
        if self.entity_manager.exists(User, user_login=schema.user_login):
            raise RequestValidationError({
                "type": "value_exists",
                "loc": ("query", "user_login"),
                "msg": "The value already exists",
                "input": schema.user_login,
            })
            # raise RequestValidationError(detail="sadf")
            # return JSONResponse(
            #     status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            #     content=jsonable_encoder({"detail": "sd", "Error": "Name field is missing"}),
            # )

            # raise HTTPException(status_code=404, detail="Name field is required")
            # raise ValueError("fuck!")
                # return JSONResponse(
                #     status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                #     content=jsonable_encoder({"detail": "error details", "body": "error body"}),
                # )
        # except ValueError as e:
        #     return JSONResponse(
        #         status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        #         content=jsonable_encoder({"detail": "error details", "body": "error body", "loc": {"ssf": "sdf"}}),
        #     )

        try:
            user = User(user_login=schema.user_login, user_pass=schema.user_pass, first_name=schema.first_name,
                        last_name=schema.last_name)
            self.entity_manager.insert(user)

            for meta_key in User._meta_keys:
                meta_value = getattr(schema, meta_key)
                if meta_value:
                    user_meta = UserMeta(user.id, meta_key, meta_value)
                    self.entity_manager.insert(user_meta)

            self.entity_manager.commit()

        except Exception as e:
            self.entity_manager.rollback()
            raise e

        return user

    def select(self, id: int):
        user = self.entity_manager.select(User, id=id)
        return user
