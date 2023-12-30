from contextvars import ContextVar
from typing import Any

context_data: ContextVar[dict] = ContextVar('context_data', default={})


def set_context_var(key: str, value: Any) -> None:
    _context_data = context_data.get()
    _context_data[key] = value
    context_data.set(_context_data)


def get_context_var(key: str):
    _context_data = context_data.get()
    return _context_data.get(key)


def delete_context_var(key: str):
    _context_data = context_data.get()
    del _context_data[key]
    context_data.set(_context_data)
