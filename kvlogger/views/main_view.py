"""メイン画面UI"""
from typing import List, Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QHBoxLayout, QLabel, QMainWindow,QMenuBar,
                               QSplitter,
                               QStatusBar, QTabWidget, QToolBar,
                               QWidget)

from kvlogger.views import style
from kvlogger.views import widget_items as wi


class MainWindowUI:
    """UI"""

    def setup_ui(self, main_window: QMainWindow, width: int = 1200) -> None:
        """UIを設定する
        Parameters
        ----------
        main_window: QtWidgets.QMainWindow
            ウィジットを設置する画面
        width: int default=1600
            画面幅
        """

        height: int = int(width * 5 / 8)

        main_window.resize(width, height)
        main_window.setWindowTitle('KV Logger')

        font = QFont()
        font.setPointSize(12)
        main_window.setFont(font)

        self.make_widgets(main_window)
        self.make_layouts()
        self.set_layout(main_window)
        self.set_menubar(main_window)
        self.set_statusbar(main_window)
        self.set_toolber(main_window)

    def add_tab(self, section: str, parameter: List[str], unit: Optional[str] = None) -> None:
        """

        Parameters
        ----------
        section: str
            セクション名. タブに表示される.
        parameter:str
            パラメタ.
        unit: Optional[str] default=None
            パラメタの単位
        """

        if unit is not None:
            section += ' [' + unit + ']'
        widget: wi.SectionMeasureWidget = wi.SectionMeasureWidget(section, parameter)
        self.tab.addTab(widget, section)

    def make_widgets(self, window: QMainWindow) -> None:
        """UI作成"""

        self.central_widget = QWidget(window)
        self.splitter = QSplitter(Qt.Orientation.Vertical)

        self.current_table = wi.StretchTableView()
        self.tab = QTabWidget()
        self.inside_tab: List[wi.SectionMeasureWidget] = []

        # statusbar用
        self.stime_label = QLabel('11111111')

    def make_layouts(self) -> None:
        """レイアウト作成"""

        self.main_layout = QHBoxLayout()

    def set_layout(self, window: QMainWindow) -> None:
        """レイアウト設定"""

        window.setCentralWidget(self.central_widget)
        self.central_widget.setLayout(self.main_layout)
        self.main_layout.addWidget(self.splitter)

        self.splitter.addWidget(self.current_table)
        self.splitter.addWidget(self.tab)

        self.splitter.setSizes([self.splitter.size().width() * 0.1,
                                self.splitter.size().width() * 0.9])

        # TODO テスト用
        self.add_tab('test', ['a', 'b'], 'T')

    def set_menubar(self, window: QMainWindow) -> None:
        """メニューバーセット"""

        self.menubar = QMenuBar()  # Make a menu without parent.
        self.menubar.setToolTip('ツールバーの表示/非表示変更<br>ショートカット：Ctrl V')
        window.setMenuBar(self.menubar)

        self.view_menu = self.menubar.addMenu('&View')

    def set_statusbar(self, window: QMainWindow) -> None:
        """ステータスバーセット"""

        self.statusbar = QStatusBar()
        window.setStatusBar(self.statusbar)

        self.statusbar.addPermanentWidget(QLabel('Start time: '))
        self.statusbar.addPermanentWidget(self.stime_label)

    def set_toolber(self, window: QMainWindow) -> None:
        """ツールバーセット"""

        self.toolbar = QToolBar()
        self.toolbar.setWindowTitle("ToolBar")
        window.addToolBar(self.toolbar)
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)


if __name__ == '__main__':
    import sys

    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    win = QMainWindow()
    ui = MainWindowUI()
    ui.setup_ui(win)
    win.show()

    sys.exit(app.exec())
