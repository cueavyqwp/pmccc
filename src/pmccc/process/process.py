"""
自定义Popen类
"""

__all__ = ["popen"]

import subprocess
import threading
import typing
import atexit
import sys
import os

# 用于从命令行获取输入
if os.name == "nt":
    import msvcrt
    import time
else:
    import select

from .log4j2 import log4j2_base


class popen(subprocess.Popen[bytes]):
    """
    自定义Popen类
    """

    def __init__(
        self,
        args: list[typing.Any],
        cwd: str | None = None,
        output: bool = True,
        log4j2: log4j2_base | None = None,
        ignore_parse_error: bool = True,
        force_utf8: bool = True,
        daemon: bool = True,
    ) -> None:
        self.ignore_parse_error = ignore_parse_error
        self.log4j2 = log4j2
        self.output = output
        if log4j2 is not None:
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
            atexit.register(self.exit)

    def parse(self):
        """
        分出每行并调用log4j2类中的parse
        """
        line: list[str] = []
        for text in iter(self.stdout.readline, ""):
            text = text.decode("utf-8", errors="replace")
            if text == "\t\n":
                value = "".join(line)
                self.parse_call(value)
                line = []
                continue
            elif self.output:
                sys.stdout.write(text)
            if self.log4j2 is None:
                continue
            if self.log4j2.is_line(text):
                line = [text]
            elif line:
                line.append(text)

    def parse_call(self, line: str) -> None:
        """
        调用log4j2类中的parse
        """
        if self.log4j2 is None:
            return
        try:
            self.log4j2.parse(line)
        except Exception as error:
            if not self.ignore_parse_error:
                raise error

    def exit(self) -> int:
        """
        中止并等待退出
        """
        self.terminate()
        return self.wait()

    def input(self) -> None:
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
                                self.stdin.write(
                                    ("".join(buffer) + "\n").encode("utf-8")
                                )
                                self.stdin.flush()
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
                elif select.select([sys.stdin], [], [], 0.1)[0]:
                    if text := sys.stdin.readline():
                        self.stdin.write(text.encode("utf-8"))
                        self.stdin.flush()
            except (KeyboardInterrupt, EOFError):
                self.stdin.close()
                break

    def wait_input(self) -> int:
        """
        等待退出,并支持输入
        """
        thread = threading.Thread(target=self.input, daemon=True)
        thread.start()
        try:
            thread.join()
        except (KeyboardInterrupt, EOFError):
            pass
        return self.exit()
