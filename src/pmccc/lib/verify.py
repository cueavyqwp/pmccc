"""
校验相关
"""

__all__ = ["get_type", "hasher", "verify_hash"]

import typing
import os

from ..types import HASH_TYPE, HASHER


def get_type(value: str) -> HASH_TYPE:
    return {32: HASH_TYPE.MD5, 40: HASH_TYPE.SHA1, 64: HASH_TYPE.SHA256, 128: HASH_TYPE.SHA512}[len(value)]


class hasher:

    def __init__(self, hasher: HASH_TYPE) -> None:
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
