import unittest
import uuid
from decimal import Decimal

from drugstore.domain.models.sales import SaleDetail

from .test_items import create_seirogan


class SaleDetailTest(unittest.TestCase):
    """売上明細テストクラス"""

    def test_instantiate_by_valid_attrs(self) -> None:
        """妥当な属性で売上明細をインスタンス化できて、小計が単価と数量を乗じた額になっていることを確認"""
        id = uuid.uuid4()
        item = create_seirogan()
        quantities = 2

        sut = SaleDetail(id, item, quantities)

        self.assertEqual(id, sut.id)
        self.assertEqual(item.id, sut.item.id)
        self.assertEqual(item.name, sut.item.name)
        self.assertEqual(item.unit_price, sut.item.unit_price)
        self.assertEqual(quantities, sut.quantities)
        self.assertEqual(Decimal("600.0"), sut.amount)

    def test_can_not_instantiate_if_quantities_is_zero(self) -> None:
        """売上明細の数量が0以下の場合に、売上明細をインスタンス化できないことを確認"""
        id = uuid.uuid4()
        item = create_seirogan()
        quantities = 0

        with self.assertRaises(ValueError):
            _ = SaleDetail(id, item, quantities)
