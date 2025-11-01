"""
路径相关
"""

import os

__all__ = ["check_dir", "check_removeable"]


def check_dir(path: str, mkdir: bool = True) -> bool:
    """
    检查路径所在文件夹是否存在并创建文件夹
    """
    dirname = os.path.dirname(os.path.abspath(path))
    # 不考虑dirname指向文件的情况
    if os.path.isdir(dirname):
        return True
    if mkdir:
        os.makedirs(dirname)
    return False


def check_removeable(path: str) -> bool:
    """
    检查目录/文件是否能被删除
    """
    if os.path.isdir(path):
        for root, _, files in os.walk(path):
            if not any(os.access(value, os.W_OK) for value in [root, *(os.path.join(root, item) for item in files)]):
                return False
        return True
    else:
        return os.access(path, os.W_OK)
