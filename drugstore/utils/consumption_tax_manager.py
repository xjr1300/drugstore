from operator import attrgetter
from typing import List

from ..domain.models.consumption_taxes import (
    MAX_CONSUMPTION_TAX_END,
    MIN_CONSUMPTION_TAX_BEGIN,
    ConsumptionTax,
)


def ensure_consumption_tax_periods_are_continuous(taxes: List[ConsumptionTax]) -> bool:
    """消費税の期間が重複または途切れなく連続しているか確認する。

    Args:
        taxes (List[ConsumptionTax]): 消費税のリスト

    Raises:
        ValueError: 消費税リストは1つ以上の消費税を格納していなければなりません。

    Returns:
        bool: 消費税の期間が重複または途切れなく連続している場合はTrue、
            連続していない場合はFalse
    """
    if len(taxes) == 0:
        raise ValueError(
            "消費税リストは1つ以上の消費税を格納していなければなりません。"
        )
    if len(taxes) == 1:
        return True
    end = taxes[0].end
    index = 1
    while index < len(taxes):
        if taxes[index].begin != end:
            return False
        end = taxes[index].end
        index += 1
    return True


class ConsumptionTaxManager:
    """消費税管理者クラス

    消費税管理者クラスが管理する消費税リストの不変条件を次に示す。

    - 消費税リストの要素数は1以上
    - 消費税リストの消費税の期間に重複または途切れがない
    - 消費税リストに含まれる消費税の全期間は、MIN_CONSUMPTION_TAX_BEGINからMAX_CONSUMPTION_TAX_ENDまで
    """  # noqa: E501

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
            ValueError: 消費税の期間が途切れているか重複しています。
        """
        if len(consumption_taxes) == 0:
            raise ValueError("消費税管理者クラスは1つ以上の消費税を受け取ります。")
        consumption_taxes.sort(key=attrgetter("begin"))
        if not ensure_consumption_tax_periods_are_continuous(consumption_taxes):
            raise ValueError("消費税の期間が途切れているか重複しています。")
        consumption_taxes[0].begin = MIN_CONSUMPTION_TAX_BEGIN
        consumption_taxes[-1].end = MAX_CONSUMPTION_TAX_END
        self.consumption_taxes = consumption_taxes
