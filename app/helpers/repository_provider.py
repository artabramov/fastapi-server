from app.managers.entity_manager import EntityManager
from app.managers.cache_manager import CacheManager
from sqlalchemy.orm import Session
from redis import Redis
from app.schemas.user_schema import UserInsert, UserSelect
from app.repositories.user_repository import UserRepository
from app.models.user import User


class RepositoryProvider:
    """Repository provider."""

    def __init__(self, db: Session, cache: Redis, user: User = None) -> None:
        """Init Repository Provider object."""
        cache_manager = CacheManager(cache)
        self.entity_manager = EntityManager(db, cache_manager)
        self.user = user

    def get(self, schema) -> object:
        """Return repository for schema."""
        if schema in [UserInsert, UserSelect]:
            return UserRepository(self.entity_manager)
