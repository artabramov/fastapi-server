"""Fernet helper for encrypt/decrypt values and files."""

from cryptography.fernet import Fernet


class FernetHelper:
    """Fernet helper for encrypt/decrypt values and files."""

    def __init__(self, encryption_key: bytes) -> None:
        """Init fernet helper object."""
        self.encryption_key = encryption_key
        self.cipher_suite = Fernet(self.encryption_key)

    @staticmethod
    def create_encryption_key() -> bytes:
        """Generate encryption key for config."""
        return Fernet.generate_key()

    async def encrypt_value(self, value: str) -> str:
        """Encrypt string value."""
        encoded_text = self.cipher_suite.encrypt(str.encode(value))
        return encoded_text.decode()

    async def decrypt_value(self, value: str) -> str:
        """Decrypt string value."""
        decoded_text = self.cipher_suite.decrypt(str.encode(value))
        return decoded_text.decode()

    async def encrypt_file(self, path: str) -> None:
        """Encrypt file."""
        with open(path, 'rb') as file:
            data = file.read()
        encrypted_data = self.cipher_suite.encrypt(data)
        with open(path, 'wb') as file:
            file.write(encrypted_data)

    async def decrypt_file(self, path: str) -> bytes:
        """Decrypt file to bytes object."""
        with open(path, 'rb') as file:
            encrypted_data = file.read()
        data = self.cipher_suite.decrypt(encrypted_data)
        return data
