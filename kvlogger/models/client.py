"""keyence機器と通信するクライアント"""
import enum
import socket
from typing import Tuple


class Status(enum.Flag):
    """機器接続状況"""

    NOT_CONNECTED = enum.auto()
    CONNECTED = enum.auto()
    RUN = enum.auto()
    ERROR = enum.auto()


class KVClient:
    """keyence機器と通信するクラス"""

    def __init__(self) -> None:
        """初期化処理"""

        self.status: Status = Status.NOT_CONNECTED
        # ip4, TCP使用
        self.client: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, address: Tuple[str, int], timeout: float = 2.0) -> None:
        """keyence機器と接続する

        Parameters
        ----------
        address: Tuple[str, int]
            IPアドレスとポート番号
        timeout: float default=10.0
            接続タイムアウト時間
        """

        self.client.settimeout(timeout)
        if self.status in Status.NOT_CONNECTED | Status.ERROR:
            try:
                self.client.connect_ex(address)
                self.status = Status.CONNECTED
            except socket.timeout as s_timeout:
                self.status = Status.NOT_CONNECTED
                self.disconnect()

                raise OSError('タイムアウトしました') from s_timeout

    def disconnect(self) -> None:
        """切断する"""

        self.client.close()
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.status = Status.NOT_CONNECTED
