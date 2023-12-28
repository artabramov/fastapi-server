from redis import Redis
# from json import dumps, loads
from collections import OrderedDict
import pickle
from app.dotenv import get_config
# from sqlalchemy.ext.serializer import dumps, loads
from marshal import dumps, loads

config = get_config()

class CacheManager:
    """Cache manager."""

    def __init__(self, cache: Redis) -> None:
        """Init cache manager."""
        self.cache = cache

    def set(self, obj: object) -> None:
        """Set sqlalchemy model in cache."""
        self.cache.set('%s:%s' % (obj.__tablename__, obj.id), dumps(obj), ex=config.REDIS_EXPIRE)

    def get(self, cls: object, obj_id: object) -> object:
        """Get sqlalchemy model from cache."""
        obj = self.cache.get('%s:%s' % (cls.__tablename__, obj_id))
        return loads(obj)
