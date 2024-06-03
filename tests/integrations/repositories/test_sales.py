import sqlite3
import uuid
from datetime import datetime
from decimal import Decimal

from drugstore.common import JST, jst_now
from drugstore.domain.models.items import Item
from drugstore.domain.models.sales import Sale, SaleDetail
from drugstore.infra.repositories.sqlite.customers import CustomerRepositoryImpl
from drugstore.infra.repositories.sqlite.items import ItemRepositoryImpl
from drugstore.infra.repositories.sqlite.sales import SaleRepositoryImpl

from tests.integrations import IntegrationTestCase

from .test_customers import IEYASU_CUSTOMER_ID, YOSHINOBU
from .test_items import BUFFERIN_ITEM_ID, OTAISAN_ITEM_ID, SEIROGAN_ITEM_ID

# sql/insert_sale_rows.sqlで登録した徳川慶喜の売上明細
YOSHINOBU_SALE_DETAILS = [
    SaleDetail(
        uuid.UUID("a16cbeba-f3cc-482a-9d41-194bd0a5f14a"),
        Item(
            BUFFERIN_ITEM_ID,
            "バファリン",
            Decimal("500"),
        ),
        3,
    ),
    SaleDetail(
        uuid.UUID("a16cbeba-f3cc-482a-9d41-194bd0a5f14a"),
        Item(
            OTAISAN_ITEM_ID,
            "太田胃酸",
            Decimal("1000"),
        ),
        2,
    ),
    SaleDetail(
        uuid.UUID("a16cbeba-f3cc-482a-9d41-194bd0a5f14a"),
        Item(
            SEIROGAN_ITEM_ID,
            "正露丸",
            Decimal("300"),
        ),
        2,
    ),
]

# sql/insert_sale_rows.sqlで登録した徳川慶喜の売上日時
YOSHINOBU_SOLD_AT = datetime.fromisoformat("2024-06-01T09:32:02+09:00").replace(
    tzinfo=JST
)
# sql/insert_sale_rows.sqlで登録した徳川慶喜の消費税の税率
YOSHINOBU_TAX_RATE = Decimal("0.1")

# sql/insert_sale_rows.sqlで登録した徳川慶喜の売上
YOSHINOBU_SALE = Sale(
    uuid.UUID("a16cbeba-f3cc-482a-9d41-194bd0a5f14a"),
    YOSHINOBU,
    YOSHINOBU_SOLD_AT,
    YOSHINOBU_TAX_RATE,
)
for sale_detail in YOSHINOBU_SALE_DETAILS:
    YOSHINOBU_SALE.add_sale_detail(sale_detail)


def create_sale(conn: sqlite3.Connection) -> Sale:
    """テスト用の売上を構築する。

    Returns:
        Sale: 売上
    """
    sale_id = uuid.uuid4()
    customer_id = IEYASU_CUSTOMER_ID
    customer_repo = CustomerRepositoryImpl(conn)
    customer = customer_repo.by_id(customer_id)
    sold_at = jst_now()
    tax_rate = Decimal("0.1")
    item_repo = ItemRepositoryImpl(conn)
    bufferin = item_repo.by_id(BUFFERIN_ITEM_ID)
    otaisan = item_repo.by_id(OTAISAN_ITEM_ID)
    if bufferin is None or otaisan is None:
        raise Exception("商品をデータベースから取得できませんでした。")
    bufferin_sale_detail = SaleDetail(sale_id, bufferin, 2)
    otaisan_sale_detail = SaleDetail(sale_id, otaisan, 1)
    sale = Sale(sale_id, customer, sold_at, tax_rate)
    sale.add_sale_detail(bufferin_sale_detail)
    sale.add_sale_detail(otaisan_sale_detail)
    return sale


class SaleRepositoryImplTest(IntegrationTestCase):
    """sqlite3の売上リポジトリテスト"""

    def test_list(self) -> None:
        """売上リストを取得できることを確認"""
        sut = SaleRepositoryImpl(self.conn)

        sales = sut.list()

        self.assertEqual(2, len(sales))
        # 徳川家康から売上
        self.assertEqual(2, len(sales[0].sale_details))
        # 徳川慶喜から売上
        self.assertEqual(3, len(sales[1].sale_details))

    def _validate_sale(self, expected: Sale, actual: Sale) -> None:
        # リンターによる警告を抑制
        if actual.customer is None:
            return
        # 売上ID
        self.assertEqual(expected.id, actual.id)
        # 顧客ID
        self.assertEqual(expected.customer.id, actual.customer.id)  # type: ignore
        # 顧客名
        self.assertEqual(expected.customer.name, actual.customer.name)  # type: ignore
        # 会員区分コード
        self.assertEqual(
            expected.customer.membership_type.code,  # type: ignore
            actual.customer.membership_type.code,
        )
        # 会員区分明
        self.assertEqual(
            expected.customer.membership_type.name,  # type: ignore, # type: ignore
            actual.customer.membership_type.name,
        )
        # 販売日時
        self.assertEqual(expected.sold_at, actual.sold_at)
        # 販売明細
        results = [detail in expected.sale_details for detail in actual.sale_details]
        self.assertTrue(all(results))
        # 小計
        self.assertEqual(expected.subtotal, actual.subtotal)
        # 割引率
        self.assertEqual(expected.discount_rate, actual.discount_rate)
        # 割引額
        self.assertEqual(expected.discount_amount, actual.discount_amount)
        # 課税対象額
        self.assertEqual(expected.taxable_amount, actual.taxable_amount)
        # 消費税率
        self.assertEqual(expected.consumption_tax_rate, actual.consumption_tax_rate)
        # 消費税額
        self.assertEqual(expected.consumption_tax_amount, actual.consumption_tax_amount)
        # 合計額
        self.assertEqual(expected.total, actual.total)

    def test_by_id(self) -> None:
        """売上IDを指定して、売上を取得できることを確認"""
        # 準備
        id = uuid.UUID("a16cbeba-f3cc-482a-9d41-194bd0a5f14a")
        sut = SaleRepositoryImpl(self.conn)

        # 実行
        sale = sut.by_id(id)

        # 検証
        self.assertIsNotNone(sale)
        # リンターからの警告を抑制するために型を制限
        if sale is None:
            return
        self._validate_sale(YOSHINOBU_SALE, sale)

    def test_none_is_returned_when_by_absent_id(self) -> None:
        """存在しない売上IDを指定したとき、売上を取得できないことを確認"""
        sut = SaleRepositoryImpl(self.conn)

        sale = sut.by_id(uuid.uuid4())

        self.assertIsNone(sale)

    def test_register(self) -> None:
        """売上を登録できることを確認"""
        # 準備
        self.conn.execute("DELETE FROM sales")
        self.conn.commit()
        expected = create_sale(self.conn)
        sut = SaleRepositoryImpl(self.conn)

        sut.register(expected)
        actual = sut.by_id(expected.id)

        self.assertIsNotNone(actual)
        # リンターからの警告を抑制するために型を制限
        if actual is None:
            return
        self._validate_sale(expected, actual)

    def test_delete(self) -> None:
        """売上を削除できることを確認"""
        id = uuid.UUID("a16cbeba-f3cc-482a-9d41-194bd0a5f14a")
        sut = SaleRepositoryImpl(self.conn)

        sut.delete(id)
        actual = sut.by_id(id)

        self.assertIsNone(actual)
