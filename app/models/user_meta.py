import enum
from time import time
from sqlalchemy import Boolean, Column, ForeignKey, Integer, BigInteger, SmallInteger, String, Enum
from sqlalchemy.orm import relationship
from app.db import Base


class UserMeta(Base):
    __tablename__ = "users_meta"
    _cachable = False

    id = Column(BigInteger, primary_key=True, index=True)
    created_date = Column(Integer, nullable=False, index=True, default=lambda: int(time()))
    updated_date = Column(Integer, nullable=False, index=True, default=0, onupdate=lambda: int(time()))
    user_id = Column(BigInteger, ForeignKey("users.id"))
    meta_key = Column(String(40), nullable=False, index=True)
    meta_value = Column(String(512), nullable=False)

    user = relationship("User", back_populates="meta", lazy='select')

    def __init__(self, user_id: int, meta_key: str, meta_value: str) -> None:
        """Init user model."""
        self.user_id = user_id
        self.meta_key = meta_key
        self.meta_value = meta_value
