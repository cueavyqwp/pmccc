"""
校验相关
"""

__all__ = ["get_type", "to_hash", "hasher", "verify_hash"]

import hashlib
import typing
import os

from ..types import HASH_TYPE, HASHER


def get_type(value: str) -> HASH_TYPE:
    return {32: HASH_TYPE.MD5, 40: HASH_TYPE.SHA1, 64: HASH_TYPE.SHA256, 128: HASH_TYPE.SHA512}[len(value)]


def to_hash(obj: typing.Any) -> int:
    """
    把传入类型转为字符串然后返回字符串对应sha1
    """
    return int(hashlib.sha1(str(obj).encode("utf-8")).hexdigest(), 16)


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
        for file in sorted((value for value in (os.path.join(path, item) for item in os.listdir(path)) if os.path.isfile(value) and (filter is None or filter in value))):
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
