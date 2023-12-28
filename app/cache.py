"""Provides Redis cache session object."""

from app.dotenv import get_config
import redis


def get_cache():
    config = get_config()
    yield redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, decode_responses=config.REDIS_DECODE)
