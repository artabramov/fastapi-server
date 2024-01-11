"""JWT helper."""

import random
import string
import jwt
import time

JTI_LENGTH = 16


class JWTHelper():
    """JWT helper."""

    def __init__(self, jwt_secret: str, jwt_algorithm: str, jti_length=JTI_LENGTH) -> None:
        """Init JWT helper object."""
        self.jwt_secret = jwt_secret
        self.jwt_algorithm = jwt_algorithm
        self.jti_length = jti_length

    async def generate_jti(self) -> str:
        """Generate JWT identifier."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=self.jti_length))

    async def encode_token(self, user_id: int, user_role: str, user_login: str, jti: str, exp=None) -> str:
        """Encode user data into JWT token."""
        payload = {
            'user_id': user_id,
            'user_role': user_role,
            'user_login': user_login,
            'jti': jti,
            'iat': int(time.time()),
        }
        if exp:
            payload['exp'] = int(exp)

        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)

    async def decode_token(self, jwt_token: str) -> dict:
        """Decode user data from JWT token."""
        payload = jwt.decode(jwt_token, self.jwt_secret, algorithms=self.jwt_algorithm)
        res = {
            'user_id': payload['user_id'],
            'user_role': payload['user_role'],
            'user_login': payload['user_login'],
            'iat': payload['iat'],
            'jti': payload['jti'],
        }
        if 'exp' in payload:
            res['exp'] = payload['exp']
        return res
