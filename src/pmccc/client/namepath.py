"""
namepath类
"""

__all__ = ["name"]

import os


class name:
    """
    name路径
    """

    def __init__(self, *name: str) -> None:
        split = ":".join(name).split(":")
        match len(split):
            case 3:
                self.package, self.name, self.version = split
                self.platform = ""
            case 4:
                self.package, self.name, self.version, self.platform = split
            case _:
                raise SyntaxError

    def __str__(self) -> str:
        key = self.get_key()
        if self.platform:
            key += f":{self.platform}"
        return key

    def __eq__(self, value: object) -> bool:
        """
        比较两namepath,忽略版本
        """
        if isinstance(value, "name"):
            return self.get_key() == value.get_key()
        else:
            return False

    def __or__(self, value: "name") -> "name":
        """
        返回版本号新的那个
        """
        return value if self.compare(self.version, value.version) else self

    def get_file(self) -> str:
        """
        获取库jar文件名
        """
        return f"{self.name}-{self.version}{f'-{self.platform}' if self.platform else ''}.jar"

    def get_path(self) -> str:
        """
        把split转为相对路径
        """
        return os.path.join(
            *self.package.split("."),
            self.name,
            self.version,
            self.get_file(),
        )

    def get_key(self) -> str:
        """
        获取不带版本的namepath
        """
        ret = ":".join((self.package, self.name))
        if self.platform:
            ret += f":{self.platform}"
        return ret

    def compare(self, first: str, second: str) -> bool:
        """
        比较版本号a >= b
        """
        split_first = [int(num) for num in first.split(".") if num.isdigit()]
        split_second = [int(num) for num in second.split(".") if num.isdigit()]
        len_first = len(split_first)
        len_second = len(split_second)
        if len_first > len_second:
            split_second += [0] * (len_first - len_second)
        else:
            split_first += [0] * (len_second - len_first)
        for numf, nums in zip(split_first, split_second):
            if numf >= nums:
                return True
        return False
