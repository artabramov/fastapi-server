"""Entity Manager."""

from sqlalchemy import asc, desc, text
from sqlalchemy.sql import func, exists
from app.log import log
from sqlalchemy.orm import Session

_ORDER_BY, _ORDER = "order_by", "order"
_ASC, _DESC = "asc", "desc"
_OFFSET, _LIMIT = "offset", "limit"
_SQLALCHEMY_RESERVED = [_OFFSET, _LIMIT, _ORDER_BY, _ORDER]
_SQLALCHEMY_OPERATORS = {
    "in": "in_",
    "eq": "__eq__",
    "not": "__ne__",
    "gte": "__ge__",
    "lte": "__le__",
    "gt": "__gt__",
    "lt": "__lt__",
    "like": "like",
}


class EntityManager:
    """Entity Manager provides methods for working with SQLAlchemy entities in the database."""

    def __init__(self, session: Session) -> None:
        """Init Entity Manager."""
        self.session = session

    async def insert(self, obj: object, commit: bool = False) -> None:
        """Insert SQLAlchemy entity into database."""
        self.session.add(obj)
        self.session.flush()

        log.debug("Insert SQLAlchemy entity into database, cls=%s, obj=%s, commit=%s" % (
            str(obj.__class__.__name__), str(obj.__dict__), commit))

        if commit:
            await self.commit()

    async def select(self, cls: object, id: int) -> object:
        """Select SQLAlchemy entity from database."""
        obj = self.session.query(cls).filter(cls.id == id).first()

        log.debug("Select SQLAlchemy entity from database, cls=%s, id=%s, obj=%s" % (
            str(cls.__name__), id, str(obj.__dict__) if obj else None))

        return obj

    async def update(self, obj: object, commit: bool = False) -> None:
        """Update SQLAlchemy entity in database."""
        self.session.merge(obj)
        self.session.flush()

        log.debug('Update SQLAlchemy entity in database, cls=%s, obj=%s.' % (
            str(obj.__class__.__name__), str(obj.__dict__)))

        if commit:
            self.commit()

    async def delete(self, obj: object, commit: bool = False) -> None:
        """Delete SQLAlchemy entity from database."""
        self.session.delete(obj)

        log.debug('Delete SQLAlchemy entity from database, cls=%s, obj=%s.' % (
            str(obj.__class__.__name__), str(obj.__dict__)))

        if commit:
            self.commit()

    async def select_all(self, cls: object, **kwargs) -> list:
        """Select all SQLAlchemy entities from database."""
        query = self.session.query(cls) \
            .filter(*self._where(cls, **kwargs)) \
            .order_by(self._order_by(**kwargs)) \
            .offset(self._offset(**kwargs)) \
            .limit(self._limit(**kwargs))
        return query.all()

    async def exists(self, cls: object, **kwargs) -> bool:
        """Check if SQLAlchemy entity exists in database."""
        res = self.session.query(exists().where(*self._where(cls, **kwargs))).scalar()

        log.debug('Check if SQLAlchemy entity exists in database, cls=%s, kwargs=%s, res=%s' % (
            str(cls.__class__.__name__), str(kwargs), res))

        return res

    async def commit(self) -> None:
        """Commit transaction."""
        self.session.commit()
        log.debug("Transaction commit.")

    async def rollback(self) -> None:
        """Rollback transaction."""
        self.session.rollback()
        log.debug("Transaction rollback.")

    # How to implement dynamic API filtering using query parameters:
    # https://www.mindee.com/blog/flask-sqlalchemy
    def _where(self, cls, **kwargs):
        where = []
        for key in {x: kwargs[x] for x in kwargs if x not in _SQLALCHEMY_RESERVED}:
            column_name, operator = key.split("__")
            column = getattr(cls, column_name)

            value = kwargs[key]
            if operator == "in":
                value = [func.lower(x.strip()) for x in value.split(",")]
            else:
                value = func.lower(value)

            operation = getattr(column, _SQLALCHEMY_OPERATORS[operator])(value)
            where.append(operation)
        return where

    def _order_by(self, **kwargs):
        order_by = text(kwargs.get(_ORDER_BY))
        return asc(order_by) if kwargs[_ORDER] == _ASC else desc(order_by)

    def _offset(self, **kwargs):
        return kwargs.get(_OFFSET, 0)

    def _limit(self, **kwargs):
        return kwargs.get(_LIMIT, 0)
