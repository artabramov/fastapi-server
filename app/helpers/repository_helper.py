"""Repository helper."""

from app.managers.entity_manager import EntityManager
from app.managers.cache_manager import CacheManager
from sqlalchemy.orm import Session
from redis import Redis
from app.repositories.user_repository import UserRepository
from app.repositories.collection_repository import CollectionRepository
from app.models.user_models import User
from app.models.collection_models import Collection


class RepositoryHelper:
    """Repository helper."""

    def __init__(self, session: Session, cache: Redis, user: User = None) -> None:
        """Init Repository Provider object."""
        self.cache_manager = CacheManager(cache)
        self.entity_manager = EntityManager(session)
        self.user = user

    async def get_repository(self, tablename: str) -> object:
        """Return repository for schema."""
        if tablename == User.__tablename__:
            return UserRepository(self.entity_manager, self.cache_manager)

        elif tablename == Collection.__tablename__:
            return CollectionRepository(self.entity_manager, self.cache_manager)
