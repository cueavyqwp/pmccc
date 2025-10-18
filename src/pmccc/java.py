"""
寻找java以及相关处理
"""

import subprocess
import typing
import re
import os

from . import info as _info


class java_info:

    def __init__(self, path: str, version: typing.Optional[str] = None, arch: typing.Optional[str] = None, jdk: bool = False):
        self.path = os.path.normpath(path)
        self.version = version
        self.arch = arch
        self.jdk = jdk

    @property
    def major(self) -> int:
        if self.version is None:
            return 8
        split = self.version.split(".")
        if split[0] == "1":
            return 8
        else:
            return int(split[0])

    def __str__(self) -> str:
        return f"{'jdk' if self.jdk else 'jre'}({self.version}) {self.arch} <{self.path}>"

    def __hash__(self) -> int:
        return str(self).__hash__()


class java_manager:

    def __init__(self, path: typing.Optional[list[str]] = None, info: typing.Optional[_info.info] = None) -> None:
        self.info = _info.info() if info is None else info
        self.java: dict[int, list[java_info]] = {}
        [self.add(value) for item in path if (
            value := self.check_java(item))] if path else None

    def add(self, java: java_info) -> None:
        print(java)
        if java.major not in self.java:
            self.java[java.major] = [java]
        else:
            self.java[java.major].append(java)

    def check_java(self, path: str) -> java_info | None:
        if not os.path.isdir(path):
            return
        target = ""
        version = None
        arch = None
        jdk = False
        for name in os.listdir(path):
            file = os.path.join(path, name)
            if os.path.isdir(file):
                continue
            name = os.path.splitext(name)[0]
            if name == "javaw":
                target = "javaw"
            elif target != "javaw" and name == "java":
                target = "java"
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

    def search(self) -> None:
        loaded: set[int] = set()
        for path in os.environ["PATH"].split(self.info.split):
            if not os.path.isdir(path):
                continue
            if "bin" not in path and "bin" in os.listdir(path):
                path = os.path.join(path, "bin")
            if (ret := self.check_java(path)):
                if (hash := ret.__hash__()) in loaded:
                    continue
                self.add(ret)
                loaded.add(hash)
