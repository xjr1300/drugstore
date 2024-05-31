import unittest
import uuid
from datetime import datetime, timezone
from decimal import Decimal

from drugstore.common import jst_datetime
from drugstore.domain.models.sales import Sale, SaleDetail

from .test_customers import create_general_customer, create_special_customer
from .test_items import create_bufferin, create_seirogan


class SaleDetailTest(unittest.TestCase):
    """売上明細テストクラス"""

    def test_instantiate_by_valid_attrs(self) -> None:
        """妥当な属性で売上明細をインスタンス化できて、小計が単価と数量を乗じた額になっていることを確認"""
        id = uuid.uuid4()
        item = create_seirogan(Decimal("300"))
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
        item = create_seirogan(Decimal("300"))
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


def create_vantelin_sale_detail(
    id: uuid.UUID, unit_price: Decimal, quantities: int
) -> SaleDetail:
    """バンテリンの売上明細を作成する。

    Args:
        id: (uuid.UUID): 売上ID
        unit_price (Decimal): 単価
        quantities (int): 数量

    Returns:
        SaleDetail: バンテリンの売上明細
    """
    return SaleDetail(id, create_bufferin(unit_price), quantities)


def create_bufferin_sale_detail(
    id: uuid.UUID, unit_price: Decimal, quantities: int
) -> SaleDetail:
    """バファリンの売上明細を作成する。

    Args:
        id: (uuid.UUID): 売上ID
        unit_price (Decimal): 単価
        quantities (int): 数量

    Returns:
        SaleDetail: バファリンの売上明細
    """
    return SaleDetail(id, create_bufferin(unit_price), quantities)


class GeneralCustomerSaleTest(unittest.TestCase):
    """一般会員売上テスト"""

    @classmethod
    def setUpClass(cls) -> None:  # noqa: D102
        # 一般会員顧客
        cls.customer = create_general_customer()
        return super().setUpClass()

    def test_ensure_overall_if_subtotal_of_sale_is_less_than_3000(self) -> None:
        """一般会員の売上の小計が3,000円未満のときに、小計、割引率、割引額、課税対象額、消費税額、合計が正しいか確認"""
        sold_at = jst_datetime(2024, 1, 1)
        consumption_tax_rate = Decimal("0.1")
        sut = Sale(self.customer, sold_at, consumption_tax_rate)

        # 小計999円
        sut.add_sale_detail(create_vantelin_sale_detail(sut.id, Decimal("999"), 1))
        # 小計2,000円
        sut.add_sale_detail(create_bufferin_sale_detail(sut.id, Decimal("500"), 4))

        self.assertEqual(Decimal("2999"), sut.subtotal)
        self.assertEqual(Decimal("0.05"), sut.discount_rate)
        self.assertEqual(Decimal("149"), sut.discount_amount)
        self.assertEqual(Decimal("2850"), sut.taxable_amount)
        self.assertEqual(Decimal("0.1"), sut.consumption_tax_rate)
        self.assertEqual(Decimal("285"), sut.consumption_tax_amount)
        self.assertEqual(Decimal("3135"), sut.total)

    def test_ensure_overall_if_subtotal_of_sale_is_3000(self) -> None:
        """一般会員の売上の小計が3,000円のときに、小計、割引率、割引額、課税対象額、消費税額、合計が正しいか確認"""
        sold_at = jst_datetime(2024, 1, 1)
        consumption_tax_rate = Decimal("0.1")
        sut = Sale(self.customer, sold_at, consumption_tax_rate)

        # 小計1,000円
        sut.add_sale_detail(create_vantelin_sale_detail(sut.id, Decimal("1000"), 1))
        # 小計2,000円
        sut.add_sale_detail(create_bufferin_sale_detail(sut.id, Decimal("500"), 4))

        self.assertEqual(Decimal("3000"), sut.subtotal)
        self.assertEqual(Decimal("0.1"), sut.discount_rate)
        self.assertEqual(Decimal("300"), sut.discount_amount)
        self.assertEqual(Decimal("2700"), sut.taxable_amount)
        self.assertEqual(Decimal("0.1"), sut.consumption_tax_rate)
        self.assertEqual(Decimal("270"), sut.consumption_tax_amount)
        self.assertEqual(Decimal("2970"), sut.total)

    def test_ensure_overall_if_subtotal_of_sale_is_greater_than_3000(self) -> None:
        """一般会員の売上の小計が3,000円より大きい、小計、割引率、割引額、課税対象額、消費税額、合計が正しいか確認"""
        sold_at = jst_datetime(2024, 1, 1)
        consumption_tax_rate = Decimal("0.1")
        sut = Sale(self.customer, sold_at, consumption_tax_rate)

        # 小計1,001円
        sut.add_sale_detail(create_vantelin_sale_detail(sut.id, Decimal("1001"), 1))
        # 小計2,000円
        sut.add_sale_detail(create_bufferin_sale_detail(sut.id, Decimal("500"), 4))

        self.assertEqual(Decimal("3001"), sut.subtotal)
        self.assertEqual(Decimal("0.1"), sut.discount_rate)
        self.assertEqual(Decimal("300"), sut.discount_amount)
        self.assertEqual(Decimal("2701"), sut.taxable_amount)
        self.assertEqual(Decimal("0.1"), sut.consumption_tax_rate)
        self.assertEqual(Decimal("270"), sut.consumption_tax_amount)
        self.assertEqual(Decimal("2971"), sut.total)


