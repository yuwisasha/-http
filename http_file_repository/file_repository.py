from pathlib import Path
from abc import ABC, abstractmethod
from hashlib import sha512
from hmac import HMAC, compare_digest

from werkzeug.datastructures import FileStorage


class AbstractFileRepository(ABC):
    @abstractmethod
    def save(self, username: str, file: FileStorage) -> str: ...  

    @abstractmethod
    def get(self, filename: str) -> str: ...  

    @abstractmethod
    def delete(self, username: str, filename: str) -> None: ...  


class FileRepository(AbstractFileRepository):
    _bufsize = 262144

    def __init__(self, base_dir: str) -> None:
        self.base_dir = base_dir

    def __compute_hash(self, username: str, file: FileStorage) -> HMAC:
        encoded_username: bytes = bytes(username, "UTF-8")
        mac = HMAC(encoded_username, file.read(), digestmod=sha512)
        print(file.read())

        return mac

    def __mkdir(self, path: Path) -> None:
        Path.mkdir(path, parents=True, exist_ok=True)

    def __mkfile(self, path: Path) -> None:
        Path.touch(path, exist_ok=False)

    def save(self, username: str, file: FileStorage) -> str:
        file_hash = self.__compute_hash(username, file)
        file_hexdigest = file_hash.hexdigest()
        file_dir = Path(self.base_dir, file_hexdigest[:2])
        file_path = Path(file_dir, file_hexdigest)

        self.__mkdir(file_dir)
        self.__mkfile(file_path)

        with open(file_path, "wb") as local_file:
            # TODO read and write by _bufsize 
            local_file.write(file.read())

        return file_hexdigest

    def get(self, filename: str) -> str:
        return Path(self.base_dir, filename[:2], filename).__str__()

    def delete(self, *, username: str, filename: str) -> None:
        encoded_username: bytes = bytes(username, "UTF-8")
        file_path = self.get(filename)
        file_content = open(file_path)
        mac = HMAC(encoded_username, file_content.read())
        file: bytes = bytes.fromhex(filename)

        file_path = Path(self.base_dir, filename[:2], filename)
        Path.unlink(file_path)
