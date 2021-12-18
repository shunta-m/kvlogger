"""UIで使用するグラフアイテム"""
import datetime as dt
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np
from PySide6.QtCore import Slot, Signal
from PySide6.QtWidgets import QApplication, QGraphicsWidget, QGraphicsGridLayout
import pyqtgraph as pg

from kvlogger.views import style


class TimeAxisItem(pg.AxisItem):
    """時間軸

    Attributes
    ----------
    format_: str
        日付表示 or 経過時間表示
    start_time: dt.datetime
        初期時刻
    """

    interval: float = 1.0
    start_time: dt.datetime = dt.datetime.now()

    def __init__(self, format_: str, alpha: float = 0.8, **kwargs) -> None:
        """初期化処理

        Parameters
        ----------
        format_: str
            表示する時刻形式. 'date' or 'elapsed'
        alpha: float default=0.8
            x軸のグリッド線の透明度. 0.0 - 1.0の間.
        """

        self.format_: str = format_

        super().__init__(**kwargs)
        if self.format_ == 'date':
            self.setLabel(text='Time', units=None, **style.axis_label())
        elif self.format_ == 'elapsed':
            self.setLabel(text='Elapsed time', units='s', **style.axis_label())
        else:
            raise ValueError('format_は"date"か"elapsed"です')

        self.setTickFont(style.tick_font())

        self.enableAutoSIPrefix(False)
        self.converter: Callable = self.select_converter()
        self.setGrid(alpha * 255)

    def select_converter(self) -> Callable:
        """x軸表示を時刻か経過時間か選択する

        Returns
        ----------
        converter: Callable
            x軸表示を変換する関数
        """

        def convert_date(values: List[float]) -> List[str]:
            """時刻列変換関数"""

            def convert(value: float) -> str:
                date: dt.datetime = self.start_time + dt.timedelta(seconds=value * self.interval)
                return date.strftime('%y/%m/%d %H:%M:%S')

            return list(map(convert, values))

        def convert_elapsed(values: list) -> list:
            """経過時間列変換関数
            表示中の0点から最大値までの経過時間を作成する
            """

            array: np.ndarray = np.array(values) * self.interval
            return np.round(array, decimals=3).tolist()

        if self.format_ == 'date':
            return convert_date
        return convert_elapsed

    def tickStrings(self, values, scale, spacing):
        """override. x tick表示"""

        return self.converter(values)

    @classmethod
    def calc_interval(cls, value: float, unit: str) -> None:
        """x軸表示を時刻か経過時間か選択する

        Parameters
        ----------
        value: float
            測定間隔
        unit: str
            時間単位
        """

        if unit == 's':
            cls.interval = value
        elif unit == 'min':
            cls.interval = value * 60
        elif unit == 'h':
            cls.interval = value * 3600
        else:
            raise ValueError('intervalは"s", "min", "h"のどれかです')

    @classmethod
    def calc_time(cls, value: float) -> str:
        """その時点での時刻を計算する

        Parameters
        ----------
        value: float
            時刻を知りたいポイント

        Returns
        -------
        time: str
            時刻
        """

        elapsed: float = value * cls.interval
        time_point = cls.start_time + dt.timedelta(seconds=elapsed)
        return time_point.strftime('%y/%m/%d %H:%M:%S')

    @classmethod
    def update_start_time(cls) -> None:
        """測定開始時間を更新する"""

        cls.start_time = dt.datetime.now()