class SpecialCustomerSaleTest(unittest.TestCase):
    """特別会員売上テスト"""

    @classmethod
    def setUpClass(cls) -> None:  # noqa: D102
        # 特別会員顧客
        cls.customer = create_special_customer()
        return super().setUpClass()

    def test_ensure_overall_if_subtotal_of_sale_is_less_than_3000(self) -> None:
        """特別会員の売上の小計が3,000円未満のときに、小計、割引率、割引額、課税対象額、消費税額、合計が正しいか確認"""
        sold_at = jst_datetime(2024, 1, 1)
        consumption_tax_rate = Decimal("0.1")
        sut = Sale(self.customer, sold_at, consumption_tax_rate)

        # 小計999円
        sut.add_sale_detail(create_vantelin_sale_detail(sut.id, Decimal("999"), 1))
        # 小計2,000円
        sut.add_sale_detail(create_bufferin_sale_detail(sut.id, Decimal("500"), 4))

        self.assertEqual(Decimal("2999"), sut.subtotal)
        self.assertEqual(Decimal("0.10"), sut.discount_rate)
        self.assertEqual(Decimal("299"), sut.discount_amount)
        self.assertEqual(Decimal("2700"), sut.taxable_amount)
        self.assertEqual(Decimal("0.1"), sut.consumption_tax_rate)
        self.assertEqual(Decimal("270"), sut.consumption_tax_amount)
        self.assertEqual(Decimal("2970"), sut.total)

    def test_ensure_overall_if_subtotal_of_sale_is_3000(self) -> None:
        """特別会員の売上の小計が3,000円のときに、小計、割引率、割引額、課税対象額、消費税額、合計が正しいか確認"""
        sold_at = jst_datetime(2024, 1, 1)
        consumption_tax_rate = Decimal("0.1")
        sut = Sale(self.customer, sold_at, consumption_tax_rate)

        # 小計1,000円
        sut.add_sale_detail(create_vantelin_sale_detail(sut.id, Decimal("1000"), 1))
        # 小計2,000円
        sut.add_sale_detail(create_bufferin_sale_detail(sut.id, Decimal("500"), 4))

        self.assertEqual(Decimal("3000"), sut.subtotal)
        self.assertEqual(Decimal("0.2"), sut.discount_rate)
        self.assertEqual(Decimal("600"), sut.discount_amount)
        self.assertEqual(Decimal("2400"), sut.taxable_amount)
        self.assertEqual(Decimal("0.1"), sut.consumption_tax_rate)
        self.assertEqual(Decimal("240"), sut.consumption_tax_amount)
        self.assertEqual(Decimal("2640"), sut.total)

    def test_ensure_overall_if_subtotal_of_sale_is_greater_than_3000(self) -> None:
        """特別会員の売上の小計が3,000円より大きい、小計、割引率、割引額、課税対象額、消費税額、合計が正しいか確認"""
        sold_at = jst_datetime(2024, 1, 1)
        consumption_tax_rate = Decimal("0.1")
        sut = Sale(self.customer, sold_at, consumption_tax_rate)

        # 小計1,001円
        sut.add_sale_detail(create_vantelin_sale_detail(sut.id, Decimal("1001"), 1))
        # 小計2,000円
        sut.add_sale_detail(create_bufferin_sale_detail(sut.id, Decimal("500"), 4))

        self.assertEqual(Decimal("3001"), sut.subtotal)
        self.assertEqual(Decimal("0.2"), sut.discount_rate)
        self.assertEqual(Decimal("600"), sut.discount_amount)
        self.assertEqual(Decimal("2401"), sut.taxable_amount)
        self.assertEqual(Decimal("0.1"), sut.consumption_tax_rate)
        self.assertEqual(Decimal("240"), sut.consumption_tax_amount)
        self.assertEqual(Decimal("2641"), sut.total)


