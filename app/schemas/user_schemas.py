"""Pydantic schemas for user model."""

from pydantic import BaseModel, Field, SecretStr
from fastapi import Query, File, UploadFile
from typing import Optional, List, Literal
from app.models.user_models import UserRole


class UserRegisterRequest(BaseModel):
    """Pydantic schema for user registration request."""

    user_login: str = Field(Query(..., min_length=2, max_length=40))
    user_pass: SecretStr = Field(Query(..., min_length=6))
    first_name: str = Field(Query(..., min_length=2, max_length=40))
    last_name: str = Field(Query(..., min_length=2, max_length=40))


class UserRegisterResponse(BaseModel):
    """Pydantic schema for user registration response."""

    user_id: int
    mfa_key: str
    mfa_image: str


class UserLoginRequest(BaseModel):
    """Pydantic schema for user login request."""

    user_login: str
    user_pass: SecretStr


class UserLoginResponse(BaseModel):
    """Pydantic schema for user login response."""

    pass_accepted: bool


class TokenSelectRequest(BaseModel):
    """Pydantic schema for token selection request."""

    user_login: str
    user_totp: str = Field(Query(..., min_length=6, max_length=6))
    exp: Optional[int] = None


class TokenSelectResponse(BaseModel):
    """Pydantic schema for token selection response."""

    user_token: str


class TokenDeleteResponse(BaseModel):
    """Pydantic schema for token deletion response."""

    pass


class UserSelectRequest(BaseModel):
    """Pydantic schema for user selection request."""

    id: int


class UserSelectResponse(BaseModel):
    """Pydantic schema for user selection response."""

    id: int
    created_date: int
    updated_date: int
    user_role: UserRole
    user_login: str
    first_name: str
    last_name: str
    meta: dict


class UserUpdateRequest(BaseModel):
    """Pydantic schema for user updation request."""

    first_name: str = Field(Query(..., min_length=2, max_length=40))
    last_name: str = Field(Query(..., min_length=2, max_length=40))
    # user meta
    user_summary: Optional[str] = Field(Query(..., max_length=512))
    user_contacts: Optional[str] = Field(Query(..., max_length=512))


class UserUpdateResponse(BaseModel):
    """Pydantic schema for user updation response."""

    pass


class UserDeleteRequest(BaseModel):
    """Pydantic schema for user deletion request."""

    id: int


class UserDeleteResponse(BaseModel):
    """Pydantic schema for user deletion response."""

    pass


class RoleUpdateRequest(BaseModel):
    """Pydantic schema for role updation request."""

    id: int
    user_role: UserRole


class RoleUpdateResponse(BaseModel):
    """Pydantic schema for role updation response."""

    pass


class UsersListRequest(BaseModel):
    """Pydantic schema for users list request."""

    user_role__eq: Optional[UserRole] = None
    user_login__eq: Optional[str] = None
    full_name__ilike: Optional[str] = None
    offset: int = 0
    limit: int = Field(1, ge=1, le=200)
    order_by: Literal["id", "created_date", "updated_date", "user_login", "first_name", "last_name"] = "id"
    order: Literal["asc", "desc"] = "desc"


class UsersListResponse(BaseModel):
    """Pydantic schema for users list requst."""

    users: List[UserSelectResponse]
    users_count: int


class UserpicUploadRequest(BaseModel):
    """Pydantic schema for userpic uploading request."""

    file: UploadFile = File(...)


class UserpicUploadResponse(BaseModel):
    """Pydantic schema for userpic uploading response."""

    pass


class UserpicDeleteRequest(BaseModel):
    """Pydantic schema for userpic deleting request."""

    pass


class UserpicDeleteResponse(BaseModel):
    """Pydantic schema for userpic deleting response."""

    pass
