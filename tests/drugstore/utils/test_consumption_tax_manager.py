import unittest
import uuid
from datetime import datetime, timedelta
from decimal import Decimal

from drugstore.common import JST
from drugstore.domain.models.consumption_taxes import ConsumptionTax
from drugstore.utils.consumption_tax_manager import (
    ensure_consumption_tax_periods_are_continuous,
)

# 連続した消費税のリスト
CONTINUOUS_CONSUMPTION_TAXES = [
    ConsumptionTax(
        uuid.uuid4(),
        datetime(2024, 1, 1, tzinfo=JST),
        datetime(2024, 4, 1, tzinfo=JST),
        Decimal("0.05"),
    ),
    ConsumptionTax(
        uuid.uuid4(),
        datetime(2024, 4, 1, tzinfo=JST),
        datetime(2024, 7, 1, tzinfo=JST),
        Decimal("0.10"),
    ),
    ConsumptionTax(
        uuid.uuid4(),
        datetime(2024, 7, 1, tzinfo=JST),
        datetime(2024, 9, 1, tzinfo=JST),
        Decimal("0.15"),
    ),
    ConsumptionTax(
        uuid.uuid4(),
        datetime(2024, 9, 1, tzinfo=JST),
        datetime(2025, 1, 1, tzinfo=JST),
        Decimal("0.20"),
    ),
]


class ConsumptionTaxesTest(unittest.TestCase):
    """消費税リストテスト"""

    def test_ensure_consumption_taxes_are_continuous(self) -> None:
        """消費税の期間が重複または途切れなく連続している場合に、期間が連続していると判定することを確認"""
        result = ensure_consumption_tax_periods_are_continuous(
            CONTINUOUS_CONSUMPTION_TAXES
        )

        self.assertTrue(result)

    def test_ensure_one_consumption_taxes_is_continuous(self) -> None:
        """1つの消費税を期間が連続していると判定することを確認"""
        taxes = [
            ConsumptionTax(
                uuid.uuid4(),
                datetime(2024, 1, 1, tzinfo=JST),
                datetime(2025, 1, 1, tzinfo=JST),
                Decimal("0.10"),
            ),
        ]

        result = ensure_consumption_tax_periods_are_continuous(taxes)

        self.assertTrue(result)

    def test_ensure_consumption_taxes_with_interrupted_periods_are_not_continuous(
        self,
    ) -> None:
        """期間が途切れている消費税のリストを、期間が連続していないと判定することを確認"""
        taxes = CONTINUOUS_CONSUMPTION_TAXES.copy()
        # 2番目の消費税を削除して、期間を途切れさせる
        del taxes[1]

        result = ensure_consumption_tax_periods_are_continuous(taxes)

        self.assertFalse(result)

    def test_ensure_consumption_taxes_with_overlapped_periods_are_not_continuous(
        self,
    ) -> None:
        """期間が重複している消費税のリストを、期間が連続していないと判定することを確認"""
        taxes = CONTINUOUS_CONSUMPTION_TAXES.copy()
        # 最初と次の消費税の期間を重複させる
        taxes[1].begin = taxes[1].begin - timedelta(seconds=1)

        result = ensure_consumption_tax_periods_are_continuous(taxes)

        self.assertFalse(result)


class ConsumptionTaxManagerTest(unittest.TestCase):
    """消費税管理者クラステスト

    # TODO: 次の単体テストを実装すること

    - イニシャライザ
        - 消費税管理クラスを構築したとき、次の不変条件を満たしているか確認
            - 1つ以上の消費税を管理していること
            - 消費税の期間が連続していること
            - 起点日時が最も大きい消費税の終点日時が終点日時の最大値になっていること
        - 空の消費税のリストを受け取った場合、ValueError例外をスローすること
        - 消費税の期間が連続していない場合、ValueError例外をスローすること
    """
