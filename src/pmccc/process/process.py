"""
自定义Popen类
"""

__all__ = ["popen"]

import subprocess
import threading
import typing
import atexit
import abc
import sys
import os

# 用于从命令行获取输入
if os.name == "nt":
    import msvcrt
    import time
else:
    import select

from ..utils import daemon as _daemon

from .log4j2 import log4j2_base

import charset_normalizer


class popen_base(subprocess.Popen[bytes]):
    """
    自定义Popen类
    """

    def __init__(
        self,
        args: list[typing.Any],
        cwd: str | None = None,
        output: bool = True,
        daemon: bool = True,
    ) -> None:
        self.output = output
        self.stdin: typing.IO[  # pyright: ignore[reportIncompatibleVariableOverride]
            bytes
        ]
        self.stdout: typing.IO[  # pyright: ignore[reportIncompatibleVariableOverride]
            bytes
        ]
        super().__init__(
            args,
            stdin=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdout=subprocess.PIPE,
            cwd=cwd,
        )
        self.parse_thread = threading.Thread(target=self.parse, daemon=True)
        self.parse_thread.start()
        if daemon:
            # 处理Ctrl-C等正常退出
            atexit.register(self.exit)
            # 主进程意外终止时兜底
            _daemon.add_daemon(os.getpid(), self.pid)

    def parse(self):
        """
        解析输出
        """
        for text in iter(self.stdout.readline, ""):
            encoding = charset_normalizer.detect(text)["encoding"]
            if encoding is None:
                encoding = "utf-8"
            text = text.decode(encoding, errors="replace")
            if self.parse_call(text) and self.output:
                sys.stdout.write(text)

    @abc.abstractmethod
    def parse_call(self, text: str) -> bool:
        """
        解析时调用,返回值决定是否输出
        """
        pass

    def exit(self) -> int:
        """
        中止并等待退出
        """
        self.terminate()
        return self.wait()

    def input_func(self) -> None:
        """
        非阻塞获取命令行输入
        """
        if os.name == "nt":
            buffer: list[str] = []
        while self.poll() is None:
            try:
                if os.name == "nt":
                    if msvcrt.kbhit():
                        char = msvcrt.getwch()
                        match char:
                            case "\r":
                                self.input("".join(buffer))
                                buffer.clear()
                                sys.stdout.write("\n")
                                sys.stdout.flush()
                            case "\x08":
                                if buffer:
                                    del buffer[-1]
                                    sys.stdout.write("\b \b")
                                    sys.stdout.flush()
                            case _:
                                buffer.append(char)
                                sys.stdout.write(char)
                                sys.stdout.flush()
                    else:
                        time.sleep(0.05)
                elif select.select([sys.stdin], [], [], 0.05)[0]:
                    if text := sys.stdin.readline():
                        self.input(text, end="")
            except (KeyboardInterrupt, EOFError):
                self.stdin.close()
                break

    def input(
        self,
        *text: str,
        sep: str = "\n",
        end: str = "\n",
        autoflush: bool = True,
        encoding: str = "utf-8",
    ) -> None:
        """
        向stdin插入文本
        """
        if self.stdin:
            self.stdin.write((sep.join(text) + end).encode(encoding, errors="replace"))
            if autoflush and (end.endswith("\n") or text[-1].endswith("\n")):
                self.stdin.flush()

    def wait_input(self) -> int:
        """
        等待退出,并支持输入
        """
        thread = threading.Thread(target=self.input_func, daemon=True)
        thread.start()
        try:
            thread.join()
        except (KeyboardInterrupt, EOFError):
            pass
        return self.exit()


class popen(popen_base):

    def __init__(
        self,
        args: list[typing.Any],
        cwd: str | None = None,
        output: bool = True,
        log4j2: log4j2_base | None = None,
        force_utf8: bool = True,
        daemon: bool = True,
    ) -> None:
        self.log4j2 = log4j2
        if log4j2 is not None and log4j2.config is not None:
            args.insert(1, f"-Dlog4j.configurationFile={log4j2.config}")
            log4j2.popen = self
        if force_utf8 and "-Dfile.encoding=UTF-8" not in args:
            args.insert(1, "-Dfile.encoding=UTF-8")
        # 获取游戏所在目录
        if cwd is None:
            for index in range(len(args)):
                if args[index] == "--gameDir":
                    cwd = str(args[index + 1])
                    break
        super().__init__(args, cwd, output, daemon)

    def parse_call(self, text: str) -> bool:
        if self.log4j2:
            self.log4j2.parse_call(text)
            if not self.log4j2.is_output(text):
                # 非应输出内容,跳过输出
                return False
        return True
