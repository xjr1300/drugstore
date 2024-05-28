import unittest
import uuid
from datetime import datetime, timezone
from decimal import Decimal

from drugstore.common import jst_datetime
from drugstore.domain.models.sales import Sale, SaleDetail

from .test_customers import create_general_customer
from .test_items import create_seirogan


class SaleDetailTest(unittest.TestCase):
    """売上明細テストクラス"""

    def test_instantiate_by_valid_attrs(self) -> None:
        """妥当な属性で売上明細をインスタンス化できて、小計が単価と数量を乗じた額になっていることを確認"""
        id = uuid.uuid4()
        item = create_seirogan()
        quantities = 2

        sut = SaleDetail(id, item, quantities)

        self.assertEqual(id, sut.sale_id)
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


class SaleInitializerTest(unittest.TestCase):
    """売上イニシャライザテストクラス"""

    def test_instantiate_by_valid_attrs(self) -> None:
        """妥当な引数でインスタンスを構築できることを確認"""
        customer = create_general_customer()
        sold_at = jst_datetime(2024, 1, 1)
        consumption_tax_rate = Decimal("0.1")

        sut = Sale(customer, sold_at, consumption_tax_rate)

        self.assertEqual(customer, sut.customer)
        self.assertEqual(sold_at, sut.sold_at)
        self.assertEqual([], sut.sale_details)
        self.assertEqual(Decimal("0"), sut.subtotal)
        self.assertEqual(Decimal("0.0"), sut.discount_rate)
        self.assertEqual(Decimal("0"), sut.discount_amount)
        self.assertEqual(consumption_tax_rate, sut.consumption_tax_rate)
        self.assertEqual(Decimal("0"), sut.consumption_tax_amount)
        self.assertEqual(Decimal("0"), sut.total)

    def test_can_not_instantiate_by_non_jst_datetimes(self) -> None:
        """売上日時が日本標準時以外のときに例外をスローすることを確認"""
        customer = create_general_customer()
        dts = [datetime(2024, 1, 1), datetime(2024, 1, 1, tzinfo=timezone.utc)]
        consumption_tax_rate = Decimal("0.1")

        with self.assertRaises(ValueError):
            for dt in dts:
                _ = Sale(customer, dt, consumption_tax_rate)

    def test_can_not_instantiate_by_invalid_consumption_tax_rates(self) -> None:
        """消費税額がドメインで定められた範囲外の場合に、例外をスローすることを確認"""
        customer = create_general_customer()
        sold_at = jst_datetime(2024, 1, 1)
        rates = [Decimal("-0.01"), Decimal("1.0")]

        with self.assertRaises(ValueError):
            for rate in rates:
                _ = Sale(customer, sold_at, rate)
