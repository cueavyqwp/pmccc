"""
校验相关
"""

__all__ = ["get_type", "to_hash", "hasher", "verify_hash", "verify_file"]

import hashlib
import typing

from ..types import HASH_TYPE, HASHER


def get_type(value: str) -> HASH_TYPE:
    """
    依据长度判断哈希类型(算法)
    """
    return {
        32: HASH_TYPE.MD5,
        40: HASH_TYPE.SHA1,
        64: HASH_TYPE.SHA256,
        128: HASH_TYPE.SHA512,
    }[len(value)]


def to_hash(obj: typing.Any) -> int:
    """
    把传入类型转为字符串然后返回字符串对应sha1
    """
    return int(hashlib.sha1(str(obj).encode("utf-8")).hexdigest(), 16)


class hasher:

    def __init__(self, hasher: HASH_TYPE) -> None:
        self.hash = HASHER[hasher]()

    def update(self, data: str | bytes) -> None:
        """
        更新数据
        """
        self.hash.update(data.encode() if isinstance(data, str) else data)

    def load(self, file: str) -> str:
        """
        从文件中加载(自动分片读取)
        """
        with open(file, "rb") as fp:
            for data in iter(lambda: fp.read(4096), b""):
                self.update(data)
        return self.hexdigest

    @property
    def hexdigest(self) -> str:
        """
        返回其对应十六进制
        """
        return self.hash.hexdigest()


class verify_hash(hasher):
    """
    用于校验哈希值
    """

    def __init__(self, value: str) -> None:
        super().__init__(get_type(value))
        self.value = value

    def check(self) -> bool:
        """
        校验两值是否相同
        """
        return self.hash.hexdigest() == self.value


class verify_file(hasher):
    """
    校验文件
    """

    def __init__(self, file: str, hasher: HASH_TYPE = HASH_TYPE.SHA1) -> None:
        super().__init__(hasher)
        self.load(file)

    def check(self, value: str) -> bool:
        """
        校验两值是否相同
        """
        return self.hash.hexdigest() == value
