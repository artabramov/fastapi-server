from app.managers.entity_manager import EntityManager


class MetaRepository:

    def __init__(self, entity_manager: EntityManager) -> None:
        """Init User Repository."""
        self.entity_manager = entity_manager

    async def set(self, meta_class: object, parent_id: int, meta_key: str, meta_value: str = None):
        if meta_value:
            meta = meta_class(parent_id, meta_key, meta_value)
            await self.entity_manager.insert(meta)