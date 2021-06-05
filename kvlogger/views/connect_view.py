"""接続ダイアログ"""
from PySide6.QtWidgets import QDialog

from kvlogger.views import connect_view_ui


class ConnectDialog(QDialog):
    """接続ダイアログ"""

    def __init__(self, *args, **kwargs) -> None:
        """初期化処理"""

        super(ConnectDialog, self).__init__(*args, **kwargs)
        self.ui = connect_view_ui.ConnectDialogUI()
        self.ui.set_up(self)
