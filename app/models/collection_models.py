"""Collection and related SQLAlchemy models."""

from time import time
from sqlalchemy import Column, ForeignKey, Integer, BigInteger, String
from sqlalchemy.orm import relationship
from app.session import Base
from app.mixins.meta_mixin import MetaMixin


class CollectionMeta(Base):
    """SQLAlchemy model for collection meta."""

    __tablename__ = "collections_meta"

    id = Column(BigInteger, primary_key=True, index=True)
    created_date = Column(Integer, nullable=False, index=True, default=lambda: int(time()))
    updated_date = Column(Integer, nullable=False, index=True, default=0, onupdate=lambda: int(time()))
    parent_id = Column(BigInteger, ForeignKey("collections.id"), nullable=False)
    meta_key = Column(String(40), nullable=False, index=True)
    meta_value = Column(String(512), nullable=False)

    collection = relationship("Collection", back_populates="collection_meta")

    def __init__(self, parent_id: int, meta_key: str, meta_value: str) -> None:
        """Init collection meta model."""
        self.parent_id = parent_id
        self.meta_key = meta_key
        self.meta_value = meta_value


class Collection(Base, MetaMixin):
    """SQLAlchemy model for collection."""

    __tablename__ = "collections"

    id = Column(BigInteger, primary_key=True, index=True)
    created_date = Column(Integer, nullable=False, index=True, default=lambda: int(time()))
    updated_date = Column(Integer, nullable=False, index=True, default=0, onupdate=lambda: int(time()))
    collection_name = Column(String(128), nullable=False, index=True)
    mediafiles_count = Column(Integer, index=True, nullable=False, default=0)

    collection_meta = relationship("CollectionMeta", back_populates="collection", lazy="joined", cascade="all,delete")

    def __init__(self, collection_name: str):
        """Init collection SQLAlchemy object."""
        self.collection_name = collection_name
        self.mediafiles_count = 0

    @property
    def meta(self) -> dict:
        """Collection meta values."""
        return {
            "collection_summary": self.getmeta("collection_summary"),
        }
