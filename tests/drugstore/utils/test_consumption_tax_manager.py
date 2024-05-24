import copy
import random
import unittest
import uuid
from datetime import datetime, timedelta
from decimal import Decimal

from drugstore.common import JST
from drugstore.domain.models.consumption_taxes import (
    MAX_CONSUMPTION_TAX_END,
    MIN_CONSUMPTION_TAX_BEGIN,
    ConsumptionTax,
)
from drugstore.utils.consumption_tax_manager import (
    ConsumptionTaxManager,
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


class ConsumptionTaxManagerTest(unittest.TestCase):
    """消費税管理者クラステスト

    次の不変条件が成立することを確認する。

    - 消費税リストの要素数は1以上
    - 消費税リストの消費税の期間に重複または途切れがない
    - 消費税リストに含まれる消費税の全期間は、MIN_CONSUMPTION_TAX_BEGINからMAX_CONSUMPTION_TAX_ENDまで
    """  # noqa: E501

    def test_instantiate_by_list_contains_continuous_consumption_taxes(self) -> None:
        """期間が連続した消費税のリストが渡されたとき、インスタンスを構築できることを確認"""
        # 連続した消費税リストをランダムに並び替え
        taxes = copy.deepcopy(CONTINUOUS_CONSUMPTION_TAXES)
        random.shuffle(taxes)

        sut = ConsumptionTaxManager(taxes)

        self.assertGreaterEqual(len(sut.consumption_taxes), 1)
        self.assertEqual(MIN_CONSUMPTION_TAX_BEGIN, sut.consumption_taxes[0].begin)
        self.assertEqual(MAX_CONSUMPTION_TAX_END, sut.consumption_taxes[-1].end)

    def test_instantiate_by_list_contains_one_consumption_tax(self) -> None:
        """1つの消費税を格納した消費税のリストが渡されたとき、インスタンス化できることを確認"""
        taxes = [
            ConsumptionTax(
                uuid.uuid4(),
                datetime(2024, 1, 1, tzinfo=JST),
                datetime(2025, 1, 1, tzinfo=JST),
                Decimal("0.10"),
            ),
        ]

        sut = ConsumptionTaxManager(taxes)

        self.assertGreaterEqual(len(sut.consumption_taxes), 1)
        self.assertEqual(MIN_CONSUMPTION_TAX_BEGIN, sut.consumption_taxes[0].begin)
        self.assertEqual(MAX_CONSUMPTION_TAX_END, sut.consumption_taxes[-1].end)

    def test_can_not_instantiate_by_consumption_tax_list_that_is_not_continuous(
        self,
    ) -> None:
        """期間が途切れている消費税のリストが渡されたとき、インスタンス化できないことを確認"""
        taxes = copy.deepcopy(CONTINUOUS_CONSUMPTION_TAXES)
        # 2番目の消費税を削除して、期間を途切れさせる
        del taxes[1]

        with self.assertRaises(ValueError):
            _ = ConsumptionTaxManager(taxes)

    def test_can_not_instantiate_by_consumption_tax_list_that_period_is_overlapped(
        self,
    ) -> None:
        """期間が重複している消費税のリストが渡されたとき、インスタンス化できないことを確認"""
        taxes = copy.deepcopy(CONTINUOUS_CONSUMPTION_TAXES)
        # 最初と次の消費税の期間を重複させる
        taxes[1].begin = taxes[1].begin - timedelta(seconds=1)

        with self.assertRaises(ValueError):
            _ = ConsumptionTaxManager(taxes)
