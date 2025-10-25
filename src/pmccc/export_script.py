"""
导出为批处理
"""

__all__ = ["export_bat", "export_shell"]

import shlex

from . import version as _version


def export_bat(version: _version, java: str) -> str:
    """
    导出为bat
    """
    pass


def export_shell() -> str:
    """
    导出为shell
    """
    pass
