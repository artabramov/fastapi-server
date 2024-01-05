"""Hash helper."""

import hashlib


class HashHelper:
    """Hash helper."""

    def __init__(self, hash_salt: str) -> None:
        """Init Hash Helper."""
        self.hash_salt = hash_salt

    def get_hash(self, value: str) -> str:
        """Return value hash."""
        encoded_value = (value + self.hash_salt).encode()
        hash_obj = hashlib.sha512(encoded_value)
        return hash_obj.hexdigest()
