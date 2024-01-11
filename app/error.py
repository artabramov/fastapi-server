from fastapi.exceptions import RequestValidationError


class E(RequestValidationError):
    # login errors
    access_denied = "Access denied."
    attempts_suspended = "Attempts are temporarily suspended"

    # bearer token errors
    token_empty = "Bearer token is empty"
    token_invalid = "Bearer token is invalid"
    token_expired = "Bearer token has expired"
    token_rejected = "Bearer token rejected"

    # value errors
    value_not_found = "The value not found"
    value_exists = "The value already exists"
    value_invalid = "The value is invalid"
    value_locked = "The value is locked"
    value_empty = "The value is empty"

    def __init__(self, loc: tuple, type: str) -> None:
        super().__init__({"loc": loc, "type": type,  "msg": getattr(self, type)})
