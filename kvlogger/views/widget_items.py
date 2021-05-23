"""UIで使用するウィジットアイテム"""
import enum
from typing import List, Optional

import numpy as np
import pandas as pd
from PySide6.QtCore import (QAbstractTableModel, QModelIndex, Qt,
                            Signal, Slot)
from PySide6.QtWidgets import (QAbstractScrollArea, QCheckBox, QFrame,
                               QHBoxLayout, QLabel, QListWidget,
                               QProgressBar, QListWidgetItem, QSplitter,
                               QTableView, QVBoxLayout, QWidget)

from kvlogger.views import CurveStatus
from kvlogger.views import graph_items as gi
from kvlogger.views import style


class DataFrameModel(QAbstractTableModel):
    """pd.DataFrameをモデルにするTableModel

    Attributes
    ----------
    data_frame: pd.DataFrame
        モデルにするデータフレーム
    """

    def __init__(self, data_frame: pd.DataFrame, parent=None) -> None:
        """初期化処理

        Parameters
        ----------
        data_frame: pd.DataFrame
            モデルにするデータフレーム
        """

        self.data_frame: pd.DataFrame = data_frame
        super(DataFrameModel, self).__init__(parent)

    def columnCount(self, parent: QModelIndex = ...) -> int:
        """列数を返す

        Returns
        ----------
        columnCount: int
            列数
        """

        return self.data_frame.shape[1]

    def data(self, index: QModelIndex, role: int = 0) -> Optional[str]:
        """ビューが指定している座標のデータを返す

        Parameters
        ----------
        index: QtCore.QModelIndex
            ビューが要求しているデータの座標
        role: int default=0
            要求しているデータ形式. 0でDisplayRole(文字列).
            表示中のデータを文字列で要求している.

        Returns
        ----------
        data: str
            ビューに要求されたデータ
        """

        if not index.isValid():
            return

        if role == 0:
            return str(self.data_frame.iloc[index.row(), index.column()])

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = 0) -> str:
        """sectionで指定したカラムインデックスの値を返す

        Parameters
        ----------
        section: int
            カラムインデックス
        orientation: QtCore.Qt.Orientation
            ヘッダーの向き
        role: int default=0
            要求しているデータ形式. 0でDisplayRole(文字列).
            表示中のデータを文字列で要求している.

        Returns
        -------
        headerData: str
            ヘッダー
        """

        if orientation == Qt.Orientation.Horizontal and role == 0:
            return str(self.data_frame.columns[section])

        if orientation == Qt.Orientation.Vertical and role == 0:
            return str(self.data_frame.index[section])

    def rowCount(self, parent: QModelIndex = ...) -> int:
        """行数を返す

        Returns
        ----------
        rowCount: int
            行数
        """

        return self.data_frame.shape[0]

    def reset_data(self, data: pd.DataFrame) -> None:
        """モデルを再定義する

        Parameters
        ----------
        data: pd.DataFrame
            新しくモデルにするデータフレーム
        """

        self.beginResetModel()
        self.data_frame = data.copy()
        self.endResetModel()


class DataFrameView(QTableView):
    """pd.DataFrameを見るTableView"""

    def __init__(self, *args, **kwargs) -> None:
        """初期化処理"""

        super(DataFrameView, self).__init__(*args, **kwargs)
        self.setAlternatingRowColors(True)
        self.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

    def set_row_height(self, height: int = 70) -> None:
        """行の高さを変更する

        Parameters
        ----------
        height: int default=50
            高さ
        """

        v_header = self.verticalHeader()
        for v in range(v_header.count()):
            v_header.setDefaultSectionSize(height)


class LegendCheckBox(QCheckBox):
    """グラフ曲線のshow/hideを変更する為の凡例チェックボックス
    QtWidgets.QListWidgetに追加して使う

    Attributes
    ----------
    idx: int
        QListWidgetの何行目に追加したかを記憶
    """

    statusChanged = Signal(int, CurveStatus)

    def __init__(self, idx: int, color: str, *args, **kwargs) -> None:
        """初期化処理

        Parameters
        ----------
        idx: int
            QListWidgetの何行目に追加したか
        color: str
            インジケーターの色表示
        """

        self.idx: int = idx
        self.color: str = color
        self.status: CurveStatus = CurveStatus.VISIBLE

        super(LegendCheckBox, self).__init__(*args, **kwargs)
        self.setStyleSheet(style.curve_check(color, self.status.value))
        self.stateChanged.connect(self.changed_check_color)

    @Slot()
    def changed_check_color(self) -> None:
        """チェックボックスの状態を判断して色を変える"""

        if self.status == CurveStatus.VISIBLE:
            self.status = CurveStatus.CURVE_ONLY
        elif self.status == CurveStatus.CURVE_ONLY:
            self.status = CurveStatus.INVISIBLE
        else:
            self.status = CurveStatus.VISIBLE

        self.emit_status_changed()

    def emit_status_changed(self) -> None:
        """statusChanged送信用"""

        self.setStyleSheet(style.curve_check(self.color, self.status.value))
        self.statusChanged.emit(self.idx, self.status)


