"""
对MC服务端RCON协议的支持
"""

__all__ = [
    "SERVERDATA_AUTH",
    "SERVERDATA_EXECCOMMAND",
    "SERVERDATA_AUTH_RESPONSE",
    "SERVERDATA_RESPONSE_VALUE",
    "rcon_client",
]

import threading
import typing
import socket
import struct
import queue

SERVERDATA_AUTH = 3
SERVERDATA_EXECCOMMAND = 2
SERVERDATA_AUTH_RESPONSE = 2
SERVERDATA_RESPONSE_VALUE = 0


class rcon_client:
    """
    RCON客户端
    """

    def __init__(
        self,
        server: str = "127.0.0.1",
        port: int = 25575,
        password: str = "",
        reconnect: int = 3,
    ) -> None:
        self.reconnect = reconnect
        self.password = password
        self.server = server
        self.port = port
        self.lastsend = 0.0
        self.lock = threading.Lock()
        self.socket = socket.socket()
        self.event = threading.Event()
        self.thread = threading.Thread(target=self.recv_func, daemon=True)
        self.queue: queue.Queue[
            tuple[str, typing.Callable[[str], typing.Any] | None]
        ] = queue.Queue()
        self.socket.settimeout(30)
        self.thread.start()

    @property
    def ok(self) -> bool:
        """
        是否处于连接状态
        """
        try:
            timeout = self.socket.gettimeout()
            self.socket.settimeout(0)
            try:
                data = self.socket.recv(1, socket.MSG_PEEK)
                return data != b""
            except BlockingIOError:
                return True
            finally:
                self.socket.settimeout(timeout)
        except:
            return False

    def __enter__(self) -> "rcon_client":
        self.ensure_connect()
        return self

    def __exit__(self, *_) -> None:
        try:
            self.disconnect()
        except:
            pass

    def connect(self) -> int | bool:
        """
        建立socket连接,成功时返回True
        """
        try:
            self.socket.connect((self.server, self.port))
        except OSError as e:
            ret = e.errno
            return -1 if ret is None else ret
        self.send_packet(0, SERVERDATA_AUTH, self.password, False)
        req_id, p_type, _ = self.recv_packet(False)
        if p_type != SERVERDATA_AUTH_RESPONSE or req_id != 0:
            return -2
        return True

    def disconnect(self) -> None:
        """
        关闭socket连接
        """
        self.event.set()
        while not self.queue.empty():
            self.queue.get(False)
        self.socket.close()

    def ensure_connect(self) -> None:
        """
        确保处于连接状态
        """
        if self.ok:
            return
        self.socket = socket.socket()
        reconnect = self.reconnect
        with self.lock:
            ret = self.connect()
            while (not self.ok) and (reconnect != 0):
                if (ret := self.connect()) is True:
                    break
                if reconnect > 0:
                    reconnect -= 1
            if ret is not True:
                raise ConnectionError(ret)

    def command(self, command: str) -> str:
        """
        发送命令
        """
        self.send_packet(0, SERVERDATA_EXECCOMMAND, command)
        return self.recv_packet()[2]

    def command_call(
        self, command: str, func: typing.Callable[[str], typing.Any] | None = None
    ) -> None:
        """
        将函数添加进等待列表中,得到回复时调用函数
        """
        self.queue.put((command, func))

    def say(self, msg: str) -> None:
        """
        执行/say,并且能够处理换行
        """
        for line in msg.splitlines():
            self.command(f"say {line}")

    def recv_func(self) -> None:
        while not self.event.is_set():
            try:
                command, func = self.queue.get(timeout=0.1)
            except queue.Empty:
                continue
            with self.lock:
                try:
                    ret = self.command(command)
                except Exception as e:
                    ret = f"Python Error: {repr(e)}"
                if func:
                    func(ret)

    def read(self, length: int, ensure_connect: bool = True) -> bytes:
        if ensure_connect:
            self.ensure_connect()
        data = b""
        while len(data) < length:
            chunk = self.socket.recv(length - len(data))
            if chunk == b"":
                raise ConnectionError
            data += chunk
        return data

    def send_packet(
        self, req_id: int, p_type: int, body: str, ensure_connect: bool = True
    ):
        if ensure_connect:
            self.ensure_connect()
        data = body.encode("utf8") + b"\x00\x00"
        length = len(data) + 8
        packet = struct.pack("<iii", length, req_id, p_type) + data
        self.socket.sendall(packet)

    def recv_packet(self, ensure_connect: bool = True) -> tuple[int, int, str]:
        length = struct.unpack("<i", self.read(4, ensure_connect))[0]
        data = self.read(length, ensure_connect)
        req_id, p_type = struct.unpack("<ii", data[:8])
        body = data[8:-2].decode("utf-8")
        return req_id, p_type, body
