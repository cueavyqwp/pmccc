"""
用于判断规则
"""

__all__ = ["check"]

import typing
import re

from .info import sysinfo


def check(
    rules: list[dict[str, typing.Any]],
    features: typing.Optional[dict[str, bool]] = None,
    info: sysinfo | None = None,
) -> bool:
    """
    传入规则列表,然后检查是否启用
    """
    ret = False
    if info is None:
        info = sysinfo()
    for rule in rules:
        if "features" in rule:
            if features is not None and all(
                key in features and features[key] == value
                for key, value in rule["features"].items()
            ):
                ret = True
            else:
                return False
        if "os" in rule:
            if "name" in rule["os"] and rule["os"]["name"] != info.os:
                continue
            if "arch" in rule["os"] and rule["os"]["arch"] != info.arch:
                continue
            if (
                "version" in rule["os"]
                and re.match(rule["os"]["version"], info.os_version) is None
            ):
                continue
        ret = {"allow": True, "disallow": False}.get(rule["action"], False)
    return ret
