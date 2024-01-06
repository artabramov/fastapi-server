"""Create config from dotenv file."""

import os
from dotenv import load_dotenv
from functools import lru_cache
from typing import Optional

DOTENV_FILE = "../.env"


class Config:
    """Config dataclass."""

    LOGGING_LEVEL: str
    LOGGING_FORMAT: str
    LOGGING_FILENAME: str
    LOGGING_FILESIZE: int
    LOGGING_FILES_LIMIT: int

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
    REDIS_EXPIRE: int

    FERNET_ENCRYPTION_STRING: str
    FERNET_ENCRYPTION_KEY: Optional[bytes]

    JWT_SECRET: str
    JWT_ALGORITHM: str

    HASH_SALT: str

    BASE_PATH: str
    BASE_URL: str


@lru_cache
def get_config() -> Config:
    """Get config object from file or cache."""
    load_dotenv(DOTENV_FILE)
    config = Config()

    for key in config.__annotations__:
        value = os.environ.get(key)

        if value == "True":
            config.__dict__[key] = True

        elif value == "False":
            config.__dict__[key] = False

        elif value == "None":
            config.__dict__[key] = None

        elif value.isdigit():
            config.__dict__[key] = int(os.environ.get(key))

        else:
            config.__dict__[key] = os.environ.get(key)

    config.FERNET_ENCRYPTION_KEY = bytes(config.FERNET_ENCRYPTION_STRING, "utf-8")

    return config