class NoneCustomerSaleTest(unittest.TestCase):
    """非会員売上テスト"""

    def test_ensure_overall_if_subtotal_of_sale_is_less_than_3000(self) -> None:
        """非会員の売上の小計が3,000円未満のときに、小計、割引率、割引額、課税対象額、消費税額、合計が正しいか確認"""
        sold_at = jst_datetime(2024, 1, 1)
        consumption_tax_rate = Decimal("0.1")
        sut = Sale(None, sold_at, consumption_tax_rate)

        # 小計999円
        sut.add_sale_detail(create_vantelin_sale_detail(sut.id, Decimal("999"), 1))
        # 小計2,000円
        sut.add_sale_detail(create_bufferin_sale_detail(sut.id, Decimal("500"), 4))

        self.assertEqual(Decimal("2999"), sut.subtotal)
        self.assertEqual(Decimal("0.00"), sut.discount_rate)
        self.assertEqual(Decimal("0"), sut.discount_amount)
        self.assertEqual(Decimal("2999"), sut.taxable_amount)
        self.assertEqual(Decimal("0.1"), sut.consumption_tax_rate)
        self.assertEqual(Decimal("299"), sut.consumption_tax_amount)
        self.assertEqual(Decimal("3298"), sut.total)

    def test_ensure_overall_if_subtotal_of_sale_is_3000(self) -> None:
        """非会員の売上の小計が3,000円のときに、小計、割引率、割引額、課税対象額、消費税額、合計が正しいか確認"""
        sold_at = jst_datetime(2024, 1, 1)
        consumption_tax_rate = Decimal("0.1")
        sut = Sale(None, sold_at, consumption_tax_rate)

        # 小計1,000円
        sut.add_sale_detail(create_vantelin_sale_detail(sut.id, Decimal("1000"), 1))
        # 小計2,000円
        sut.add_sale_detail(create_bufferin_sale_detail(sut.id, Decimal("500"), 4))

        self.assertEqual(Decimal("3000"), sut.subtotal)
        self.assertEqual(Decimal("0.00"), sut.discount_rate)
        self.assertEqual(Decimal("0"), sut.discount_amount)
        self.assertEqual(Decimal("3000"), sut.taxable_amount)
        self.assertEqual(Decimal("0.1"), sut.consumption_tax_rate)
        self.assertEqual(Decimal("300"), sut.consumption_tax_amount)
        self.assertEqual(Decimal("3300"), sut.total)

    def test_ensure_overall_if_subtotal_of_sale_is_greater_than_3000(self) -> None:
        """非会員の売上の小計が3,000円より大きい、小計、割引率、割引額、課税対象額、消費税額、合計が正しいか確認"""
        sold_at = jst_datetime(2024, 1, 1)
        consumption_tax_rate = Decimal("0.1")
        sut = Sale(None, sold_at, consumption_tax_rate)

        # 小計1,001円
        sut.add_sale_detail(create_vantelin_sale_detail(sut.id, Decimal("1001"), 1))
        # 小計2,000円
        sut.add_sale_detail(create_bufferin_sale_detail(sut.id, Decimal("500"), 4))

        self.assertEqual(Decimal("3001"), sut.subtotal)
        self.assertEqual(Decimal("0.00"), sut.discount_rate)
        self.assertEqual(Decimal("0"), sut.discount_amount)
        self.assertEqual(Decimal("3001"), sut.taxable_amount)
        self.assertEqual(Decimal("0.1"), sut.consumption_tax_rate)
        self.assertEqual(Decimal("300"), sut.consumption_tax_amount)
        self.assertEqual(Decimal("3301"), sut.total)


