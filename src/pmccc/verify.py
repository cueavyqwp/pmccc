"""
校验相关
"""

__all__ = ["TYPES", "HASHER", "get_type", "hasher", "verify_hash"]

import hashlib
import typing
import enum
import os


class TYPES(enum.Enum):

    SHA1 = 0
    SHA256 = 1
    SHA512 = 2
    MD5 = 3


HASHER = {
    TYPES.SHA1: hashlib.sha1,
    TYPES.SHA256: hashlib.sha256,
    TYPES.SHA512: hashlib.sha512,
    TYPES.MD5: hashlib.md5
}


def get_type(value: str) -> TYPES:
    return {32: TYPES.MD5, 40: TYPES.SHA1, 64: TYPES.SHA256, 128: TYPES.SHA512}[len(value)]


class hasher:

    def __init__(self, hasher: TYPES) -> None:
        self.hash = HASHER[hasher]()

    def update(self, data: str | bytes) -> None:
        self.hash.update(data.encode() if isinstance(data, str) else data)

    def load(self, file: str) -> str:
        with open(file, "rb") as fp:
            for data in iter(lambda: fp.read(4096), b""):
                self.update(data)
        return self.hexdigest

    def load_dir(self, path: str, filter: typing.Optional[str] = None) -> str:
        for file in sorted(os.listdir(path)):
            file = os.path.join(path, file)
            if os.path.isdir(file) or (filter is not None and filter not in file):
                continue
            self.load(file)
        return self.hexdigest

    @property
    def hexdigest(self) -> str:
        return self.hash.hexdigest()


class verify_hash(hasher):
    def __init__(self, value: str) -> None:
        super().__init__(get_type(value))
        self.value = value

    def check(self) -> bool:
        return self.hash.hexdigest() == self.value
