from typing import List

from ..domain.models.consumption_taxes import ConsumptionTax


def ensure_consumption_tax_periods_are_continuous(taxes: List[ConsumptionTax]) -> bool:
    """消費税の期間が重複または途切れなく連続しているか確認する。

    Args:
        taxes (List[ConsumptionTax]): 消費税のリスト

    Returns:
        bool: 消費税の期間が重複または途切れなく連続している場合はTrue、
            連続していない場合はFalse
    """


class ConsumptionTaxManager:
    """消費税管理者クラス"""

    def __init__(self, consumption_taxes: List[ConsumptionTax]) -> None:
        """イニシャライザ

        1. 消費税のリストを起点日時でソート
        2. 消費税リストに消費税の期間が重複または途切れなく連続しているか確認
        3. 先頭の消費税の起点日時に起点日時の最小値を設定
        4. 最後の消費税の終点日時に終点日時の最大値を設定

        Args:
            consumption_taxes (List[ConsumptionTax]): 消費税のリスト

        Raises:
            ValueError: 消費税管理者クラスは1つ以上の消費税を受け取ります。
        """
        if len(consumption_taxes) == 0:
            raise ValueError("消費税管理者クラスは1つ以上の消費税を受け取ります。")
