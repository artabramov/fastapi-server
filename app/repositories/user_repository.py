"""User repository."""

from app.models.user_models import User, UserMeta, UserRole
from app.models.user_models import USER_PASS_ATTEMPTS_LIMIT, USER_PASS_SUSPENDED_TIME, USER_MFA_ATTEMPTS_LIMIT
from app.managers.entity_manager import EntityManager
from app.errors import E
from app.helpers.mfa_helper import MFAHelper
from app.helpers.jwt_helper import JWTHelper
from app.dotenv import get_config
from fastapi import HTTPException, UploadFile
from app.helpers.hash_helper import HashHelper
from fastapi.exceptions import RequestValidationError
from app.repositories.meta_repository import MetaRepository
from app.managers.file_manager import FileManager
from PIL import Image
import time

config = get_config()
jwt_helper = JWTHelper(config.JWT_SECRET, config.JWT_ALGORITHM)
hash_helper = HashHelper(config.HASH_SALT)


class UserRepository:
    """User repository."""

    def __init__(self, entity_manager: EntityManager, cache_manager) -> None:
        """Init User Repository."""
        self.entity_manager = entity_manager
        self.cache_manager = cache_manager

    async def register(self, user_login: str, user_pass: str, first_name: str, last_name: str) -> User:
        """Register a new user."""
        if await self.entity_manager.exists(User, user_login__eq=user_login):
            raise RequestValidationError({"loc": ["query", "user_login"], "input": user_login,
                                          "type": "value_exists", "msg": E.value_exists})

        try:
            jti = await jwt_helper.generate_jti()
            mfa_key = await MFAHelper.generate_mfa_key()
            await MFAHelper.create_mfa_image(user_login, mfa_key)

            pass_hash = await hash_helper.hash(user_pass)
            user = User(user_login, pass_hash, first_name, last_name)

            # set admin role for first registered user
            users_count = await self.entity_manager.count_all(User)
            if not users_count:
                user.user_role = UserRole.admin

            await user.encrypt_attr("jti", jti)
            await user.encrypt_attr("mfa_key", mfa_key)
            await self.entity_manager.insert(user, commit=True)

        except Exception as e:
            await MFAHelper.delete_mfa_image(mfa_key)
            await self.entity_manager.rollback()
            raise e

        return user

    async def login(self, user_login: str, user_pass: str):
        """User login."""
        user = await self.entity_manager.select_by(User, user_login__eq=user_login)

        if not user:
            raise RequestValidationError({"loc": ["query", "user_login"], "input": user_login,
                                          "type": "value_invalid", "msg": E.value_invalid})

        elif user.user_role.name == UserRole.none.name:
            raise RequestValidationError({"loc": ["query", "user_login"], "input": user_login,
                                          "type": "login_denied", "msg": E.login_denied})

        elif user.suspended_date >= time.time():
            raise RequestValidationError({"loc": ["query", "user_login"], "input": user_login,
                                          "type": "login_suspended", "msg": E.login_suspended})

        elif user.pass_hash == await hash_helper.hash(user_pass):
            user.suspended_date = 0
            user.pass_attempts = 0
            user.pass_accepted = True
            await self.entity_manager.update(user, commit=True)
            await self.cache_manager.delete(user)

        else:
            user.suspended_date = 0
            user.pass_attempts = user.pass_attempts + 1
            user.pass_accepted = False
            if user.pass_attempts >= USER_PASS_ATTEMPTS_LIMIT:
                user.suspended_date = int(time.time()) + USER_PASS_SUSPENDED_TIME
                user.pass_attempts = 0

            await self.entity_manager.update(user, commit=True)
            await self.cache_manager.delete(user)

            raise RequestValidationError({"loc": ["query", "user_pass"], "input": user_pass,
                                          "type": "value_invalid", "msg": E.value_invalid})

    async def token_select(self, user_login: str, user_totp: str, exp: int = None) -> str:
        """Get user token."""
        user = await self.entity_manager.select_by(User, user_login__eq=user_login)

        if not user:
            raise RequestValidationError({"loc": ["query", "user_login"], "input": user_login,
                                          "type": "login_invalid", "msg": E.login_invalid})

        elif not user.pass_accepted:
            raise RequestValidationError({"loc": ["query", "user_login"], "input": user_login,
                                          "type": "login_denied", "msg": E.login_denied})

        mfa_key = await user.decrypt_attr("mfa_key")
        if user_totp == await MFAHelper.get_mfa_totp(mfa_key):
            await MFAHelper.delete_mfa_image(mfa_key)
            user.mfa_attempts = 0
            user.pass_accepted = False
            await self.entity_manager.update(user, commit=True)
            await self.cache_manager.delete(user)

            jti = await user.decrypt_attr("jti")
            user_token = await jwt_helper.encode_token(user.id, user.user_role.name, user.user_login, jti, exp)
            return user_token

        else:
            user.mfa_attempts = user.mfa_attempts + 1
            if user.mfa_attempts >= USER_MFA_ATTEMPTS_LIMIT:
                user.mfa_attempts = 0
                user.pass_accepted = False

            await self.entity_manager.update(user, commit=True)
            await self.cache_manager.delete(user)

            raise RequestValidationError({"loc": ["query", "user_totp"], "input": user_totp,
                                          "type": "value_invalid", "msg": E.value_invalid})

    async def token_delete(self, user: User):
        """Delete user token."""
        jti = await jwt_helper.generate_jti()
        await user.encrypt_attr("jti", jti)
        await self.entity_manager.update(user, commit=True)
        await self.cache_manager.delete(user)

    async def select(self, user_id: int) -> User:
        """Select user."""
        user = await self.cache_manager.get(User, user_id)
        if not user:
            user = await self.entity_manager.select(User, user_id)

        if not user:
            raise HTTPException(status_code=404)

        await self.cache_manager.set(user)
        return user

    async def update(self, user: User, first_name: str, last_name: str, user_summary: str = None,
                     user_contacts: str = None):
        """Update user."""
        user.first_name = first_name
        user.last_name = last_name
        await self.entity_manager.update(user)

        meta_repository = MetaRepository(self.entity_manager)
        await meta_repository.set(UserMeta, user.id, "user_summary", user_summary)
        await meta_repository.set(UserMeta, user.id, "user_contacts", user_contacts)

        await self.entity_manager.commit()
        await self.cache_manager.delete(user)

    async def role_update(self, user: User, user_role: str):
        """Update user role."""
        user.user_role = user_role
        await self.entity_manager.update(user, commit=True)
        await self.cache_manager.delete(user)

    async def delete(self, user: User):
        """Delete user."""
        try:
            await self.entity_manager.delete(user, commit=True)
        except Exception:
            raise RequestValidationError({"loc": ["path", "user_id"], "input": user.id,
                                         "type": "value_locked", "msg": E.value_locked})

        await self.cache_manager.delete(user)

    async def select_all(self, **kwargs):
        """Select some users."""
        # TODO: subquery
        # if "user_contacts__ilike" in kwargs:
        #     kwargs["id__in"] = await self.entity_manager.subquery(UserMeta, "user_id", meta_key__eq="user_contacts",
        #                                                           meta_value__ilike=kwargs["user_contacts__ilike"])

        users = await self.entity_manager.select_all(User, **kwargs)
        for user in users:
            await self.cache_manager.set(user)
        return users

    async def count_all(self, **kwargs):
        """Count users."""
        users_count = await self.entity_manager.count_all(User, **kwargs)
        return users_count

    async def userpic_upload(self, user: User, file: UploadFile):
        """Upload userpic."""
        if file.content_type not in config.USERPIC_MIMES:
            raise RequestValidationError({"loc": ["file", "file"], "input": file.content_type,
                                          "type": "file_mime", "msg": E.file_mime})

        meta_repository = MetaRepository(self.entity_manager)
        userpic_dir = FileManager.path_join(config.APPDATA_PATH, config.USERPIC_DIR)

        userpic = await FileManager.file_upload(file, userpic_dir)
        userpic_path = FileManager.path_join(userpic_dir, userpic)

        image = Image.open(userpic_path)
        image.thumbnail(tuple([config.USERPIC_WIDTH, config.USERPIC_HEIGHT]))
        image.save(userpic_path, image_quality=config.USERPIC_QUALITY)

        await meta_repository.set(UserMeta, user.id, "userpic", userpic, commit=True)
        await self.cache_manager.delete(user)

    async def userpic_delete(self, user: User):
        """Delete userpic."""
        meta_repository = MetaRepository(self.entity_manager)
        userpic = user.getmeta("userpic")

        if userpic:
            userpic_dir = FileManager.path_join(config.APPDATA_PATH, config.USERPIC_DIR)
            userpic_path = FileManager.path_join(userpic_dir, userpic)
            await FileManager.file_delete(userpic_path)
            await meta_repository.set(UserMeta, user.id, "userpic", None, commit=True)
            await self.cache_manager.delete(user)
