from pathlib import Path
from abc import ABC, abstractmethod
from hashlib import sha256


class AbstractFileRepository(ABC):
    @abstractmethod
    def save(self, file_data: bytes) -> str: ...  

    @abstractmethod
    def get(self, filename: str) -> str: ...  

    @abstractmethod
    def delete(self, filename: str) -> None: ...  


class FileRepository(AbstractFileRepository):
    def __init__(self, base_dir: str) -> None:
        self.base_dir = base_dir

    def __compute_hash(self, data: bytes) -> str:
        sha256_hash = sha256(data)

        return sha256_hash.hexdigest()

    def __mkdir(self, path: Path) -> None:
        Path.mkdir(path, parents=True, exist_ok=True)

    def __mkfile(self, path: Path) -> None:
        Path.touch(path, exist_ok=False)

    def save(self, file_data: bytes) -> str:
        file_hash = self.__compute_hash(file_data)
        file_dir = Path(self.base_dir, file_hash[:2])
        file_path = Path(file_dir, file_hash)

        self.__mkdir(file_dir)
        self.__mkfile(file_path)

        with open(file_path, "wb") as file:
            file.write(file_data)

        return file_hash

    def get(self, filename: str) -> str:
        return Path(self.base_dir, filename[:2], filename).__str__()

    def delete(self, filename: str) -> None:
        file_path = Path(self.base_dir, filename[:2], filename)
        Path.unlink(file_path)
