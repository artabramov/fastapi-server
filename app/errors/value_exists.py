from fastapi.exceptions import RequestValidationError


class ValueExists(RequestValidationError):

    ERROR_TYPE = "value_exists"
    ERROR_MSG = "The value already exists"

    def __init__(self, **kwargs) -> None:
        super().__init__(kwargs | {"type": self.ERROR_TYPE, "msg": self.ERROR_MSG})
