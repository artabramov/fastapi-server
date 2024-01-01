"""Entity Manager."""

from sqlalchemy import asc, desc, text
from sqlalchemy.sql import func, exists
from decimal import Decimal
from app.log import log
from sqlalchemy.orm import Session

ENTITY_MANAGER_RESERVED_KEYS = ['subquery', 'order_by', 'order', 'limit', 'offset']
ENTITY_MANAGER_DELETE_ALL_BATCH_SIZE = 500
_ORDER_BY = "order by"
_ORDER = "order"
_OFFSET = "offset"
_LIMIT = "limit"
_ASC = "asc"
_DESC = "desc"
_IN = "in"
_ID = "id"
_RESERVED_KEYS = [_ORDER_BY, _ORDER, _OFFSET, _LIMIT, _ASC, _DESC, _IN]


class EntityManager:
    """Entity Manager provides methods for working with SQLAlchemy entities in the database."""

    def __init__(self, session: Session) -> None:
        """Init Entity Manager."""
        self.session = session
        self.query = None

    def __getattr__(self, attr: str, *args, **kwargs):
        pass
        return getattr(self.query)(*args, **kwargs)

    async def insert(self, obj: object, commit: bool = False) -> None:
        """Insert SQLAlchemy entity into database."""
        self.session.add(obj)
        self.session.flush()

        if commit:
            await self.commit()

        log.debug("Insert SQLAlchemy entity into database, cls=%s, obj=%s, commit=%s" % (
            str(obj.__class__.__name__), str(obj.__dict__), commit))

    async def select(self, cls: object, id: int) -> object:
        """Select SQLAlchemy entity from database."""
        obj = self.session.query(cls).filter(cls.id == id).first()

        log.debug("Select SQLAlchemy entity from database, cls=%s, id=%s, obj=%s" % (
            str(cls.__name__), id, str(obj.__dict__) if obj else None))

        return obj

    async def select_all(self, cls: object, **kwargs) -> list:
        """Select all SQLAlchemy entities from database."""
        query = self.session.query(cls)
        return query.all()

    # def select_all(self, cls: object, **kwargs) -> list:
    #     """Select all SQLAlchemy entities from database."""
    #     query = self.session.query(cls)
    #     query = cls.query.filter(*self._get_where(cls, kwargs))

    #     if 'subquery' in kwargs:
    #         subquery = self._get_subquery(**kwargs['subquery'])
    #         query = query.filter(cls.id.in_(subquery))

    #     if 'order_by' in kwargs and kwargs['order'] == 'asc':
    #         query = query.order_by(asc(kwargs['order_by']))

    #     elif 'order_by' in kwargs and kwargs['order'] == 'desc':
    #         query = query.order_by(desc(kwargs['order_by']))

    #     else:
    #         query = query.order_by(asc('id'))

    #     if 'limit' in kwargs:
    #         query = query.limit(kwargs['limit'])

    #     else:
    #         query = query.limit(None)

    #     if 'offset' in kwargs:
    #         query = query.offset(kwargs['offset'])

    #     else:
    #         query = query.offset(0)

    #     objs = query.all()
    #     return objs

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
        log.debug("Transaction commit.")

    async def rollback(self) -> None:
        """Rollback transaction."""
        self.session.rollback()
        log.debug("Transaction rollback.")

    # def _where(self, cls: object, kwargs: dict) -> list:
    #     """Create complete "where" expression."""
    #     conditions = [self._condition(cls, k, v) for k, v in kwargs.items() if k not in ENTITY_MANAGER_RESERVED_KEYS]

    #     return self._merge(
    #         [self._condition(cls, k, v) for k, v in kwargs.items() if k not in ENTITY_MANAGER_RESERVED_KEYS])

    # def _filters(self, query, kwargs: dict):
    #     if "order by" in kwargs and kwargs["order"] == "asc":
    #         query = query.order_by(asc(kwargs["order by"]))

    #     elif "order by" in kwargs and kwargs["order"] == "desc":
    #         query = query.order_by(desc(kwargs["order by"]))

    #     else:
    #         query = query.order_by(asc("id"))

    #     if "limit" in kwargs:
    #         query = query.limit(kwargs["limit"])

    #     else:
    #         query = query.limit(None)

    #     if "offset" in kwargs:
    #         query = query.offset(kwargs["offset"])

    #     else:
    #         query = query.offset(0)

    # def _condition(self, cls: object, k: str, v):
    #     """Add one condition to the query."""
    #     if isinstance(v, list):
    #         return getattr(cls, k).in_(v)

    #     elif isinstance(v, dict):
    #         res = []
    #         for operator in v:
    #             if operator in ["=", "eq"]:
    #                 res.append(getattr(cls, k) == v[operator])

    #             elif operator in ['!=', 'ne']:
    #                 res.append(getattr(cls, k) != v[operator])

    #             elif operator in ['>', 'gt']:
    #                 res.append(getattr(cls, k) > v[operator])

    #             elif operator in ['>=', 'ge']:
    #                 res.append(getattr(cls, k) >= v[operator])

    #             elif operator in ['<', 'lt']:
    #                 res.append(getattr(cls, k) < v[operator])

    #             elif operator in ['<=', 'le']:
    #                 res.append(getattr(cls, k) <= v[operator])
    #         return res

    #     elif str(v).startswith('%') and str(v).endswith('%'):
    #         return getattr(cls, k).ilike(v)

    #     else:
    #         return getattr(cls, k) == v

    # def _subquery(self, **kwargs) -> object:
    #     """Get subquery."""
    #     return self.session.query(kwargs['foreign_key']).filter(
    #         *self._extract_clauses([self._add_clause(kwargs['subquery_cls'], k, v) for k, v in kwargs['subquery_kwargs'].items()])  # noqa E501
    #     ).subquery()

    # def _merge(self, conditions: list) -> list:
    #     """Merge all conditions from nested list into plain one."""
    #     result = []
    #     for el in conditions:
    #         if isinstance(el, list):
    #             result.extend(el)
    #         else:
    #             result.append(el)
    #     return result









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
                if operator in ['=', 'eq']:
                    res.append(getattr(cls, k) == v[operator])

                elif operator in ['!=', 'ne']:
                    res.append(getattr(cls, k) != v[operator])

                elif operator in ['>', 'gt']:
                    res.append(getattr(cls, k) > v[operator])

                elif operator in ['>=', 'ge']:
                    res.append(getattr(cls, k) >= v[operator])

                elif operator in ['<', 'lt']:
                    res.append(getattr(cls, k) < v[operator])

                elif operator in ['<=', 'le']:
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
