"""
寻找Java以及相关处理
"""

__all__ = ["java_info", "java_manager"]

import collections.abc
import subprocess
import threading
import typing
import re
import os

from . import sysinfo
from . import config
from . import path as _path

from .verify import to_hash

from ..types import PmcccJavaNotFoundError


def select_java(
    version: int = 8, available: collections.abc.Iterable[int] | None = None
) -> list[int]:
    """
    根据传入的Java版本返回可选的Java版本
    """
    target: list[int] = []
    match version:
        case 8:
            target += [8, 9, 10, 11]
        case 16:
            target += [17, 16]
        case 17:
            target += [21, 17, 18, 19, 20, 22]
        case 21:
            target += [21, 22]
        case _:
            pass
    return [value for value in target if available is None or value in available]


class java_info:
    """
    Java版本信息
    """

    def __init__(
        self,
        path: str,
        version: str | None = None,
        arch: str | None = None,
        jdk: bool = False,
    ):
        """
        Java版本信息

        ---

        path: javaw/java程序
        """
        self.path = _path.format_abspath(path)
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
        return (
            f"{'jdk' if self.jdk else 'jre'}({self.version})[{self.arch}] <{self.path}>"
        )

    def __hash__(self) -> int:
        return to_hash(os.path.dirname(self.path))


class java_manager(config.config_base):
    """
    Java管理器
    """

    def __init__(
        self,
        path: collections.abc.Iterable[str] | None = None,
        info: sysinfo | None = None,
        selector: typing.Callable[[int, list[int]], list[int]] = select_java,
    ) -> None:
        self.info = sysinfo() if info is None else info
        self.java: dict[int, list[java_info]] = {}
        self.loaded: list[int] = []
        self.selector = selector
        (
            [self.add(value) for item in path if (value := self.check_java(item))]
            if path
            else None
        )

    def config_export(self) -> dict[str, typing.Any]:
        return {
            str(key): [
                {
                    "path": value.path,
                    "version": value.version,
                    "arch": value.arch,
                    "jdk": value.jdk,
                }
                for value in item
            ]
            for key, item in self.java.items()
        }

    def config_loads(self, data: dict[str, typing.Any]) -> None:
        for key, item in data.items():
            key = int(key)
            if key not in self.java:
                self.java[key] = []
            for value in item:
                self.add(
                    java_info(
                        value["path"], value["version"], value["arch"], value["jdk"]
                    )
                )

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
        if java.arch and java.arch != self.info.arch or hash(java) in self.loaded:
            return
        if java.major not in self.java:
            self.java[java.major] = [java]
        else:
            self.java[java.major].append(java)
        self.loaded.append(hash(java))

    def add_path(self, path: str) -> bool:
        """
        通过Java程序路径来进行添加
        """
        return self.add(info) is None if (info := self.check_java(path)) else False

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
        text = subprocess.run(
            (target, "-version"), capture_output=True, text=True
        ).stderr
        version = (
            version.group(1)
            if (
                version := re.search(
                    '(?i)\\b(?:java|openjdk)\\s+(?:version\\s+)?"?([0-9]+(?:\\.[0-9]+){0,2})',
                    text,
                )
            )
            else None
        )
        arch = arch.group(1) if (arch := re.search("(\\d{2})-Bit", text)) else None
        arch = "x86" if arch == "32" else f"x{arch}"
        return java_info(target, version, arch, jdk)

    def search(self, dirs: collections.abc.Iterable[str] | None = None) -> None:
        """
        通过文件夹找Java(非遍历)

        默认通过环境变量来找
        """
        threads: list[threading.Thread] = []
        if dirs is None:
            dirs = os.environ["PATH"].split(self.info.split)
        for path in dirs:
            if not os.path.isdir(path):
                continue
            if "bin" not in path and "bin" in os.listdir(path):
                path = os.path.join(path, "bin")

            def func():
                if ret := self.check_java(path):
                    self.add(ret)

            # 多线程查找
            threads.append(threading.Thread(target=func, daemon=True))
            threads[-1].start()
        for thread in threads:
            thread.join()

    def select_java(self, target: int | str) -> list[str]:
        """
        根据传入的Java版本返回可选的Java版本
        """
        ret = self.selector(int(target), list(self.java.keys()))
        if not ret:
            raise PmcccJavaNotFoundError
        return [info.path for value in ret for info in self.java[value]]
