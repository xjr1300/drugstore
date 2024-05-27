import uuid
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Self

from drugstore.common import JST, is_jst_datetime

# 最も過去の消費税の起点日
MIN_CONSUMPTION_TAX_BEGIN = datetime.min.replace(tzinfo=JST)
# 最も将来の消費税の終点日
MAX_CONSUMPTION_TAX_END = datetime.max.replace(tzinfo=JST)

# 消費税率の範囲
MIN_CONSUMPTION_TAX_RATE = Decimal("0.0")
MAX_CONSUMPTION_TAX_RATE = Decimal("1.0")


@dataclass
class ConsumptionTax:
    """消費税"""

    # 消費税率ID
    id: uuid.UUID
    # 消費税を適用する起点日時 (左閉区間)
    begin: datetime
    # 消費税を適用する終点日時 (右開区間)
    end: datetime
    # 消費税率
    rate: Decimal

    def __init__(
        self, id: uuid.UUID, begin: datetime, end: datetime, rate: Decimal
    ) -> None:
        """イニシャライザ

        Args:
            id (uuid.UUID): 消費税ID
            begin (datetime): 消費税の起点日時
            end (datetime): 消費税の終点日時
            rate (Decimal): 消費税の税率

        Raises:
            ValueError: 消費税の起点日時と終点日時は日本標準時でなくてはなりません。
            ValueError: 消費税の起点日時が範囲外です。
            ValueError: 消費税の終点日時が範囲外です。
            ValueError: 消費税の起点日時が終点日時以降です。
            ValueError: 消費税の税率が0.0未満または1.0以上です。
        """
        if not is_jst_datetime(begin) or not is_jst_datetime(end):
            raise ValueError(
                "消費税の起点日時と終点日時は日本標準時でなくてはなりません。"
            )
        if begin < MIN_CONSUMPTION_TAX_BEGIN or MAX_CONSUMPTION_TAX_END <= begin:
            raise ValueError("消費税の起点日時が範囲外です。")
        if end <= MIN_CONSUMPTION_TAX_BEGIN or MAX_CONSUMPTION_TAX_END < end:
            raise ValueError("消費税の終点日時が範囲外です。")
        if end <= begin:
            raise ValueError("消費税の起点日時が終点日時以降です。")
        if not validate_consumption_tax_rate(rate):
            raise ValueError("消費税の税率が0.0未満または1.0以上です。")
        self.id = id
        self.begin = begin
        self.end = end
        self.rate = rate

    def contains(self, other: Self) -> bool:
        """消費税の期間が引数で与えられた消費税の期間を含むか確認する。

        Args:
            other (Self): 消費税

        Returns:
            bool: 消費税の期間が引数で与えられた消費税の期間を含む場合True、
                含まない場合はFalse
        """
        if other.begin < self.begin:
            return False
        if self.end < other.end:
            return False
        return True


def validate_consumption_tax_rate(rate: Decimal) -> bool:
    """消費税の税率を検証する。

    Args:
        rate (Decimal): 消費税の税率

    Returns:
        bool: 消費税の税率が妥当な場合はTrue、そうでない場合はFalse
    """
    return MIN_CONSUMPTION_TAX_RATE <= rate < MAX_CONSUMPTION_TAX_RATE
