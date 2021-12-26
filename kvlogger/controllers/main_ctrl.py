"""ソフトのメイン制御"""
from typing import Callable, List, Optional, Tuple

from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QApplication, QMessageBox

from kvlogger.models import model
from kvlogger.views import (connect_view as cv,
                            main_view as mv,
                            settings_view as sv,
                            widget_items as wi)


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
        self.view = mv.MainWindow(self.model.configs.label_measurement_items, 100)
        # UIへアクセスする用のショートカット
        self.ui = self.view.ui

        # テーブルモデル作成
        table_model: wi.CurrentValueModel = wi.CurrentValueModel(self.model.configs.measure_name_items)
        self.ui.values_table.setModel(table_model)

        self.connect_slot()

    def connect_slot(self) -> None:
        """uiイベントとスロット接続"""

        self.ui.connect_action.triggered.connect(self.connect_kv)
        self.ui.settings_action.triggered.connect(self.settings)

    @Slot()
    def connect_kv(self) -> None:
        """keyenceデバイスと接続する"""

        dialog = cv.ConnectDialog()
        result: Optional[Tuple[str, int]] = dialog.exec_dialog(self.model.configs.server)

        if result is None:
            return

        try:
            self.model.client.connect(result)
        except OSError as ex:
            self.view.error(ex)
            return

        self.switch_slot(self.ui.connect_action.triggered, self.disconnect_kv)
        self.view.connected()
        if self.model.settings.status == model.settings.Status.SET:
            self.view.ready()

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

    @Slot()
    def settings(self) -> None:
        """測定設定"""

        units = [unit.value for unit in model.settings.Unit]
        dialog = sv.SettingsDialog(units, self.model.settings.interval_unit)

        now_settings = (self.model.settings.save_dir,
                        self.model.settings.interval_value,
                        self.model.settings.interval_unit,
                        self.model.settings.data_point,
                        )

        result: Optional[Tuple[str, str, float, str, int]] = dialog.exec_dialog(*now_settings)

        if result is None:
            return
        try:
            self.model.settings.update(result)
            self.model.settings.status = model.settings.Status.SET
        except model.settings.DirectoryExistsError as ex:
            self.model.settings.status = model.settings.Status.NOT_SET
            self.view.error(ex)
            return

        self.view.set_settings()
        if self.model.client.status == model.client.Status.CONNECTED:
            self.view.ready()

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


if __name__ == '__main__':
    import sys

    import numpy as np
    import qdarktheme
    import pyqtgraph as pg

    app = QApplication(sys.argv)
    app.setStyleSheet(qdarktheme.load_stylesheet())

    controller = MainController(app)


    def update2():
        l = []
        for i in range(14):
            l.append(np.random.normal())

        controller.view.ui.center_widget.plot.set_data(l)


    def update3():
        l = []
        for i in range(14):
            l.append(np.random.normal())

        controller.view.ui.center_widget.plot.set_data_maxlen(l)


    def switch():
        timer.timeout.disconnect()
        timer.timeout.connect(update3)


    controller.view.ui.center_widget.plot.changedPlotMethod.connect(switch)

    controller.start()

    timer = pg.QtCore.QTimer()
    timer.timeout.connect(update2)
    timer.start(1000)

    sys.exit(app.exec())
