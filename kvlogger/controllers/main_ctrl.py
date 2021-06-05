"""ソフトのメイン制御"""
from typing import Callable, List, Optional, Tuple

from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QApplication, QDialog, QMessageBox

from kvlogger.models import model
from kvlogger.views import (connect_view, main_view, widget_items as wi)


class MainController:
    """メインコントローラ"""

    def __init__(self, app: QApplication) -> None:
        """初期化処理

        Parameters
        ----------
        app: QApplication
            イベント監視オブジェクト
        """

        self.app = app
        self.model = model.Model()
        self.view = main_view.MainWindow()
        # UIへアクセスする用のショートカット
        self.ui = self.view.ui

        # テーブルモデル作成
        table_model: wi.CurrentValueModel = wi.CurrentValueModel(self.model.config.all_items_name)
        self.ui.current_table.setModel(table_model)
        # tab
        for section in self.model.config.measure_sections:
            items: List[str] = self.model.config.get_section_items_name(section)
            unit: str = self.model.config.get_measure_section_unit(section)
            self.ui.add_tab(section, items, unit)

        self.connect_slot()

    def connect_slot(self) -> None:
        """uiイベントとスロット接続"""

        self.ui.connect_action.triggered.connect(self.connect_kv)

    @Slot()
    def connect_kv(self) -> None:
        """keyenceデバイスと接続する"""

        dialog = connect_view.ConnectDialog()
        result: Optional[Tuple[str, int]] = dialog.exec_dialog(self.model.config.server)

        if result is None:
            return

        try:
            self.model.client.connect(result)
            self.switch_slot(self.ui.connect_action.triggered, self.disconnect_kv)
            self.view.connected()
        except OSError as ex:
            self.view.error(ex)

    @Slot()
    def disconnect_kv(self) -> None:
        """keyenceデバイスとの接続を切る"""

        buttons = QMessageBox.Yes | QMessageBox.No
        result = QMessageBox.information(self.view, 'Information', '切断しますか',
                                         buttons, QMessageBox.No)
        if result == QMessageBox.Yes:
            self.model.client.disconnect()
            self.switch_slot(self.ui.connect_action.triggered, self.connect_kv)
            self.view.disconnected()

    def start(self) -> None:
        """ソフト立上"""

        self.view.show()

    @staticmethod
    def switch_slot(signal: Signal, new: Callable) -> None:
        """シグナルのスロット切り替え

        Parameters
        ----------
        signal: Signal
            スロットを切り替えするシグナル
        new: Callable
            新しく接続するシグナル
        """

        signal.disconnect()
        signal.connect(new)
