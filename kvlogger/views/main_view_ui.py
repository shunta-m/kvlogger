"""メイン画面UI"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QFont, QIcon
from PySide6.QtWidgets import (QHBoxLayout, QLabel, QMainWindow, QMenuBar, QTextEdit,
                               QSplitter, QStatusBar, QToolBar, QWidget)

from kvlogger.views import icons
from kvlogger.views import widget_items as wi


class MainWindowUI:
    """UI"""

    def setup_ui(self, main_window: QMainWindow, width: int = 1400) -> None:
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
        self.set_statusbar(main_window)
        self.set_toolber(main_window)
        self.set_menubar(main_window)

    def make_widgets(self, window: QMainWindow) -> None:
        """UI作成"""

        self.central_widget = QWidget(window)
        self.splitter = QSplitter(Qt.Orientation.Vertical)

        self.values_table = wi.StretchTableView()
        self.plot = wi.CentralWidget({'test': [f"test{i}" for i in range(2)], 'test2': [f"test2_{i}" for i in range(5)],
                                      'tes3': [f"test3_{i}" for i in range(2)],
                                      'test4': [f"test4_{i}" for i in range(5)]})
        self.log_txt_edit = QTextEdit()

        # statusbar用
        self.connect_status_label = QLabel('未接続')
        self.settings_status_label = QLabel('未設定')
        self.stime_label = QLabel('11111111')
        self.clock_label = QLabel('')

    def make_layouts(self) -> None:
        """レイアウト作成"""

        self.main_layout = QHBoxLayout()

    def set_layout(self, window: QMainWindow) -> None:
        """レイアウト設定"""

        window.setCentralWidget(self.central_widget)
        self.central_widget.setLayout(self.main_layout)
        self.main_layout.addWidget(self.splitter)

        self.splitter.addWidget(self.values_table)
        self.splitter.addWidget(self.plot)
        self.splitter.addWidget(self.log_txt_edit)

        self.splitter.setSizes([self.splitter.size().width() * 0.15,
                                self.splitter.size().width() * 0.75,
                                self.splitter.size().width() * 0.1,
                                ])

    def set_menubar(self, window: QMainWindow) -> None:
        """メニューバーセット"""

        self.menubar = QMenuBar()  # Make a menu without parent.
        self.menubar.setToolTip('ツールバーの表示/非表示変更<br>ショートカット：Ctrl V')
        window.setMenuBar(self.menubar)

        self.file_menu = self.menubar.addMenu('&File')
        self.view_menu = self.menubar.addMenu('&View')
        self.view_menu.addAction(self.toolbar.toggleViewAction())

    def set_statusbar(self, window: QMainWindow) -> None:
        """ステータスバーセット"""

        self.statusbar = QStatusBar()
        window.setStatusBar(self.statusbar)

        # self.statusbar.addPermanentWidget(QLabel('接続状態: '), )
        # self.statusbar.addPermanentWidget(self.connect_status_label, 4)
        # self.statusbar.addPermanentWidget(QLabel('設定: '), )
        # self.statusbar.addPermanentWidget(self.settings_status_label, 4)
        # self.statusbar.addPermanentWidget(QLabel('開始時刻: '), )
        # self.statusbar.addPermanentWidget(self.stime_label, 4)
        self.statusbar.addPermanentWidget(self.clock_label)

    def set_toolber(self, window: QMainWindow) -> None:
        """ツールバーセット"""

        self.toolbar = QToolBar()
        self.toolbar.setWindowTitle("ToolBar")
        window.addToolBar(Qt.ToolBarArea.LeftToolBarArea, self.toolbar)
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        self.connect_action = QAction(QIcon(icons.CONNECT_ICON), '接続')
        self.settings_action = QAction(QIcon(icons.SETTINGS_ICON), '設定')
        self.run_action = QAction(QIcon(icons.RUN_ICON), '開始')
        self.stop_action = QAction(QIcon(icons.STOP_ICON), '終了')
        # self.open_action = QAction(QIcon(icons.OPEN_ICON), '開く')

        self.toolbar.addAction(self.connect_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.settings_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.run_action)
        self.toolbar.addAction(self.stop_action)
        self.toolbar.addSeparator()
        # self.toolbar.addAction(self.open_action)
        # self.toolbar.addSeparator()


if __name__ == '__main__':
    import sys

    from PySide6.QtWidgets import QApplication
    import qdarktheme

    app = QApplication(sys.argv)
    app.setStyleSheet(qdarktheme.load_stylesheet())
    win = QMainWindow()
    ui = MainWindowUI()
    ui.setup_ui(win)
    win.show()

    sys.exit(app.exec())
