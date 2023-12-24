from app.managers.entity_manager import EntityManager
from sqlalchemy.orm import Session
from app.schemas.user_schema import UserInsert, UserSelect
from app.repositories.user_repository import UserRepository


class RepositoryProvider:
    """Repository provider."""

    def __init__(self, db: Session) -> None:
        """Init Repository Provider object."""
        self.entity_manager = EntityManager(db)

    def get(self, schema) -> object:
        """Return repository for schema."""
        if schema in [UserInsert, UserSelect]:
            return UserRepository(self.entity_manager)
