"""
日志发送器

包含自定义log4j2类,会开放一个服务器发日志,以及客户端类
"""

__all__ = ["logsender_log4j2", "logsender_client"]

import threading
import socket
import abc
import re

from ..process import log4j2 as _log4j2


class logsender_log4j2(_log4j2.log4j2_base):

    def __init__(
        self,
        ip: str = "localhost",
        port: int = 25590,
        onlymsg: bool = True,
        pattern: str | None = None,
        config: str | bool = True,
        info: type[_log4j2.loginfo] = _log4j2.loginfo,
    ) -> None:
        super().__init__(config, info)
        self.onlymsg = onlymsg
        self.pattern = pattern
        self.address = (ip, port)
        self.client: list[socket.socket] = []
        self.socket = socket.socket()

    def start(self) -> None:
        self.socket.bind(self.address)
        self.socket.listen(0)
        self.thread = threading.Thread(target=self.main, daemon=True)
        self.thread.start()

    def shutdown(self) -> None:
        try:
            self.thread.join(0)
        except TimeoutError:
            pass
        self.socket.close()

    def main(self) -> None:
        """
        服务端主逻辑
        """
        while True:
            self.client.append(self.socket.accept()[0])

    def user(self, user: socket.socket, text: bytes) -> None:
        """
        与客户端通信
        """
        try:
            user.sendall(text + b"\0")
        except:
            self.client.remove(user)

    def parse(self, line: str) -> None:
        if self.pattern and not re.search(self.pattern, line):
            return
        text = (
            self.split(line)[1].encode("utf-8")
            if self.onlymsg
            else line.encode("utf-8")
        )
        for user in self.client:
            threading.Thread(target=self.user, args=(user, text), daemon=True).start()


class logsender_client:

    def __init__(
        self, ip: str = "localhost", port: int = 25590, reconnect: int = 3
    ) -> None:
        self.thread = threading.Thread(target=self.main, daemon=True)
        self.socket = socket.socket()
        self.socket.settimeout(1)
        self.reconnect = reconnect
        self.address = (ip, port)

    def connect(self) -> None:
        self.socket.connect(self.address)
        if not self.thread.is_alive():
            self.thread.start()

    def disconnect(self) -> None:
        try:
            self.thread.join(0)
        except TimeoutError:
            pass
        self.socket.close()

    def main(self) -> None:
        data = b""
        while True:
            try:
                data += self.socket.recv(1024)
            except (OSError, ConnectionError, TimeoutError):
                # 要么断连了,要么规定时间内没有新消息
                try:
                    # 发送一下看看是否还在连接,反正服务端不处理客户端输入
                    self.socket.send(b"")
                    continue
                except (OSError, ConnectionError):
                    # 断连了
                    self.socket = socket.socket()
                    reconnect = self.reconnect
                    while reconnect != 0:
                        if reconnect > 0:
                            reconnect -= 1
                        try:
                            self.connect()
                            break
                        except (OSError, ConnectionError) as error:
                            if reconnect <= 0:
                                # 捕捉了异常又抛出去(
                                raise error
                    continue
            if data == b"":
                break
            if data.endswith(b"\0"):
                threading.Thread(
                    target=self.parse, args=(data[:-1].decode("utf-8"),), daemon=True
                ).start()
                data = b""

    @abc.abstractmethod
    def parse(self, text: str) -> None:
        pass
