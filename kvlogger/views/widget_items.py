"""UIで使用するウィジットアイテム"""
import datetime as dt
from typing import Any, Dict, List, Optional

import numpy as np
from PySide6.QtCore import (QAbstractTableModel, QModelIndex, Qt,
                            Signal, Slot)
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import (QAbstractScrollArea, QCheckBox, QLabel,
                               QHBoxLayout, QItemDelegate, QHeaderView,
                               QListWidget, QListWidgetItem, QStyleOptionViewItem,
                               QTableView, QVBoxLayout, QWidget)

from kvlogger.views import graph_items as gi
from kvlogger.views import style


class CurrentValue:
    """現在値を保持する"""

    def __init__(self, col: str, trend_value: float = 0.0, line_value: float = 0.0) -> None:
        """初期化処理

        Parameters
        ----------
        col: str
            カラム名
        trend_value: float default=0.0
            値
        """

        self.col = col
        self.trend_value = trend_value
        self.line_value = line_value

    def to_list(self) -> list:
        return [self.trend_value, self.line_value]


class CurrentValueModel(QAbstractTableModel):
    """現在値を表示するテーブルのモデル"""

    def __init__(self, columns: List[str], *args, **kwargs):
        """初期化処理

        Parameters
        ----------
        columns: List[str]
            カラム名のリスト
        """

        super(CurrentValueModel, self).__init__(*args, **kwargs)

        self._data = [CurrentValue(col) for col in columns]

    def columnCount(self, parent: QModelIndex = ...) -> int:
        """列数を返す

        Returns
        ----------
        columnCount: int
            列数
        """

        return len(self._data)

    def data(self, index: QModelIndex, role: int = 0) -> Optional[float]:
        """ビューが指定している座標のデータを返す

        Parameters
        ----------
        index: QModelIndex
            ビューが要求しているデータの座標
        role: int default=0
            要求しているデータ形式. 0でDisplayRole(文字列).
            表示中のデータを文字列で要求している.

        Returns
        ----------
        data: float
            ビューに要求されたデータ
        """

        if not index.isValid():
            return

        if role == 0:
            return self._data[index.column()].to_list()[index.row()]

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = 0) -> str:
        """sectionで指定したカラムインデックスの値を返す

        Parameters
        ----------
        section: int
            カラムインデックス
        orientation: Qt.Orientation
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
            return str(self._data[section].col)

        if orientation == Qt.Orientation.Vertical and role == 0:
            return str(['trend', 'line'][section])

    def rowCount(self, parent: QModelIndex = ...) -> int:
        """行数を返す

        Returns
        ----------
        rowCount: int
            行数
        """

        return 2


class AlignDelegate(QItemDelegate):
    """文字、数字によって左寄せか右寄せかを変える"""

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        type_cell = type(index.data())
        if type_cell is str:
            option.displayAlignment = Qt.AlignLeft | Qt.AlignVCenter
        elif type_cell is int:
            option.displayAlignment = Qt.AlignRight | Qt.AlignVCenter
        elif type_cell is float:
            option.displayAlignment = Qt.AlignRight | Qt.AlignVCenter
        else:
            option.displayAlignment = Qt.AlignCenter | Qt.AlignVCenter

        QItemDelegate.paint(self, painter, option, index)


class StretchTableView(QTableView):
    """セルサイズ調節可能なTableView"""

    def __init__(self, *args, **kwargs) -> None:
        """初期化処理"""

        super(StretchTableView, self).__init__(*args, **kwargs)
        self.setAlternatingRowColors(True)
        self.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.setItemDelegate(AlignDelegate())

    def set_stretch(self) -> None:
        """rows or columnsの幅View全体にする"""

        v_header: QHeaderView = self.verticalHeader()
        h_header: QHeaderView = self.horizontalHeader()

        for vh in range(v_header.count()):
            v_header.setSectionResizeMode(QHeaderView.Stretch)

        for hh in range(h_header.count()):
            h_header.setSectionResizeMode(QHeaderView.Stretch)


class IndexCheckBox(QCheckBox):
    """グラフ曲線のshow/hideを変更する為の凡例チェックボックス
    QtWidgets.QListWidgetに追加して使う

    Attributes
    ----------
    idx: int
        自身の番号
    color: str
        インジゲーターの表示色

    Signal
    -----
    indexStateChanged
        状態が変わった時、自身の番号と状態を送信
    """

    indexStateChanged = Signal(int, bool)

    def __init__(self, idx: int, color: str, *args, **kwargs) -> None:
        """初期化処理

        Parameters
        ----------
        idx: int
            自身の番号
        color: Optional[str]
            インジケーターの表示色
        """

        self.idx: int = idx
        self.color: str = color

        super(IndexCheckBox, self).__init__(*args, **kwargs)
        self.setStyleSheet(style.changed_checkbox_style(color, True))
        self.stateChanged.connect(self.emit_changed_state)

    @Slot()
    def emit_changed_state(self) -> None:
        """
        チェックボックスの状態を判断してindexStateChangedを送信する.
        stateがTrueの時、curveを表示する.
        """

        state: bool = self.isChecked()
        if state:
            self.setStyleSheet(style.changed_checkbox_style(self.color, state))
        else:
            self.setStyleSheet(style.changed_checkbox_style(self.color, state))
        self.indexStateChanged.emit(self.idx, state)


class CheckListWidget(QListWidget):
    """グラフ曲線のshow/hideを変更するチェックボックスを格納するリストウィジット"""

    checkStateChanged = Signal(int, bool)

    def __init__(self, *args, **kwargs) -> None:
        """初期化処理

        Parameters
        ----------
        ch: int
            チャンネル番号
        """

        self.check_list: List[IndexCheckBox] = []
        super(CheckListWidget, self).__init__(*args, **kwargs)
        self.add_all_checkbox()

    def add_all_checkbox(self) -> None:
        """リスト内の全てのチェックボックスを操作するチェックボックスを追加"""

        self.add_checkbox(-1, '#000', 'all')

    def add_checkbox(self, idx: int, color: str, text: str) -> None:
        """LegendCheckBoxを追加する

        Parameters
        ----------
        idx: int
            チェックボックスの番号
        color: str
            チェックボックスのインジゲーターの色
        text: str
            チェックボックスのテキスト
        """

        # ################# ListWidgetに追加するチェックボックス作成 ###################
        item = QListWidgetItem()
        check = IndexCheckBox(idx, color, text)
        check.setChecked(True)
        check.indexStateChanged.connect(self.emit_changed_check)
        # ####################################

        self.addItem(item)
        self.setItemWidget(item, check)

        self.check_list.append(check)

    # todo 変える必要あり(2021/12/19)
    @Slot(int, bool)
    def emit_changed_check(self, idx: int, state: bool) -> None:
        """チェックボックスの状態が変わったとき、チャンネル番号を追加してcheckStateChangedを発火

        Parameters
        ----------
        idx: int
            チェックボックスの行番号
        state: bool
            チェックボックスの状態
        """

        if idx == -1:
            for check in self.check_list[1:]:
                check.setChecked(state)
        else:
            self.checkStateChanged.emit(idx, state)


class CentralWidget(QWidget):
    """画面中央のウィジット"""

    def __init__(self, data_name: Dict[str, List[str]], *args, **kwargs) -> None:
        """初期化処理

        Parameters
        ----------
        data_name: Dict[str, List[str]]
            {y軸ラベル: [測定データ名, ...]}の辞書
        """

        super(CentralWidget, self).__init__(*args, **kwargs)

        self.setup_ui(data_name)
        self.connect_slot()

    def setup_ui(self, data_name: Dict[str, List[str]]) -> None:
        """ui作成

        Parameters
        ----------
        data_name: Dict[str, List[str]]
            {y軸ラベル: [測定データ名, ...]}の辞書
        """

        main_layout = QHBoxLayout()
        right_layout = QVBoxLayout()

        self.setLayout(main_layout)

        self.plot: gi.CustomMultiAxisWidget = gi.CustomMultiAxisWidget(data_name, 1000)
        self.legend_list = CheckListWidget()

        main_layout.addWidget(self.plot, 9)
        main_layout.addLayout(right_layout, 1)

        right_layout.addWidget(QLabel(style.text_size('visible / invisible')))
        right_layout.addWidget(self.legend_list)

        # 凡例とカーブ追加
        colors: np.ndarray = style.curve_colors(len(self.plot.data))
        for idx, (plot_data_item, color) in enumerate(zip(self.plot.data, colors)):
            plot_data_item.setPen(color)
            self.legend_list.add_checkbox(idx, style.rgb_to_hex(color), plot_data_item.name())

    def connect_slot(self) -> None:
        """slot接続"""

        self.legend_list.checkStateChanged.connect(self.plot.switch_curve_visible)


if __name__ == '__main__':
    import sys

    from PySide6.QtWidgets import QApplication

    length = 100
    items_ = {'test': [f"test{i}" for i in range(2)], 'test2': [f"test2_{i}" for i in range(5)],
              'tes3': [f"test3_{i}" for i in range(2)], 'test4': [f"test4_{i}" for i in range(5)]}


    def test():
        app = QApplication(sys.argv)

        ta = StretchTableView()
        model = CurrentValueModel([key for key in items_.keys()])
        ta.setModel(model)
        ta.set_stretch()

        sec = CentralWidget(items_)

        win = QWidget()
        lay = QVBoxLayout()
        lay.addWidget(ta, 10)
        lay.addWidget(sec, 90)
        win.setLayout(lay)

        sec.plot.data[0].setData([i * 1 for i in range(10)])
        sec.plot.data[1].setData([i * 2 for i in range(10)])
        sec.plot.data[2].setData([i * 3 for i in range(10)])
        sec.plot.data[3].setData([i * 4 for i in range(10)])
        sec.plot.data[4].setData([i * 4 for i in range(10)])
        sec.plot.data[5].setData([i * 4 for i in range(10)])
        sec.plot.data[6].setData([i * 4 for i in range(10)])
        sec.plot.data[7].setData([i * 4 for i in range(10)])
        sec.plot.data[8].setData([i * 4 for i in range(10)])

        win.show()
        sys.exit(app.exec())


    test()
