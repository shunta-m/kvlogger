"""実行ファイル"""
import sys

from PySide6.QtWidgets import QApplication
import qdarktheme

from kvlogger.controllers import main_ctrl


def main() -> None:
    """メイン関数"""

    app = QApplication(sys.argv)
    app.setStyleSheet(qdarktheme.load_stylesheet())

    controller = main_ctrl.MainController(app)
    controller.start()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
