"""
进程守护脚本

用法: <主进程pid> <子进程pid> [退出间隔]
"""

__all__ = ["add_daemon"]

import subprocess
import time
import sys
import os

import psutil


def main(pid_main: int, pid_sub: int, wait: int = 1):
    while psutil.pid_exists(pid_main):
        time.sleep(0.1)
    time.sleep(wait)
    if psutil.pid_exists(pid_sub):
        psutil.Process(pid_sub).terminate()


def add_daemon(pid_main: int, pid_sub: int, wait: int = 1) -> None:
    """
    添加进程守护
    """
    # 创建子进程并脱离主进程,以防变成僵尸进程
    if os.name == "nt":
        subprocess.Popen(
            (
                # 使用pythonw不会弹出控制台
                os.path.join(os.path.dirname(sys.executable), "pythonw"),
                __file__,
                str(pid_main),
                str(pid_sub),
                str(wait),
            ),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            creationflags=subprocess.DETACHED_PROCESS
            | subprocess.CREATE_NEW_PROCESS_GROUP,
            close_fds=True,
        )
    else:
        subprocess.Popen(
            (sys.executable, __file__, str(pid_main), str(pid_sub), str(wait)),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            start_new_session=True,
            close_fds=True,
        )


if __name__ == "__main__":
    argv = sys.argv[1:]
    length = len(argv)
    if length < 2 or not all(value.isdigit() for value in argv):
        # 传参错误
        exit(-1)
    main(
        int(argv[0]),
        int(argv[1]),
        int(argv[2]) if length > 2 and argv[2].isdecimal() else 1,
    )
