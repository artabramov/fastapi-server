"""Provides Postgres database session object."""
from app.dotenv import get_config
import logging
from logging.handlers import RotatingFileHandler
from logging import Filter
from app.context import get_context_var

config = get_config()


class ContextualFilter(Filter):
    """Contextual filter for logging."""

    def filter(self, message: object) -> bool:
        """Customize the contextual filter."""
        message.uuid = get_context_var("uuid")
        return True


handler = RotatingFileHandler(filename=config.LOGGING_FILENAME, maxBytes=config.LOGGING_FILESIZE,
                              backupCount=config.LOGGING_FILES_LIMIT)
handler.setFormatter(logging.Formatter(config.LOGGING_FORMAT))

log = logging.getLogger(__name__)
log.addHandler(handler)
log.addFilter(ContextualFilter())
log.setLevel(logging.getLevelName(config.LOGGING_LEVEL))


def get_log():
    """Get logger object."""
    return log
