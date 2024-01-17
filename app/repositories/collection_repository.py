"""Collection repository."""

from app.models.collection_models import Collection, CollectionMeta
from app.managers.entity_manager import EntityManager
from app.repositories.meta_repository import MetaRepository


class CollectionRepository:
    """Collection repository."""

    def __init__(self, entity_manager: EntityManager, cache_manager) -> None:
        """Init Collection Repository."""
        self.entity_manager = entity_manager
        self.cache_manager = cache_manager

    async def insert(self, user_id: int, collection_name: str, collection_summary: str) -> Collection:
        """Insert a new collection."""
        collection = Collection(user_id, collection_name)
        await self.entity_manager.insert(collection)

        meta_repository = MetaRepository(self.entity_manager)
        await meta_repository.set(CollectionMeta, user_id, "collection_summary", collection_summary)

        await self.entity_manager.commit()
        return collection
