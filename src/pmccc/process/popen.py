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

if os.name == "nt":
    import msvcrt
    import time
else:
    import select

from .log4j2 import log4j2 as _log4j2


class popen(subprocess.Popen[str]):
    """
    自定义Popen类
    """

    def __init__(self, args: list[typing.Any], cwd: typing.Optional[str] = None, log4j2: typing.Optional[_log4j2] = None, ignore_parse_error: bool = True, daemon: bool = True) -> None:
        self.ignore_parse_error = ignore_parse_error
        self.log4j2 = log4j2
        if log4j2 is not None:
            args.insert(1, f"-Dlog4j.configurationFile={log4j2.config}")
        # 获取游戏所在目录
        if cwd is None:
            for index in range(len(args)):
                if args[index] == "--gameDir":
                    cwd = str(args[index+1])
                    break
        self.stdin: typing.IO[str]  # type: ignore
        self.stdout: typing.IO[str]  # type: ignore
        super().__init__(args, stdin=subprocess.PIPE, stderr=subprocess.STDOUT,
                         stdout=None if log4j2 is None else subprocess.PIPE,  encoding="utf-8", text=True, cwd=cwd)
        self.parse_thread = threading.Thread(
            target=self.parse, daemon=True)
        self.parse_thread.start()
        if daemon:
            atexit.register(self.exit)

    def parse(self):
        """
        分出每行并调用log4j2类中的parse
        """
        if self.log4j2 is None:
            return
        line: list[str] = []
        for text in iter(self.stdout.readline, ""):
            if text == "\t\n":
                self.parse_call("".join(line))
                line = []
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
        self.terminate()
        return self.wait()

    def input(self) -> None:
        if os.name == "nt":
            buffer: list[str] = []
        while self.poll() is None:
            try:
                if os.name == "nt":
                    if msvcrt.kbhit():
                        char = msvcrt.getwch()
                        match char:
                            case "\r":
                                self.stdin.write("".join(buffer) + "\n")
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
                    text = sys.stdin.readline()
                    if text:
                        self.stdin.write(text)
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
