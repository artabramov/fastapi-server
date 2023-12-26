import enum
from time import time
from sqlalchemy import Boolean, Column, ForeignKey, Integer, BigInteger, SmallInteger, String, Enum
from sqlalchemy.orm import relationship
from app.db import Base


class UserRole(enum.Enum):
    none = 0
    reader = 1
    writer = 2
    editor = 3
    admin = 4


class User(Base):
    __tablename__ = 'users'
    _meta_keys = ["user_summary", "user_contacts"]

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
    userpic = Column(String(512), nullable=True, unique=True)

    meta = relationship("UserMeta", back_populates="user")

    def __init__(self, user_login: str, user_pass: str, first_name: str, last_name: str) -> None:
        """Init user model."""
        self.suspended_date = 0
        self.user_role = UserRole.none
        self.user_login = user_login
        self.first_name = first_name
        self.last_name = last_name
        self.user_pass = user_pass
        self.pass_hash = user_pass + 'salt'
        self.pass_attempts = 0
        self.pass_accepted = False
        self.mfa_key_encrypted = 'mfa-key-encrypted' + str(time())
        self.mfa_attempts = 0
        self.jti_encrypted = 'jti-encrypted' + str(time())
