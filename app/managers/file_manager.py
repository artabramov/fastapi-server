"""File Manager."""

import os
import uuid
import shutil
import filetype
# import io
# from app.helpers.fernet_helper import FernetHelper
from app.log import get_log

log = get_log()


class FileManager:
    """File Manager."""

    @staticmethod
    def path_exists(path: str) -> bool:
        """Check if exists."""
        return os.path.exists(path)

    @staticmethod
    def path_empty(path: str) -> bool:
        """Check if directory contains files."""
        return len(os.listdir(path)) == 0

    @staticmethod
    def path_join(path: str, *paths) -> str:
        """Join two or more paths."""
        return os.path.join(path, *paths)

    @staticmethod
    def path_create(path: str) -> None:
        """Create a new directory."""
        os.mkdir(path)
        log.debug("Create a new directory, path=%s." % path)

    @staticmethod
    def path_delete(path: str) -> None:
        """Delete path."""
        os.rmdir(path)
        log.debug("Delete path, path=%s." % path)

    @staticmethod
    def path_truncate(path: str) -> None:
        """Delete all files and subdirectories in path."""
        for filename in os.listdir(path):
            file_path = os.path.join(path, filename)
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        log.debug('Path truncated. Path=%s.' % path)

    @staticmethod
    def uuid() -> str:
        """Create uuid."""
        return str(uuid.uuid4())

    @staticmethod
    def file_path(path: str) -> str:
        """Get absolute path to file directory."""
        return os.path.dirname(os.path.abspath(path))

    @staticmethod
    def file_name(path: str) -> str:
        """Get file path without extension."""
        file_name, _ = os.path.splitext(path)
        return file_name

    @staticmethod
    def file_ext(path: str) -> str:
        """Get file extension."""
        _, file_ext = os.path.splitext(path)
        return file_ext

    @staticmethod
    def file_mime(path: str) -> str:
        """Get file mimetype."""
        kind = filetype.guess(path)
        return kind.mime if kind else None

    @staticmethod
    def file_size(path: str) -> int:
        """Get file size."""
        return os.path.getsize(path)

    @staticmethod
    def file_date(path: str) -> int:
        """Get file time in UNIX timestamp."""
        return int(os.stat(path).st_mtime)

    @staticmethod
    def file_exists(path: str) -> bool:
        """Check is file exist."""
        return os.path.isfile(path)

    @staticmethod
    def files_list(path: str) -> list:
        """Get files list in directory exclude filenames started with a dot."""
        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and not f.startswith('.')]
        return sorted(files)

    @staticmethod
    def file_delete(path: str) -> None:
        """Delete a file."""
        if os.path.isfile(path):
            os.remove(path)
            log.debug('File deleted. Path=%s.' % path)

    @staticmethod
    def file_copy(src_path: str, dst_path: str) -> None:
        """Copy file."""
        shutil.copyfile(src_path, dst_path)
        log.debug('File copied. Src_path=%s. Dst_path=%s' % (src_path, dst_path))

    @staticmethod
    def file_move(src_path: str, dst_path: str) -> None:
        """Move/rename file."""
        os.rename(src_path, dst_path)
        log.debug('File moved. Src_path=%s. Dst_path=%s' % (src_path, dst_path))

    @staticmethod
    def file_exec(command: str) -> None:
        """Execute the command."""
        os.system(command)

    # @staticmethod
    # def file_upload(file: object, path: str) -> str:
    #     """Upload a file and return filename."""
    #     filename = self.path_join(self.uuid() + self.file_ext(file.filename))
    #     path = self.path_join(path, filename)
    #     file.save(path)
    #     log.debug('File uploaded. Path=%s.' % path)
    #     return filename

    # @staticmethod
    # def file_encrypt(base_path: str, filename: str, encryption_key: bytes) -> str:
    #     """Encrypt file and return filename."""
    #     file_ext = self.file_ext(filename)
    #     new_filename = filename.replace(file_ext, '')
    #     path = self.path_join(base_path, new_filename)
    #     self.file_move(self.path_join(base_path, filename), path)
    #     FernetHelper(encryption_key).encrypt_file(path)
    #     log.debug('File encrypted. Path=%s.' % path)
    #     return new_filename

    # @staticmethod
    # def file_decrypt(path: str, encryption_key: bytes) -> bytes:
    #     """Decrypt file and return bytes stream."""
    #     decrypted_file = io.BytesIO(FernetHelper(encryption_key).decrypt_file(path))
    #     log.debug('File decrypted. Path=%s.' % path)
    #     return decrypted_file
