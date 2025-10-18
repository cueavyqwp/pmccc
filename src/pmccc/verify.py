"""
校验类
"""

__all__ = ["verify"]

import hashlib
import typing


class verify:

    def __init__(self, value: str, type: typing.Literal["sha1", "sha256", "sha512", "md5"]) -> None:
        """
        用于校验文件

        ---

        value: 哈希值/MD5
        """
        self.value = value
        self.hash = {"sha1": hashlib.sha1, "sha256": hashlib.sha256,
                     "sha512": hashlib.sha512, "md5": hashlib.md5}.get(type, hashlib.sha1)()

    def update(self, data: str | bytes) -> "verify":
        self.hash.update(data.encode() if isinstance(data, str) else data)
        return self

    def hexdigest(self) -> str:
        return self.hash.hexdigest()

    def check(self) -> bool:
        return self.hash.hexdigest() == self.value
