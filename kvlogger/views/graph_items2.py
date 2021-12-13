"""UIで使用するグラフアイテム"""
import datetime as dt
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np
from PySide6.QtGui import QColor
from PySide6.QtCore import Slot, Signal, QPointF
from PySide6.QtWidgets import QApplication, QGraphicsWidget, QGraphicsGridLayout
import pyqtgraph as pg

from kvlogger.views import CurveStatus
from kvlogger.views import style


class SortableCurve(pg.PlotDataItem):
    """並べ替え可能なpg.PlotCurveItem
    pg.PlotCurveItem.setPosでスクロールさせながら表示する

    sigSentInfo: Signal
        自身の情報(名前, 色)を送信するシグナル
    emit_num: int
        sigMouseMoved(pg.PlotItemのシグナル)を受け取ったタイミングを判別する変数.
    nearest: List[float] = [1.0, 1.0]
        sigMouseMovedを受け取ったとき、どのcurveが一番近いか判別するリスト

    Attributes
    ----------
    idx: int
        整列番号
    color: Tuple[int, int, int, int]
        自身の色.
    """

    sigSentInfo: Signal = Signal(tuple)
    emit_num: int = 0
    nearest: List[float] = [1.0, 1.0]

    def __init__(self, idx: int, *args, **kwargs) -> None:
        """初期化処理


        Parameters
        ----------
        idx: int
            整列番号
        """

        self.idx: int = idx
        super(SortableCurve, self).__init__(*args, **kwargs)

        self.color: Tuple[int, int, int] = tuple(self.opts['pen'])

    @Slot(int, QPointF)
    def send_info(self, emit_num: int, coord: QPointF) -> None:
        """

        Parameters
        ----------
        emit_num: int
            同じタイミングのsigMouseMovedシグナルかどうかを調べる数字
        coord: QPointF
            マウスカーソルがあるグラフ座標
        """

        if self.curve.mouseShape().contains(coord):
            info: Tuple[str, tuple] = self.opts['name'], self.color

            idx_y: int = np.argmin(np.abs(coord.y() - self.yData))
            x_diff: float = np.min(np.abs(coord.x() - self.xData[idx_y]))

            idx_x: int = np.argmin(np.abs(coord.x() - self.xData))
            y_diff: float = np.min(np.abs(coord.y() - self.yData[idx_x]))

            if self.select_emitter(emit_num, x_diff, y_diff):
                self.sigSentInfo.emit(info)

    @classmethod
    def select_emitter(cls, emit_num: int, x_diff: float, y_diff: float) -> bool:
        """どのcurveのsigSentInfoシグナルを発火するかを決める.
        マウスカーソルが一番近いcurveを調べてsigSendInfoを発火する.

        Parameters
        ----------
        emit_num: int
            同じタイミングのsigMouseMovedシグナルかどうかを調べる数字
        x_diff: float
            マウスカーソルの座標とその座標のcurveのx値の差分
        y_diff: float
            マウスカーソルの座標とその座標のcurveのy値の差分

        Returns
        -------
        result: bool
            sigSentInfoを送信するかの結果
        """

        if cls.emit_num != emit_num:
            cls.emit_num = emit_num
            cls.nearest = [1.0, 1.0]

        result: bool = False

        if cls.nearest[0] > x_diff:
            cls.nearest[0] = x_diff
            result = True

        if cls.nearest[1] > y_diff:
            cls.nearest[1] = y_diff
            result = True
        return result

    def set_data(self, values: np.ndarray) -> None:
        """測定値をグラフ表示する.

        Parameters
        ----------
        values: np.ndarray
            測定値
        """

        self.setData(values)


