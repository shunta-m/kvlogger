"""views内で使用するもの"""
import enum


class CurveStatus(enum.Flag):
    """curve表示状態の列挙型

    VISIBLE: curve, region共に表示
    CURVE_ONLY: curveのみ表示
    INVISIBLE: curve, region共に非表示
    """

    VISIBLE = enum.auto()
    CURVE_ONLY = enum.auto()
    INVISIBLE = enum.auto()
