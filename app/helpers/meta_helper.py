"""Meta helper."""

class MetaHelper:
    """Meta helper inserts, updates or deletes meta data."""

    @staticmethod
    async def set(entity_manager, parent_class, parent_id: int, parent_schema, meta_class):

        for meta_key in parent_class._meta_attrs:
            if hasattr(parent_schema, meta_key):
                meta_value = getattr(parent_schema, meta_key)
                if meta_value:
                    meta = meta_class(parent_id, meta_key, meta_value)
                    await entity_manager.insert(meta)
