"""メイン画面"""
import datetime as dt

from PySide6.QtCore import QTimer
from PySide6.QtGui import QIcon, QResizeEvent
from PySide6.QtWidgets import QMainWindow, QMessageBox

from kvlogger.views import icons, main_view_ui


class MainWindow(QMainWindow):
    """メイン画面"""

    def __init__(self, *args, **kwargs) -> None:
        """初期化処理"""

        super(MainWindow, self).__init__(*args, **kwargs)
        self.ui = main_view_ui.MainWindowUI()
        self.ui.setup_ui(self)

        self.ui.run_action.setDisabled(True)
        self.ui.stop_action.setDisabled(True)
        self.clock()

        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.clock)
        self.timer.start()

    def clock(self) -> None:
        """現在時刻表示"""

        now: str = dt.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        self.ui.clock_label.setText(now)

    def connected(self) -> None:
        """機器接続したときにアイコンを変更する"""

        self.ui.connect_action.setIcon(QIcon(icons.DISCONNECT_ICON))
        self.ui.connect_action.setText('Disconnect')
        self.ui.status_label.setText('Connected')
        QMessageBox.information(self, 'Information', '接続しました')

    def disconnected(self) -> None:
        """機器切断したときにアイコンを変更する"""

        self.ui.connect_action.setIcon(QIcon(icons.CONNECT_ICON))
        self.ui.connect_action.setText('Connect')
        self.ui.status_label.setText('Not connected')
        QMessageBox.information(self, 'Information', '切断しました')

    def error(self, ex: Exception) -> None:
        """エラー発生時の画面設定

        Parameters
        ----------
        ex: Exception
            エラー内容
        """

        QMessageBox.critical(self, 'Error', f"{ex}")
        self.ui.status_label.setText('Error')

    def ready(self) -> None:
        """測定可能時の画面設定"""

        self.ui.run_action.setEnabled(True)
        self.ui.status_label.setText('Ready')

    def resizeEvent(self, event: QResizeEvent) -> None:
        """画面サイズが変更されたとき発生するイベント
        テーブルサイズを調整する

        Parameters
        ----------
        event: QResizeEvent
            イベント信号
        """

        self.ui.current_table.set_stretch()

    def set(self) -> None:
        """測定設定後の画面変更"""

    def started(self) -> None:
        """測定開始後のアイコン表示変更"""

        self.ui.run_action.setDisabled(True)
        self.ui.stop_action.setEnabled(True)

    def stopped(self) -> None:
        """測定終了後のアイコン表示変更"""

        self.ui.run_action.setEnabled(True)
        self.ui.stop_action.setDisabled(True)


if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    win = MainWindow()
    win.ready()
    win.show()
    sys.exit(app.exec())
