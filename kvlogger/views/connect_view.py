"""接続ダイアログ"""
from typing import Optional, Tuple

from PySide6.QtWidgets import QDialog

from kvlogger.views import connect_view_ui


class ConnectDialog(QDialog):
    """接続ダイアログ"""

    def __init__(self, *args, **kwargs) -> None:
        """初期化処理"""

        super(ConnectDialog, self).__init__(*args, **kwargs)
        self.ui = connect_view_ui.ConnectDialogUI()
        self.ui.set_up(self)

    def exec_dialog(self, ip: str, port: int) -> Optional[Tuple[str, int]]:
        """ダイアログモーダル表示

        Parameters
        ----------
        ip: str
            IPアドレス
        port: int
            ポート番号
        """

        self.ui.ip_edit.setText(ip)
        self.ui.port_edit.setText(str(port))
        result = self.exec()

        if result == self.Accepted:
            return self.ui.ip_edit.text(), int(self.ui.port_edit.text())
