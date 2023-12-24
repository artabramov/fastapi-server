from sqlalchemy import asc, desc, text
from sqlalchemy.sql import func, exists
from decimal import Decimal

ENTITY_MANAGER_RESERVED_KEYS = ['subquery', 'order_by', 'order', 'limit', 'offset']
ENTITY_MANAGER_DELETE_ALL_BATCH_SIZE = 500


class EntityManager:
    """Entity manager."""

    def __init__(self, db) -> None:
        """Init entity manager object."""
        self.db = db

    def insert(self, obj: object, commit: bool = False) -> None:
        """Insert entity into database."""
        self.db.add(obj)
        self.db.flush()

        if commit:
            self.db.commit()
            self.db.refresh(obj)
