"""UIで使用するグラフアイテム"""
import datetime as dt
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np
from PySide6.QtCore import Slot, Signal, QPointF
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

            self.layout.addItem(yaxis, 0, len(ylabels) - i)

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

    changedPlotMethod: Signal = Signal()

    def __init__(self, data_name: Dict[str, List[str]], data_maxlen: int, top_items: Optional[list] = None,
                 yspacer_count: int = 1,
                 *args, **kwargs) -> None:
        """初期化処理

        Parameters
        -----
        data_name: Dict[str, List[str]]
            生成するY軸のラベルをキーに持つ辞書. 値は追加するcurveの名前のリスト
        data_maxlen: int
            表示データ最大長
        top_items: Optional[list] default=None
            グラフ上部に配置したいもの
        yspacer_count: int default=1
            yaxesのスペーサー数
        """

        self.current_len: int = 0
        self.data_maxlen: int = data_maxlen
        self.data_pos: int = 0

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
            view_box.setXLink(self.plot)  # x軸をリンク
            self.plot.scene().addItem(view_box)  # plotItem内にviewBoxを追加

            yaxis.linkToView(view_box)  # 追加するy軸とviewBoxをリンクさせる

            for name in data_name[yaxis.labelText]:
                nan = np.empty(data_maxlen)
                nan[1:] = np.nan
                nan[0] = 0  # set_dataのpassに引っ掛からないようjに1つだけnan以外にする
                data = pg.PlotDataItem(y=nan, name=name)
                view_box.addItem(data)
                self.data.append(data)

            self.view_boxes.append(view_box)
        # ########################################################################

        self.plot.autoBtn.clicked.connect(self.reset_range)  # plotItemのautoBtnを押したときにself.reset_rage()も実行
        self.plot.vb.sigResized.connect(self.update_views)  # plotItemのサイズが変わった時にviewBox達をそれに合わせる

        self.update_views()
        self.reset_range()

    def set_data(self, values: list) -> None:
        """データ入力.
           データ長がmaxlenに到達していない時用

        Parameters
        ----------
        values: List[Sequence]
            入力データ
            [[val, val, ...], [val, val, ...], [val, val, ...], ,...]
        """

        for data, value in zip(self.data, values):
            if all(np.isnan(data.yData)):  # 全てnp.nanだったら == 非表示だったら
                pass
            ydata = data.yData
            ydata[self.current_len] = value
            data.setData(ydata)

        self.current_len += 1

        if self.current_len == self.data_maxlen - 1:
            self.changedPlotMethod.emit()
            for vb in self.view_boxes:
                vb.enableAutoRange(axis=pg.ViewBox.XAxis, enable=True)

    def set_data_maxlen(self, values: list) -> None:
        """データ入力.
           データ長がmaxlenに到達した時用

        Parameters
        ----------
        values: List[Sequence]
            入力データ
            [[val, val, ...], [val, val, ...], [val, val, ...], ,...]
        """

        self.data_pos += 1
        for data, value in zip(self.data, values):
            if all(np.isnan(data.yData)):  # 全てnp.nanだったら == 非表示だったら
                pass
            ydata = data.yData
            ydata[:-1] = ydata[1:]
            ydata[-1] = value
            data.setData(ydata)

            data.setPos(self.data_pos, 0)

    def reset_range(self) -> None:
        """表示範囲をデータに合わせる"""

        for vb in self.view_boxes:
            vb.enableAutoRange(axis=pg.ViewBox.XYAxes, enable=True)

    def update_views(self) -> None:
        """self.plot.scene()のサイズが変わったとき,view_boxもその大きさに合わせる"""

        plot_vb = self.plot.vb
        for vb in self.view_boxes:
            vb.setGeometry(plot_vb.sceneBoundingRect())
            vb.enableAutoRange(axis=pg.ViewBox.XAxis, enable=True)


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
    getLineValues = Signal(str, list)

    def __init__(self, *args, **kwargs) -> None:
        super(CustomMultiAxisWidget, self).__init__(yspacer_count=2, *args, **kwargs)

        self.plot.setAxisItems({'bottom': TimeAxisItem('date', orientation='bottom')})

        self.line = pg.InfiniteLine(angle=90, movable=True, pen=pg.mkPen('#ffd700'),
                                    hoverPen=pg.mkPen('#ffd700'))
        self.plot.addItem(self.line, ignoreBounds=True)

        self.proxy = pg.SignalProxy(self.plot.scene().sigMouseMoved,
                                    rateLimit=60,
                                    slot=self.get_mouse_position)

    @Slot()
    def get_mouse_position(self, ev: Tuple[QPointF]) -> None:
        """マウス座標にtrend_lineを移動させ, そのx座標時のデータを取得する

        Parameters
        ----------
        ev: Tuple[QtCore.QPointF]
            画面のピクセル座標
        """

        pos = ev[0]
        if not self.plot.sceneBoundingRect().contains(pos):
            # posがplot内の座標ではなかったら終了
            return

        # ########## グラフの座標取得 ##############
        # ex) coord=PySide6.QtCore.QPointF(141.6549821809388, 4.725564511858496)
        coord = self.plot.vb.mapSceneToView(pos)
        x_coord: float = coord.x()
        int_x_coord: int = int(x_coord) - self.data_pos
        if 0 > int_x_coord or int_x_coord >= self.current_len:  # データが無い範囲の時終了
            return
        # ########################

        # ########### データ取得 ###############
        data_time: str = TimeAxisItem.calc_time(x_coord)
        # [(value, 'curve name'), (**, **), ...]の形式
        line_values: List[Tuple[Optional[float], str]] = []
        for data in self.data:
            try:
                line_values.append((data.yData[int_x_coord], data.name()))
            except TypeError:  # data.yDataがNoneの時
                line_values.append((None, data.name()))
        # ########################

        self.line.setPos(int(coord.x()))
        self.getLineValues.emit(data_time, line_values)

    def switch_curve_visible(self, idx: int, _: bool, values: Optional[np.ndarray] = None) -> None:
        """curveとregionの表示を切り替える.
           valuesがNoneだったら非表示にする

        Parameters
        ----------
        idx: int
            curve番号
        _: bool
            使用しない
        values: Optional[np.ndarray] default=None
            入力データ
        """

        if values is None:
            invisible_values = np.empty(self.data_maxlen)
            invisible_values[:] = np.nan
            self.data[idx].setData(invisible_values)
        else:
            self.data[idx].setData(values)


if __name__ == '__main__':
    import sys

    test_d = {'y1': ['a'], 'y2': ['b', 'c'], 'y3': ['d', 'e', 'f']}

    len_ = 100

    app = QApplication(sys.argv)
    window = CustomMultiAxisWidget(test_d, len_)


    def update2():
        l = []
        for i in range(6):
            l.append(np.random.normal())

        window.set_data(l)


    def update3():
        l = []
        for i in range(6):
            l.append(np.random.normal())

        window.set_data_maxlen(l)


    timer = pg.QtCore.QTimer()
    timer.timeout.connect(update2)
    timer.start(100)


    def switch():
        timer.timeout.disconnect()
        timer.timeout.connect(update3)


    window.changedPlotMethod.connect(switch)

    window.show()

    # window.showMaximized()
    sys.exit(app.exec())
