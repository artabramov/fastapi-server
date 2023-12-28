"""Create config from dotenv file."""

import os
from dotenv import load_dotenv
from functools import lru_cache

DOTENV_FILE = '../.env'


class Config:
    """Config dataclass."""

    SQLALCHEMY_USERNAME: str
    SQLALCHEMY_PASSWORD: str
    SQLALCHEMY_HOST: str
    SQLALCHEMY_PORT: int
    SQLALCHEMY_DATABASE: str
    SQLALCHEMY_AUTOCOMMIT: bool
    SQLALCHEMY_AUTOFLUSH: bool

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DECODE: bool


@lru_cache
def get_config() -> Config:
    """Get config object from file or cache."""
    load_dotenv(DOTENV_FILE)
    config = Config()

    for key in config.__annotations__:
        value = os.environ.get(key).strip().lower()

        if value == 'true':
            config.__dict__[key] = True

        elif value == 'false':
            config.__dict__[key] = False

        elif value.isdigit():
            config.__dict__[key] = int(os.environ.get(key))

        else:
            config.__dict__[key] = os.environ.get(key)

    config.SQLALCHEMY_URI = 'postgresql+psycopg2://%s:%s@%s:%s/%s' % (
        config.SQLALCHEMY_USERNAME, config.SQLALCHEMY_PASSWORD, config.SQLALCHEMY_HOST, config.SQLALCHEMY_PORT,
        config.SQLALCHEMY_DATABASE)
    return config