class LegendListWidget(QListWidget):
    """グラフ曲線のshow/hideを変更するチェックボックスを格納するリストウィジット

    Attributes
    ----------
    check_list: List[LegendCheckBox]
        チェックボックス格納
    """

    checkStatusChanged = Signal(int, CurveStatus)

    def __init__(self, *args, **kwargs) -> None:
        """初期化処理"""

        self.check_list: List[LegendCheckBox] = []

        super(LegendListWidget, self).__init__(*args, **kwargs)
        self.add_all_checkbox()

    def add_all_checkbox(self) -> None:
        """リスト内の全てのチェックボックスを操作するチェックボックスを追加"""

        self.add_checkbox(-1, '#000', 'all')

    def add_checkbox(self, idx: int, color: str, label: str) -> None:
        """LegendCheckBoxを追加する

        Parameters
        ----------
        idx: int
            チェックボックス番号
        color: str
            チェックボックスインジケーターの色
        label: str
            チェックボックスラベル
        """

        check: LegendCheckBox = LegendCheckBox(idx, color, label)
        item = QListWidgetItem()

        self.addItem(item)
        self.setItemWidget(item, check)

        self.check_list.append(check)
        check.statusChanged.connect(self.changed_status)

    def clear_checkbox(self) -> None:
        """リスト内のチェックボックスを消去する"""

        for check in self.check_list:
            check.statusChanged.disconnect(self.changed_status)

        self.clear()
        self.check_list.clear()

    @Slot(int, CurveStatus)
    def changed_status(self, idx: int, status: CurveStatus) -> None:
        """チェックボックスの状態が変わったとき、チャンネル番号を追加してcheckStateChangedを発火

        Parameters
        ----------
        idx: int
            チェックボックスの行番号
        status: CurveStatus
            curveの状態
        """

        if idx == -1:
            for check in self.check_list[1:]:
                check.status = status
                check.emit_status_changed()
        else:
            self.checkStatusChanged.emit(idx, status)


class SectionMeasureWidget(QWidget):
    """セクションごとの測定画面"""

    def __init__(self, section: str, items: List[str], *args, **kwargs) -> None:
        """初期化処理

        Parameters
        ----------
        section: str
            セクション名
        items: List[str]
            セクション内のアイテム
        """

        super(SectionMeasureWidget, self).__init__(*args, **kwargs)

        self.setup_ui(section, items)
        self.connect_slot()

    def setup_ui(self, ylabel: str, items: List[str]) -> None:
        """ui作成

        Parameters
        ----------
        ylabel: str
            グラフyラベル
        items: List[str]
            セクション内のアイテム
        """

        splitter: QSplitter = QSplitter()
        left_widget: QWidget = QWidget()
        right_widget: QWidget = QWidget()

        main_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        main_layout.addWidget(splitter)
        self.setLayout(main_layout)

        self.describe_view: DataFrameView = DataFrameView()
        self.progress: QProgressBar = QProgressBar()
        self.graph: gi.MainPlot = gi.MainPlot(ylabel)
        self.legend_list: LegendListWidget = LegendListWidget()

        left_layout.addWidget(QLabel('Describe'))
        left_layout.addWidget(self.describe_view)
        left_layout.addWidget(self.progress)
        left_widget.setLayout(left_layout)

        right_layout.addWidget(QLabel('Legend'))
        right_layout.addWidget(self.legend_list)
        right_widget.setLayout(right_layout)

        splitter.addWidget(left_widget)
        splitter.addWidget(self.graph)
        splitter.addWidget(right_widget)

        splitter.setSizes([splitter.size().width() * 0.25,
                           splitter.size().width() * 0.65,
                           splitter.size().width() * 0.10])

        colors: np.ndarray = style.curve_colors(len(items))
        for idx, (item, color) in enumerate(zip(items, colors)):
            self.graph.add_curve(idx, color, item)
            self.legend_list.add_checkbox(idx, style.rgb_to_hex(color), item)

        for curve in self.graph.curves.values():
            r1 = int(np.random.rand() * 10)
            r2 = r1 + 10
            curve.set_data(np.random.randint(r1, r2, 100))

    def connect_slot(self) -> None:
        """slot接続"""

        self.legend_list.checkStatusChanged.connect(self.graph.switch_curve_visible)
        self.legend_list.checkStatusChanged.connect(self.graph.switch_curve_visible)


class StaticHLine(QFrame):
    """横線"""

    def __init__(self) -> None:
        super(StaticHLine, self).__init__()
        self.setFrameStyle(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)

        self.setLineWidth(0)
        self.setMidLineWidth(1)


if __name__ == '__main__':
    import sys

    from PySide6.QtWidgets import QApplication

    length = 5
    sec = 'test'
    items_ = [f"test{i}" for i in range(length)]

    app = QApplication(sys.argv)
    win = SectionMeasureWidget(sec, items_)
    win.show()

    sys.exit(app.exec())
