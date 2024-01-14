"""MFA helper."""

import pyotp
import qrcode
from app.dotenv import get_config
from app.managers.file_manager import FileManager
from app.log import get_log

MFA_IMAGE_EXTENSION = 'png'
MFA_IMAGE_VERSION = 1
MFA_IMAGE_SIZE = 6
MFA_IMAGE_BORDER = 1
MFA_IMAGE_FIT = True
MFA_IMAGE_COLOR = 'black'
MFA_IMAGE_BACKGROUND = 'white'
MFA_IMAGE_APP = 'memo'
MFA_IMAGE_DIR = 'mfa/'
MFA_IMAGE_URL = 'mfa/'

config = get_config()
log = get_log()


class MFAHelper:
    """MFA helper."""

    @staticmethod
    async def generate_mfa_key() -> bytes:
        """Generate a random MFA key."""
        return pyotp.random_base32()

    @staticmethod
    async def get_mfa_totp(mfa_key: str) -> str:
        """Return string TOTP key for currenct moment and defined mfa_key."""
        totp = pyotp.TOTP(mfa_key)
        return totp.now()

    @staticmethod
    async def create_mfa_image(user_login: str, mfa_key: str) -> None:
        """Create MFA image."""
        qr = qrcode.QRCode(version=MFA_IMAGE_VERSION, error_correction=qrcode.constants.ERROR_CORRECT_L,
                           box_size=MFA_IMAGE_SIZE, border=MFA_IMAGE_BORDER)
        qr.add_data('otpauth://totp/%s?secret=%s&issuer=%s' % (MFA_IMAGE_APP, mfa_key, user_login))
        qr.make(fit=MFA_IMAGE_FIT)
        img = qr.make_image(fill_color=MFA_IMAGE_COLOR, back_color=MFA_IMAGE_BACKGROUND)
        path = FileManager.path_join(config.APPDATA_PATH,  MFA_IMAGE_DIR, mfa_key + '.' + MFA_IMAGE_EXTENSION)
        img.save(path)
        log.debug("Create MFA image, path=%s." % path)

    @staticmethod
    async def delete_mfa_image(mfa_key: str) -> None:
        """Delete MFA image."""
        path = FileManager.path_join(config.APPDATA_PATH, MFA_IMAGE_DIR, mfa_key + '.' + MFA_IMAGE_EXTENSION)
        FileManager.file_delete(path)
        log.debug("Delete MFA image, path=%s." % path)
