from redis import Redis
from json import dumps, loads
from collections import OrderedDict

class CacheManager:
    """Cache manager."""

    def __init__(self, cache: Redis) -> None:
        """Init cache manager."""
        self.cache = cache

    def _asdict(self, obj):
        result = OrderedDict()
        for key in obj.__mapper__.c.keys():
            result[key] = getattr(obj, key)
        return result

    def set(self, obj: object) -> None:
        """Set sqlalchemy model in cache."""
        self.cache.set('%s.%s' % (obj.__tablename__, obj.id), dumps(self._asdict(obj)))

    def get(self, cls: object, obj_id: object) -> object:
        """Get sqlalchemy model from cache."""
        obj = self.cache.get('%s.%s' % (cls.__tablename__, obj_id))
        return obj
