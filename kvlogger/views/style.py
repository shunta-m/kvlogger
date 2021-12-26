"""UIのスタイルを記載"""
from typing import Sequence

import numpy as np
from PySide6.QtGui import QFont
import seaborn as sns


def changed_checkbox_style(color: str, flag: bool) -> str:
    """凡例チェックボックスをクリックしたときのスタイル変更
    dark theme のスタイルシートを一部無効にしている

    Parameters
    ----------
    color
    flag

    Returns
    -------

    """
    if flag is True:
        return f"""QCheckBox {{font-size:12pt; border-width: 0px;}}
                   QCheckBox::indicator {{margin: 0 0 2 10;
                                          height: 10px;
                                          width: 18px;
                                          Background-color: {color};
                                          image:url()}}
                    }}
                """
    else:
        return f"""QCheckBox {{font-size:12pt; background-color: #f08080; border-width: 0px;}}
                   QCheckBox::indicator {{margin: 0 0 2 10;
                                          height: 10px;
                                          width: 18px;
                                          Background-color: {color};
                                          image:url()}}
                """


def rgb_to_hex(rgb: Sequence) -> str:
    """(r, g, b) -> #rrggbb変換

    Parameters
    ----------
    rgb: tuple
        rgbのタプル

    Returns
    -------
    hex: str
        カラーコード
    """

    r, g, b = f"{rgb[0]:02x}", f"{rgb[1]:02x}", f"{rgb[2]:02x}"
    return '#' + r + g + b


def curve_colors(num: int) -> np.ndarray:
    """curveの色を作成

    Parameters
    ----------
    num: int
        色を作成する数

    Returns
    ----------
    colors: np.ndarray
        色. [(r, g, b), (r, g, b), ...]
    """

    colors: np.ndarray = np.array(sns.color_palette(n_colors=num)) * 255
    return colors.astype(np.uint8)


def tag(name: str, fontsize: int):
    """タグ装飾用デコレータ

    Parameters
    ----------
    name: str
        タグの名前
    fontsize: int
        フォントサイズ
    """

    def _tag(f):
        def _wrapper(text: str):
            start_tag = f"<{name} style='font-size:{fontsize}px'>"
            body = f(text)
            end_tag = f"</{name}>"

            return start_tag + body + end_tag

        return _wrapper

    return _tag


@tag('div', 14)  # 第2引数(25の部分)を変更すると文字サイズが変わる
def text_size(text) -> str:
    return text


def axis_label(color: str = '#969696', size: int = 12) -> dict:
    return {'color': color, 'font-size': f"{size}pt"}


def tick_font(size: int = 10) -> QFont:
    font = QFont()
    font.setPointSize(size)
    return font
