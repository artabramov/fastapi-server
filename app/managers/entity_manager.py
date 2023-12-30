"""Entity Manager."""

from sqlalchemy import asc, desc, text
from sqlalchemy.sql import func, exists
from decimal import Decimal
from app.log import log
from sqlalchemy.orm import Session

ENTITY_MANAGER_RESERVED_KEYS = ['subquery', 'order_by', 'order', 'limit', 'offset']
ENTITY_MANAGER_DELETE_ALL_BATCH_SIZE = 500


class EntityManager:
    """Entity Manager provides methods for working with SQLAlchemy entities in the database."""

    def __init__(self, session: Session) -> None:
        """Init Entity Manager."""
        self.session = session

    async def insert(self, obj: object, commit: bool = False) -> None:
        """Insert SQLAlchemy entity into database."""
        self.session.add(obj)
        self.session.flush()

        if commit:
            await self.commit()

        log.debug("Insert SQLAlchemy entity into database, cls=%s, obj=%s, commit=%s" % (
            str(obj.__class__.__name__), str(obj.__dict__), commit))

    async def select(self, cls: object, **kwargs) -> object:
        """Select SQLAlchemy entity from database."""
        obj = self.session.query(cls).filter(*self._extract_clauses([
            self._add_clause(cls, k, v) for k, v in kwargs.items()])).first()

        log.debug("Select SQLAlchemy entity from database, cls=%s, kwargs=%s, obj=%s" % (
            str(cls.__name__), str(kwargs), str(obj.__dict__) if obj else None))

        return obj

    async def update(self, obj: object, commit: bool = False) -> None:
        """Update SQLAlchemy entity in database."""
        self.session.merge(obj)
        self.session.flush()

        if commit:
            self.commit()

        log.debug('Update SQLAlchemy entity in database, cls=%s, obj=%s.' % (
            str(obj.__class__.__name__), str(obj.__dict__)))

    async def delete(self, obj: object, commit: bool = False) -> None:
        """Delete SQLAlchemy entity from database."""
        self.session.delete(obj)
        self.session.flush()

        if commit:
            self.commit()

        log.debug('Delete SQLAlchemy entity from database, cls=%s, obj=%s.' % (
            str(obj.__class__.__name__), str(obj.__dict__)))

    async def exists(self, cls: object, **kwargs) -> bool:
        """Check if SQLAlchemy entity exists in database."""
        res = self.session.query(exists().where(*self._get_where(cls, kwargs))).scalar()

        log.debug('Check if SQLAlchemy entity exists in database, cls=%s, kwargs=%s, res=%s' % (
            str(cls.__class__.__name__), str(kwargs), res))
        return res

    async def commit(self) -> None:
        """Commit transaction."""
        self.session.commit()

    async def rollback(self) -> None:
        """Rollback transaction."""
        self.session.rollback()

    def _get_where(self, cls: object, kwargs: dict) -> list:
        """Create where expression."""
        return self._extract_clauses([
            self._add_clause(cls, k, v) for k, v in kwargs.items() if k not in ENTITY_MANAGER_RESERVED_KEYS])

    def _extract_clauses(self, clauses: list) -> list:
        """Convert clauses from nested list into plain list."""
        res = []
        for el in clauses:
            if isinstance(el, list):
                res.extend(el)
            else:
                res.append(el)
        return res

    def _add_clause(self, cls: object, k: str, v):
        """Add clause into query."""
        if isinstance(v, list):
            return getattr(cls, k).in_(v)

        elif isinstance(v, dict):
            res = []
            for operator in v:
                if operator == '=' or operator == 'eq':
                    res.append(getattr(cls, k) == v[operator])
                elif operator == '!=' or operator == 'ne':
                    res.append(getattr(cls, k) != v[operator])
                elif operator == '>' or operator == 'gt':
                    res.append(getattr(cls, k) > v[operator])
                elif operator == '>=' or operator == 'ge':
                    res.append(getattr(cls, k) >= v[operator])
                elif operator == '<' or operator == 'lt':
                    res.append(getattr(cls, k) < v[operator])
                elif operator == '<=' or operator == 'le':
                    res.append(getattr(cls, k) <= v[operator])
            return res

        elif str(v).startswith('%') and str(v).endswith('%'):
            return getattr(cls, k).ilike(v)

        else:
            return getattr(cls, k) == v

    def _get_subquery(self, **kwargs) -> object:
        """Get subquery."""
        return self.session.query(kwargs['foreign_key']).filter(
            *self._extract_clauses([self._add_clause(kwargs['subquery_cls'], k, v) for k, v in kwargs['subquery_kwargs'].items()])  # noqa E501
        ).subquery()