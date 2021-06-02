"""メイン画面制御"""
from typing import List

import numpy as np
import pandas as pd
from PySide6.QtCore import Signal, Slot
from PySide6.QtGui import QResizeEvent
from PySide6.QtWidgets import QMainWindow

from kvlogger.models import settings
from kvlogger.views import main_view
from kvlogger.views import widget_items as wi


class MainWindow(QMainWindow):
    """メイン制御"""

    def __init__(self, *args, **kwargs) -> None:
        """初期化処理"""

        self.config = settings.InitConfig()

        super(MainWindow, self).__init__(*args, **kwargs)
        self.ui = main_view.MainWindowUI()
        self.ui.setup_ui(self)

        # テーブルモデル作成
        model: wi.CurrentValueModel = wi.CurrentValueModel(self.config.all_items_name)
        self.ui.current_table.setModel(model)

        for section in self.config.measure_sections:
            items: List[str] = self.config.get_section_items_name(section)
            unit: str = self.config.get_measure_section_unit(section)
            self.ui.add_tab(section, items, unit)

        self.connect_slot()

    def connect_slot(self) -> None:
        """スロット接続"""

    def resizeEvent(self, event: QResizeEvent) -> None:
        """画面サイズが変更されたとき発生するイベント
        テーブルサイズを調整する

        Parameters
        ----------
        event: QResizeEvent
            イベント信号
        """

        self.ui.current_table.set_stretch()


if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