class SaleTest(unittest.TestCase):
    """売上テストクラス"""

    def test_ensure_update_overall_after_sale_detail_that_had_same_item_is_added(
        self,
    ) -> None:
        """登録されている売上明細の商品と、同じ商品の売上明細を売上に追加したとき、登録されている売上明細が更新されることを確認"""
        customer = create_general_customer()
        sold_at = jst_datetime(2024, 1, 1)
        consumption_tax_rate = Decimal("0.1")
        sut = Sale(customer, sold_at, consumption_tax_rate)

        sut.add_sale_detail(create_vantelin_sale_detail(sut.id, Decimal("1000"), 1))
        sut.add_sale_detail(create_vantelin_sale_detail(sut.id, Decimal("1000"), 1))

        self.assertEqual(Decimal("2000"), sut.subtotal)
        self.assertEqual(Decimal("0.05"), sut.discount_rate)
        self.assertEqual(Decimal("100"), sut.discount_amount)
        self.assertEqual(Decimal("1900"), sut.taxable_amount)
        self.assertEqual(Decimal("0.1"), sut.consumption_tax_rate)
        self.assertEqual(Decimal("190"), sut.consumption_tax_amount)
        self.assertEqual(Decimal("2090"), sut.total)

    def test_ensure_update_overall_after_sale_detail_is_removed(
        self,
    ) -> None:
        """売上明細を削除したとき、小計、割引率、割引額、課税対象額、消費税額、合計が正しいか確認

        小計が3,000円以上ある売上から、売上明細が削除されて小計が3,000円未満になったとき、
        小計、割引率、割引額、課税対象額、消費税額、合計が正しいか確認する。
        """
        customer = create_general_customer()
        sold_at = jst_datetime(2024, 1, 1)
        consumption_tax_rate = Decimal("0.1")
        sut = Sale(customer, sold_at, consumption_tax_rate)
        bufferin_sd = create_bufferin_sale_detail(sut.id, Decimal("600"), 1)
        sut.add_sale_detail(bufferin_sd)
        vantelin_sd = create_vantelin_sale_detail(sut.id, Decimal("2400"), 1)
        sut.add_sale_detail(vantelin_sd)

        sut.remove_sale_detail(bufferin_sd.item.id)

        self.assertEqual(Decimal("2400"), sut.subtotal)
        self.assertEqual(Decimal("0.05"), sut.discount_rate)
        self.assertEqual(Decimal("120"), sut.discount_amount)
        self.assertEqual(Decimal("2280"), sut.taxable_amount)
        self.assertEqual(Decimal("0.1"), sut.consumption_tax_rate)
        self.assertEqual(Decimal("228"), sut.consumption_tax_amount)
        self.assertEqual(Decimal("2508"), sut.total)

    def test_raise_exception_if_assigning_item_id_that_does_not_exist_sale_details(
        self,
    ) -> None:
        """引数で指定された商品の売上明細が売上に存在しない場合に例外をスローするか確認"""
        customer = create_general_customer()
        sold_at = jst_datetime(2024, 1, 1)
        consumption_tax_rate = Decimal("0.1")
        sut = Sale(customer, sold_at, consumption_tax_rate)
        bufferin_sd = create_bufferin_sale_detail(sut.id, Decimal("600"), 1)
        sut.add_sale_detail(bufferin_sd)

        with self.assertRaises(ValueError):
            sut.remove_sale_detail(uuid.uuid4())

    def test_ensure_throw_exception_when_sale_detail_has_invalid_sale_id(self) -> None:
        """追加する売上明細の売上IDが、追加先の売上の売上IDと一致しないときに、例外をスローすることを確認"""
        customer = create_general_customer()
        sold_at = jst_datetime(2024, 1, 1)
        consumption_tax_rate = Decimal("0.1")
        sut = Sale(customer, sold_at, consumption_tax_rate)

        with self.assertRaises(ValueError):
            sut.add_sale_detail(
                create_vantelin_sale_detail(uuid.uuid4(), Decimal("1000"), 1)
            )
