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

config = get_config()
fernet_helper = FernetHelper(config.FERNET_ENCRYPTION_KEY)
hash_helper = HashHelper(config.HASH_SALT)


class UserRole(enum.Enum):
    none = 0
    reader = 1
    writer = 2
    editor = 3
    admin = 4


class User(Base, MetaMixin):
    __tablename__ = "users"
    _meta_keys = ["userpic", "user_summary", "user_contacts"]

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

    meta = relationship("UserMeta", back_populates="user", lazy='joined')

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
        """Set attribute."""
        if key == "user_pass":
            self.pass_hash = await hash_helper.hash(value)

        elif key == "mfa_key":
            self.mfa_key_encrypted = await fernet_helper.encrypt_value(value)

        elif key == "jti":
            self.jti_encrypted = await fernet_helper.encrypt_value(value)

    async def getattr(self, key: str):
        """Get attribute."""
        if key == "mfa_key":
            return await fernet_helper.decrypt_value(self.mfa_key_encrypted)

        elif key == "jti":
            return await fernet_helper.decrypt_value(self.jti_encrypted)

    @hybrid_property
    def full_name(self) -> str:
        """Virtial full name."""
        return self.first_name + ' ' + self.last_name