class LeftYAxisWidget(QGraphicsWidget):
    """追加するY軸用のウィジット"""

    def __init__(self, ylabels: List[str], spacer_count: int = 1, *args, **kwargs) -> None:
        """初期化処理

        Parameters
        -----
        ylabels: List[str]
            生成するY軸のラベル
        spacer_count: int default=1
            スペーサーを何行入れるか
        """

        super(LeftYAxisWidget, self).__init__(*args, **kwargs)

        # レイアウト
        self.layout = QGraphicsGridLayout()
        self.layout.setContentsMargins(1, 1, 1, 1)
        self.layout.setSpacing(0)
        self.layout.setHorizontalSpacing(10)
        self.layout.setVerticalSpacing(0)
        self.layout.setRowStretchFactor(0, 10)
        self.layout.setRowStretchFactor(1, 0)
        self.setLayout(self.layout)

        self.yaxes: List[pg.AxisItem] = []

        for i, label in enumerate(ylabels):
            yaxis = pg.AxisItem(orientation='left')
            yaxis.setLabel(label)
            # yaxis.setGrid(128)  # grid線
            self.yaxes.append(yaxis)

            self.layout.addItem(yaxis, 0, i)

        for row in range(1, spacer_count + 1):
            self.layout.addItem(pg.LabelItem(' '), row, 0)


class MultiAxisWidget(pg.GraphicsLayoutWidget):
    """複数y軸グラフ

    Attributes
    -----
    plot: pg.PlotItem
        グラフ
    yaxes: LeftYAxisWidget
        y軸追加ウィジット
    """

    def __init__(self, data_name: Dict[str, List[str]], top_items: Optional[list] = None, yspacer_count: int = 1,
                 *args, **kwargs) -> None:
        """初期化処理

        Parameters
        -----
        data_name: Dict[str, List[str]]
            生成するY軸のラベルをキーに持つ辞書. 値は追加するcurveの名前のリスト
        top_items: Optional[list] default=None
            グラフ上部に配置したいもの
        yspacer_count: int default=1
            yaxesのスペーサー数
        """

        super(MultiAxisWidget, self).__init__(*args, **kwargs)

        # ############################### plotItem ##############################
        self.plot = pg.PlotItem()
        self.plot.hideAxis('left')  # 元々のy軸は隠す
        # #######################################################################

        # ########################### 左側の複数y軸作成 ##########################
        ylabels = [label for label in data_name.keys()]
        self.yaxes = LeftYAxisWidget(ylabels, spacer_count=yspacer_count)
        # #####################################################

        # #################### グラフ上部に追加したいwidgetがある時 ##################
        row_count = 0
        if top_items is not None:
            for item in top_items:
                self.addItem(item, row_count, 0, colspan=2)
                row_count += 1
        # #######################################################################

        self.addItem(self.yaxes, row_count, 0)  # 追加Y軸ウィジットをレイアウトに追加(0行0列目)
        self.addItem(self.plot, row_count, 1)  # plotItemをレイアウトに追加(0行1列目)

        self.view_boxes: List[pg.ViewBox] = []
        self.data: List[pg.PlotDataItem] = []

        # ################## yaxisとviewboxをリンクさせる ##########################
        # 1つの軸に付き1つのviewboxを割り当てる
        for i, yaxis in enumerate(self.yaxes.yaxes):
            view_box = pg.ViewBox()
            view_box.setXLink(self.plot)  # x軸をリンク挿せる
            self.plot.scene().addItem(view_box)  # plotItem内にviewBoxを追加

            yaxis.linkToView(view_box)  # 追加するy軸とviewBoxをリンクさせる

            for name in data_name[yaxis.labelText]:
                data = pg.PlotDataItem(name=name)
                view_box.addItem(data)
                self.data.append(data)

            self.view_boxes.append(view_box)
        # ########################################################################

        self.plot.autoBtn.clicked.connect(self.reset_range)  # plotItemのautoBtnを押したときにself.reset_rage()も実行
        self.plot.vb.sigResized.connect(self.update_views)  # plotItemのサイズが変わった時にviewBox達をそれに合わせる

        self.update_views()
        self.reset_range()

    def set_multi_value(self, values: List[Sequence]) -> None:
        """複数データ入力

        Parameters
        ----------
        values: List[Sequence]
            入力するデータ
        """

        for data, value in zip(self.data, values):
            data.clear()
            data.setData(value)

    def reset_range(self) -> None:
        """表示範囲をデータに合わせる"""

        for vb in self.view_boxes:
            vb.enableAutoRange(axis=pg.ViewBox.XYAxes, enable=True)

    def update_views(self) -> None:
        """self.plot.scene()のサイズが変わったとき,view_boxもその大きさに合わせる"""

        plot_vb = self.plot.vb
        for vb in self.view_boxes:
            vb.setGeometry(plot_vb.sceneBoundingRect())


