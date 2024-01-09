"""User SQLAlchemy model."""

import enum
from time import time
from sqlalchemy import Boolean, Column, ForeignKey, Integer, BigInteger, SmallInteger, String, Enum
from sqlalchemy.orm import relationship
from app.session import Base
from app.mixins.meta_mixin import MetaMixin
from sqlalchemy.ext.hybrid import hybrid_property
from app.helpers.fernet_helper import FernetHelper
from app.helpers.hash_helper import HashHelper
from app.dotenv import get_config
from app.helpers.mfa_helper import MFA_IMAGE_RELATIVE_URL, MFA_IMAGE_EXTENSION

config = get_config()
fernet_helper = FernetHelper(config.FERNET_ENCRYPTION_KEY)
hash_helper = HashHelper(config.HASH_SALT)


class UserMeta(Base):
    __tablename__ = "users_meta"

    id = Column(BigInteger, primary_key=True, index=True)
    created_date = Column(Integer, nullable=False, index=True, default=lambda: int(time()))
    updated_date = Column(Integer, nullable=False, index=True, default=0, onupdate=lambda: int(time()))
    user_id = Column(BigInteger, ForeignKey("users.id"))
    meta_key = Column(String(40), nullable=False, index=True)
    meta_value = Column(String(512), nullable=False)

    user = relationship("User", back_populates="meta")

    def __init__(self, user_id: int, meta_key: str, meta_value: str) -> None:
        """Init user model."""
        self.user_id = user_id
        self.meta_key = meta_key
        self.meta_value = meta_value


class UserRole(enum.Enum):
    none = 0
    reader = 1
    writer = 2
    editor = 3
    admin = 4


class User(Base, MetaMixin):
    __tablename__ = "users"
    _meta_attrs = ["userpic", "user_summary", "user_contacts"]
    _encrypted_attrs = ["mfa_key", "jti"]

    id = Column(BigInteger, primary_key=True, index=True)
    created_date = Column(Integer, nullable=False, index=True, default=lambda: int(time()))
    updated_date = Column(Integer, nullable=False, index=True, default=0, onupdate=lambda: int(time()))
    suspended_date = Column(Integer, nullable=False, default=0)
    user_role = Column(Enum(UserRole), nullable=False, index=True, default=UserRole.none)
    user_login = Column(String(40), nullable=False, index=True, unique=True)
    first_name = Column(String(40), nullable=False, index=True)
    last_name = Column(String(40), nullable=False, index=True)
    pass_hash = Column(String(128), nullable=False, index=True)
    pass_attempts = Column(SmallInteger, nullable=False, default=0)
    pass_accepted = Column(Boolean, nullable=False, default=False)
    mfa_key_encrypted = Column(String(512), nullable=False, unique=True)
    mfa_attempts = Column(SmallInteger(), nullable=False, default=0)
    jti_encrypted = Column(String(512), nullable=False, unique=True)

    meta = relationship("UserMeta", back_populates="user", lazy="joined")

    def __init__(self, user_login: str, first_name: str, last_name: str):
        """Init User SQLAlchemy object."""
        self.suspended_date = 0
        self.user_role = UserRole.none
        self.user_login = user_login
        self.first_name = first_name
        self.last_name = last_name
        self.pass_attempts = 0
        self.pass_accepted = False
        self.mfa_attempts = 0

    async def setattr(self, key: str, value: str) -> None:
        """Set encrypted/hashed attribute."""
        if key in self._encrypted_attrs:
            setattr(self, key + "_encrypted", await fernet_helper.encrypt_value(value))
        
        elif key == "user_pass":
            self.pass_hash = await hash_helper.hash(value)

    async def getattr(self, key: str):
        """Get decrypted attribute."""
        if key in self._encrypted_attrs:
            return await fernet_helper.decrypt_value(getattr(self, key + "_encrypted"))

    @hybrid_property
    def full_name(self) -> str:
        """User full name."""
        return self.first_name + " " + self.last_name
    
    @property
    def mfa_image(self) -> str:
        return config.BASE_URL + MFA_IMAGE_RELATIVE_URL + self.getattr("mfa_key") + "." + MFA_IMAGE_EXTENSION

    async def to_dict(self):
        return {
            "id": self.id,
            "created_date": self.created_date,
            "updated_date": self.updated_date,
            "user_role": self.user_role.name,
            "user_login": self.user_login,
            "user_summary": await self.getmeta("user_summary"),
            "user_contacts": await self.getmeta("user_contacts"),
        }
