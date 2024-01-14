"""Errors."""


class E:
    """Errors dataclass."""

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

    # file errors
    file_mime = 'Invalid file mimetype.'
