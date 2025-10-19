"""
寻找java以及相关处理
"""

__all__ = ["java_info", "java_manager"]

import subprocess
import typing
import re
import os

from . import info as _info


class java_info:

    def __init__(self, path: str, version: typing.Optional[str] = None, arch: typing.Optional[str] = None, jdk: bool = False):
        """
        Java版本信息

        ---

        path: javaw/java程序
        """
        self.path = os.path.normpath(path)
        self.version = version
        self.arch = arch
        self.jdk = jdk

    @property
    def major(self) -> int:
        """
        获取大版本号
        """
        if self.version is None:
            return 8
        split = self.version.split(".")
        if split[0] == "1":
            return 8
        else:
            return int(split[0])

    def __str__(self) -> str:
        return f"{'jdk' if self.jdk else 'jre'}({self.version})[{self.arch}] <{self.path}>"

    def __hash__(self) -> int:
        return str(self).__hash__()


class java_manager:
    """
    Java管理器
    """

    def __init__(self, path: typing.Optional[list[str]] = None, info: typing.Optional[_info] = None) -> None:
        self.info = _info() if info is None else info
        self.java: dict[int, list[java_info]] = {}
        [self.add(value) for item in path if (
            value := self.check_java(item))] if path else None

    def __str__(self) -> str:
        ret: list[str] = []
        for key, value in self.java.items():
            ret.append(f"JDK/JRE-{key}:")
            for java in value:
                ret.append(f"  {java}")
        return "\n".join(ret)

    def add(self, java: java_info) -> None:
        """
        把Java信息加入管理器
        """
        # 不加载位数不匹配的jre/jdk
        if java.arch and java.arch != self.info.arch:
            return
        if java.major not in self.java:
            self.java[java.major] = [java]
        else:
            self.java[java.major].append(java)

    def check_java(self, path: str) -> java_info | None:
        """
        传入bin目录,获取Java信息
        """
        if not os.path.isdir(path):
            return
        target = ""
        version = None
        arch = None
        jdk = False
        for item in os.listdir(path):
            file = os.path.join(path, item)
            if os.path.isdir(file):
                continue
            name = os.path.splitext(item)[0]
            if name == "javaw":
                target = item
            elif not target.startswith("javaw") and name == "java":
                target = item
            elif name == "javac":
                jdk = True
        if not target:
            return
        target = os.path.join(path, target)
        text = subprocess.run((target, "-version"),
                              capture_output=True, text=True).stderr
        version = version.group(1) if (version := re.search(
            "(?i)\\b(?:java|openjdk)\\s+(?:version\\s+)?\"?([0-9]+(?:\\.[0-9]+){0,2})", text)) else None
        arch = arch.group(1) if (arch := re.search(
            "(\\d{2})-Bit", text)) else None
        arch = "x86" if arch == "32" else f"x{arch}"
        return java_info(target, version, arch, jdk)

    def search(self, dirs: typing.Optional[list[str]] = None) -> None:
        """
        通过文件夹找Java(非遍历)

        默认通过环境变量来找
        """
        if dirs is None:
            dirs = os.environ["PATH"].split(self.info.split)
        # 防止重复加载
        loaded: set[int] = set()
        for path in dirs:
            if not os.path.isdir(path):
                continue
            if "bin" not in path and "bin" in os.listdir(path):
                path = os.path.join(path, "bin")
            if (ret := self.check_java(path)):
                if (hash := ret.__hash__()) in loaded:
                    continue
                self.add(ret)
                loaded.add(hash)
