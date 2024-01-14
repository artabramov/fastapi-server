"""Meta repository."""

from app.managers.entity_manager import EntityManager


class MetaRepository:
    """Meta repository."""

    def __init__(self, entity_manager: EntityManager) -> None:
        """Init User Repository."""
        self.entity_manager = entity_manager

    async def set(self, meta_class: object, parent_id: int, meta_key: str, meta_value: str = None):
        """Insert, update or delete meta value."""
        meta = await self.entity_manager.select_by(meta_class, parent_id__eq=parent_id, meta_key__eq=meta_key)
        if not meta and meta_value:
            meta = meta_class(parent_id, meta_key, meta_value)
            await self.entity_manager.insert(meta)

        elif meta and meta_value:
            meta.meta_value = meta_value
            await self.entity_manager.update(meta)

        elif meta and not meta_value:
            await self.entity_manager.delete(meta)
