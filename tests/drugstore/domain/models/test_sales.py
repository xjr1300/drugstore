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


class SaleTest(unittest.TestCase):
    """売上テストクラス

    - 会員以外への売上をインスタンス化できて、小計、割引率、割引額、消費税率、消費税額、合計額が正しいことを確認
    - 一般会員への売上をインスタンス化できて、顧客ID、小計、割引率、割引額、消費税率、消費税額、合計額が正しいことを確認
    - 特別会員への売上をインスタンス化できて、顧客ID、小計、割引率、割引額、消費税率、消費税額、合計額が正しいことを確認
    - 売上明細のない売上をインスタンス化できないことを確認
    - 同じ商品の売上明細を登録できないことを確認
    """  # noqa: E501