class RegionCurve(SortableCurve):
    """Region付curve"""

    def __init__(self, *args, **kwargs) -> None:
        """初期化処理"""

        self.min_: float = 0
        self.max_: float = 0
        super(RegionCurve, self).__init__(*args, **kwargs)
        # color: QColor = QColor(*self.color[:-1], a=32)
        color: QColor = QColor(*self.color, a=32)
        self.region = pg.LinearRegionItem(orientation='horizontal',
                                          brush=pg.mkBrush(color),
                                          pen=pg.mkPen(color),
                                          movable=False)
        self.region.setRegion((0, 0))
        self.region.setZValue(10)

    def added(self, widget: pg.PlotItem) -> None:
        """自身とregionをwidgetに追加する

        Parameters
        ----------
        widget: pg.PlotItem
            追加するプロットアイテム
        """

        if self not in widget.items:
            widget.addItem(self, ignoreBounds=False)
        if self.region not in widget.items:
            widget.addItem(self.region, ignoreBounds=True)

    def reset_region(self) -> None:
        """regionをリセットする"""

        self.min_, self.max_ = min(self.yData), max(self.yData)
        self.region.setRegion((self.min_, self.max_))

    def removed(self, widget: pg.PlotItem) -> None:
        """自身とregionをwidgetから削除する

        Parameters
        ----------
        widget: pg.PlotItem
            curveとregionを削除するプロットアイテム
        """

        if self in widget.items:
            widget.removeItem(self)
            widget.removeItem(self.region)

    def set_data(self, values: np.ndarray) -> None:
        """測定値をグラフ表示する. regionの範囲を最大、最小値に合わせる

        Parameters
        ----------
        values: np.ndarray
            測定値
        """

        self.min_, self.max_ = np.min(values), np.max(values)

        self.setData(values)
        self.region.setRegion((self.min_, self.max_))

    def removed_region(self, widget: pg.PlotItem) -> None:
        """regionの表示 / 非表示切り替え

        Parameters
        ----------
        widget: pg.PlotItem
            regionを削除するプロットアイテム
        """

        if self.region in widget.items:
            widget.removeItem(self.region)
        if self not in widget.items:
            widget.addItem(self)

    def update_data(self, values: np.ndarray) -> None:
        """測定値を更新する

        Parameters
        ----------
        values: np.ndarray
            測定値
        """

        min_, max_ = min(values), max(values)
        self.min_ = min(self.min_, min_)
        self.max_ = max(self.max_, max_)

        self.setData(values)
        self.region.setRegion((self.min_, self.max_))


@Slot(QPointF)
def set_coord_text(coord: QPointF) -> None:
    """座標ラベル表示

    Parameters
    ----------
    coord: QtCore.QPointF
        マウス座標
    """

    time = TimeAxisItem.calc_time(coord.x())
    val = f"{coord.y():.3e}"
    print(time, val)


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
            yaxis.setGrid(128)  # grid線
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

    def __init__(self, ylabels: List[str], top_items: Optional[list] = None, yspacer_count: int = 1,
                 *args, **kwargs) -> None:
        """初期化処理

        Parameters
        -----
        ylabels: List[str]
            生成するY軸のラベル
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

        self.yaxes = LeftYAxisWidget(ylabels, spacer_count=yspacer_count)

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

            data = pg.PlotDataItem(name=yaxis.labelText)
            view_box.addItem(data)

            self.view_boxes.append(view_box)
            self.data.append(data)
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
    horizontal_line: pg.InfiniteLine
        グラフ上で動かせる横線
    vertical_line: pg.InfiniteLine
        グラフ上で動かせる縦線

    Signal
    -----
    mouseMoved
        self.plot上をマウスが動いたときの信号
        2021/12/14時, 使用予定なし (pg.InfiniteLineの方が使いやすい)
    """
    mouseMoved = Signal(QPointF)

    def __init__(self, ylabels, *args, **kwargs) -> None:
        super(CustomMultiAxisWidget, self).__init__(ylabels, yspacer_count=2, *args, **kwargs)

        self.plot.setAxisItems({'bottom': TimeAxisItem('date', orientation='bottom')})

        self.vertical_line = pg.InfiniteLine(angle=90, movable=True, pen=pg.mkPen('#fff'))
        self.horizontal_line = pg.InfiniteLine(pos=1, angle=0, movable=True, pen=pg.mkPen('#fff'))
        self.plot.addItem(self.horizontal_line, ignoreBounds=True)
        self.plot.addItem(self.vertical_line, ignoreBounds=True)

        self.vertical_line.sigPositionChanged.connect(self.get_trend_value)
        # self.mouseMoved.connect(set_coord_text)
        # self.proxy = pg.SignalProxy(self.plot.scene().sigMouseMoved,
        #                             rateLimit=60,
        #                             slot=self.get_mouse_position)

    def get_trend_value(self) -> None:
        
        x_idx = int(self.vertical_line.getXPos())
        l = [TimeAxisItem.calc_time(self.vertical_line.getXPos())]
        for data in self.data:
            l.append((data.yData[x_idx], data.name()))
        print(l, x_idx)

    def get_mouse_position(self, event: Tuple[QPointF]) -> None:
        """

        Parameters
        ----------
        event: Tuple[QtCore.QPointF]
            画面のピクセル座標
        """

        pos = event[0]
        if not self.plot.sceneBoundingRect().contains(pos):
            # posがplot内の座標ではなかったら終了
            return

        # グラフの座標取得
        # ex) coord=PyQt5.QtCore.QPointF(141.6549821809388, 4.725564511858496)
        coord = self.plot.vb.mapSceneToView(pos)
        self.mouseMoved.emit(coord)


