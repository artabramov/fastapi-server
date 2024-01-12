# from fastapi.exceptions import RequestValidationError

class E:
    # login errors
    login_denied = "Login denied due to user role permissions"
    login_suspended = "Login attempts are temporarily suspended"

    # JWT errors
    jwt_empty = "The token is missing or empty"
    jwt_invalid = "The token has invalid format"
    jwt_expired = "The token has expired"
    jwt_rejected = "The token contains invalid user data"
    jwt_denied = "The token does not have enough permissions"

    # value errors
    value_empty = "The value is empty"
    value_exists = "The value already exists"
    value_invalid = "The value is invalid"
    value_locked = "The value is locked"

#     @staticmethod
#     def get_error_dict(error_loc: tuple, error_type: str, value: str) -> None:
#         # super().__init__({"loc": loc, "type": type,  "msg": getattr(self, type)})
#         return {"loc": error_loc, "type": error_type, "msg": getattr(E, error_type), "input": value}


# class CustomValidationError(RequestValidationError):
#     def __init__(self, error_loc: tuple, error_type: str, value: str) -> None:
#         super().__init__({"loc": error_loc, "type": error_type, "msg": getattr(E, error_type), "input": value})
