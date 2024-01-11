from fastapi.exceptions import RequestValidationError


class E(RequestValidationError):
    # auth errors
    access_denied = "Access denied."
    attempts_suspended = "Attempts are temporarily suspended"

    # value errors
    value_not_found = "The value not found"
    value_exists = "The value already exists"
    value_invalid = "The value is invalid"
    value_locked = "The value is locked"

    def __init__(self, loc: tuple, type: str) -> None:
        super().__init__({"loc": loc, "type": type,  "msg": getattr(self, type)})
