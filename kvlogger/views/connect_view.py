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

    def exec_dialog(self, address: Tuple[str, int]) -> Optional[Tuple[str, int]]:
        """ダイアログモーダル表示

        Parameters
        ----------
        address: Tuple[str, int]
            IPアドレスとポート番号
        """

        self.ui.ip_edit.setText(address[0])
        self.ui.port_edit.setText(str(address[1]))
        result = self.exec()

        if result == self.Accepted:
            return self.ui.ip_edit.text(), int(self.ui.port_edit.text())
