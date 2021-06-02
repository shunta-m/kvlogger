"""接続ダイアログ制御"""
from typing import Any

from PySide6.QtCore import Signal, Slot
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QDialog

from kvlogger.views import connect_view


class ConnectDialog(QDialog):
    """接続ダイアログ制御"""

    def __init__(self, *args, **kwargs) -> None:
        """初期化処理"""

        super(ConnectDialog, self).__init__(*args, **kwargs)
        self.ui = connect_view.ConnectDialogUI()
        self.ui.set_up(self)

    def closeEvent(self, arg__1: QCloseEvent) -> int:
        return 1
