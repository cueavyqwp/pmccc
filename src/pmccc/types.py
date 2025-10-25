"""
pmccc自定义的类型
"""

__all__ = ["HASH_TYPE", "HASHER", "PmcccException"]

import hashlib
import typing
import enum

# 校验相关


class HASH_TYPE(enum.Enum):

    SHA1 = 0
    SHA256 = 1
    SHA512 = 2
    MD5 = 3


HASHER = {
    HASH_TYPE.SHA1: hashlib.sha1,
    HASH_TYPE.SHA256: hashlib.sha256,
    HASH_TYPE.SHA512: hashlib.sha512,
    HASH_TYPE.MD5: hashlib.md5
}

# 自定义异常


class PmcccException(Exception):
    """
    pmccc异常基类
    """

    def __init__(self, *args: object) -> None:
        """
        pmccc异常
        """
        super().__init__(*args)