class MainPlot(pg.GraphicsLayoutWidget):
    """x軸が複数あるプロット

    Attributes
    ----------
    emit_no: int
        sigMouseMoved(pg.PlotItemのシグナル)を受け取ったタイミングを判別する変数.
    curves: Dict[int, RegionCurve]

    labels: CursorLabel
        マウスカーソル位置表示用ラベル
    plot: pg.PlotItem
        プロット
    """

    mouseMoved = Signal(int, QPointF)

    def __init__(self, ylabel: str, *args, **kwargs) -> None:
        """初期化処理

        Parameters
        ----------
        ylabel: str
            y軸ラベル
        """

        self.emit_no = 0
        self.curves: Dict[int, RegionCurve] = {}
        super(MainPlot, self).__init__(*args, **kwargs)

        self.labels: CursorLabel = CursorLabel(ylabel)
        self.plot: pg.PlotItem = pg.PlotItem()
        yaxis: pg.AxisItem = self.plot.getAxis('left')
        yaxis.setTickFont(style.tick_font())
        yaxis.setLabel(text=ylabel, **style.axis_label())

        self.plot.showGrid(y=True, alpha=0.8)

        self.addItem(self.labels, 0, 0)
        self.addItem(self.plot, 1, 0)

        self.plot.setAxisItems({'bottom': TimeAxisItem('date', orientation='bottom')})
        sub_xaxis: TimeAxisItem = TimeAxisItem('elapsed', alpha=0,
                                               orientation='bottom', linkView=self.plot.vb)
        sub_xaxis.setZValue(-1000)
        self.plot.layout.addItem(sub_xaxis, 4, 1)
        self.plot.layout.setVerticalSpacing(10)

        self.mouseMoved.connect(self.labels.set_coord_text)
        self.proxy = pg.SignalProxy(self.plot.scene().sigMouseMoved,
                                    rateLimit=60,
                                    slot=self.get_mouse_position)

    def add_curve(self, idx: int, color: tuple, name: str) -> None:
        """プロットするcurveを追加する

        Parameters
        ----------
        idx: int
            カーブ番号
        color: tuple
            (r, g, b)
        name: str
            curveの名前
        """

        curve: RegionCurve = RegionCurve(idx, name=name, pen=color)
        curve.sigSentInfo.connect(self.labels.set_curve_label)
        self.mouseMoved.connect(curve.send_info)
        curve.added(self.plot)
        self.curves[idx] = curve

    def get_mouse_position(self, event: Tuple[QPointF]) -> None:
        """

        Parameters
        ----------
        event: Tuple[QtCore.QPointF]
            画面のピクセル座標
        """

        self.emit_no += 1
        if self.emit_no == 128:
            self.emit_no = 0

        pos = event[0]
        if not self.plot.sceneBoundingRect().contains(pos):
            # posがplot内の座標ではなかったら終了
            return

        # グラフの座標取得
        # ex) coord=PyQt5.QtCore.QPointF(141.6549821809388, 4.725564511858496)
        coord = self.plot.vb.mapSceneToView(pos)
        self.mouseMoved.emit(self.emit_no, coord)

    @Slot(int, CurveStatus)
    def switch_curve_visible(self, idx: int, status: CurveStatus) -> None:
        """curveとregionの表示を切り替える

        Parameters
        ----------
        idx: int
            curve番号
        status: CurveStatus
            表示 / 非表示判定
        """

        if idx not in self.curves:
            raise ValueError('番号が存在していません')

        if status == CurveStatus.VISIBLE:
            self.curves[idx].added(self.plot)
        elif status == CurveStatus.CURVE_ONLY:
            self.curves[idx].removed_region(self.plot)
        elif status == CurveStatus.INVISIBLE:
            self.curves[idx].removed(self.plot)


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    window = CustomMultiAxisWidget([f"y{i}" for i in range(2, 0, -1)])

    data1 = np.random.randint(0, 10, 10)
    data2 = np.random.randint(0, 10, 10)
    data3 = np.random.randint(0, 10, 10)
    data4 = np.random.randint(0, 10, 10)
    data5 = np.random.randint(0, 10, 10)
    data6 = np.random.randint(0, 10, 10)
    data7 = np.random.randint(0, 10, 10)
    data8 = np.random.randint(0, 10, 10)
    data9 = np.random.randint(0, 10, 10)
    data10 = np.random.randint(0, 10, 10)

    window.set_multi_value([data1, data2, data3, data4, data5,
                            data6, data7, data8, data9, data10])

    # for i, color in enumerate(['b', 'g', 'r']):
    #     window.yaxes.yaxes[i].setPen(pg.mkPen(color))
    #     window.data[i].setPen(pg.mkPen(color))

    window.update_views()
    window.reset_range()

    window.show()
    # window.showMaximized()
    sys.exit(app.exec())