class CustomMultiAxisWidget(MultiAxisWidget):
    """MultiAxisWidgetのカスタムクラス. kvloggerはこれを使用

    Attributes
    -----
    trend_line: pg.InfiniteLine
        グラフ上で動かせる縦線

    Signal
    -----
    getTrendValues
        trend_line上の値を送信する信号
        get_trend_value() で使用
    """
    getTrendValues = Signal(str, list)

    def __init__(self, ylabels, *args, **kwargs) -> None:
        super(CustomMultiAxisWidget, self).__init__(ylabels, yspacer_count=2, *args, **kwargs)

        self.plot.setAxisItems({'bottom': TimeAxisItem('date', orientation='bottom')})

        self.trend_line = pg.InfiniteLine(angle=90, movable=True, pen=pg.mkPen('#fff'))
        self.plot.addItem(self.trend_line, ignoreBounds=True)

        self.trend_line.sigPositionChanged.connect(self.get_trend_value)

    @Slot()
    def get_trend_value(self) -> None:
        """trend_lineと重なっている座標の値を取得し、getTrendValues信号を送信する"""

        # ########## trend_lineのx値取得 ##############
        x_pos: float = self.trend_line.getXPos()
        x_time: str = TimeAxisItem.calc_time(x_pos)
        x_idx = int(x_pos)
        # ########################

        # ########## trend_lineのy値取得 ##############
        # [(value, 'curve name'), (**, **), ...]の形式
        trend_values: List[Tuple[float, str]] = []
        for data in self.data:
            trend_values.append((data.yData[x_idx], data.name()))
        # ########################

        self.getTrendValues.emit(x_time, trend_values)

    # @Slot(int, CurveStatus)
    # def switch_curve_visible(self, idx: int, status: CurveStatus) -> None:
    #     """curveとregionの表示を切り替える
    #
    #     Parameters
    #     ----------
    #     idx: int
    #         curve番号
    #     status: CurveStatus
    #         表示 / 非表示判定
    #     """
    #
    #     if idx not in self.curves:
    #         raise ValueError('番号が存在していません')
    #
    #     if status == CurveStatus.VISIBLE:
    #         self.curves[idx].added(self.plot)
    #     elif status == CurveStatus.CURVE_ONLY:
    #         self.curves[idx].removed_region(self.plot)
    #     elif status == CurveStatus.INVISIBLE:
    #         self.curves[idx].removed(self.plot)


if __name__ == '__main__':
    import sys

    test_d = {'y1': ['a', 'b', 'c'], 'y2': ['d', 'e'], 'y3': ['f']}

    app = QApplication(sys.argv)
    window = CustomMultiAxisWidget(test_d)
    # window = CustomMultiAxisWidget([f"y{i}" for i in range(3, 0, -1)])

    data1 = np.random.randint(0, 10, 10)
    data2 = np.random.randint(0, 10, 10)
    data3 = np.random.randint(0, 10, 10)
    data4 = np.random.randint(0, 10, 10)
    data5 = np.random.randint(0, 10, 10)
    data6 = np.empty(0)
    # data6 = np.random.randint(0, 10, 10)
    # data7 = np.random.randint(0, 10, 10)
    # data8 = np.random.randint(0, 10, 10)
    # data9 = np.random.randint(0, 10, 10)
    # data10 = np.random.randint(0, 10, 10)

    window.set_multi_value([data1, data2, data3, data4, data5, data6])
    # data6, data7, data8, data9, data10])

    # for i, color in enumerate(['b', 'g', 'r']):
    #     window.yaxes.yaxes[i].setPen(pg.mkPen(color))
    #     window.data[i].setPen(pg.mkPen(color))

    window.update_views()
    window.reset_range()

    window.show()
    # window.showMaximized()
    sys.exit(app.exec())