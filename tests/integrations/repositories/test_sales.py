import uuid
from datetime import datetime
from decimal import Decimal

from drugstore.common import JST
from drugstore.domain.models.items import Item
from drugstore.domain.models.sales import Sale, SaleDetail
from drugstore.infra.repositories.sqlite.sales import SaleRepositoryImpl

from tests.integrations import IntegrationTestCase

YOSHINOBU_SALE_DETAILS = [
    SaleDetail(
        uuid.UUID("a16cbeba-f3cc-482a-9d41-194bd0a5f14a"),
        Item(
            uuid.UUID("0734980b-ca7e-4bf4-81df-39ac95920ce0"),
            "バファリン",
            Decimal("500"),
        ),
        3,
    ),
    SaleDetail(
        uuid.UUID("a16cbeba-f3cc-482a-9d41-194bd0a5f14a"),
        Item(
            uuid.UUID("ef2d7dab-02e7-4680-8e8e-55070f695d8b"),
            "太田胃酸",
            Decimal("1000"),
        ),
        2,
    ),
    SaleDetail(
        uuid.UUID("a16cbeba-f3cc-482a-9d41-194bd0a5f14a"),
        Item(
            uuid.UUID("6e0d4fbe-cafe-4af7-bc95-a564b5029322"),
            "正露丸",
            Decimal("300"),
        ),
        2,
    ),
]


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

    def _validate_sale(self, sale: Sale) -> None:
        # リンターによる警告を抑制
        if sale.customer is None:
            return
        # 販売ID
        self.assertEqual(uuid.UUID("a16cbeba-f3cc-482a-9d41-194bd0a5f14a"), sale.id)
        # 顧客ID
        self.assertEqual(
            uuid.UUID("830f842f-4822-4f73-adf8-3243c71ca0a7"), sale.customer.id
        )
        # 顧客名
        self.assertEqual("徳川慶喜", sale.customer.name)
        # 会員区分コード
        self.assertEqual(2, sale.customer.membership_type.code)
        # 会員区分明
        self.assertEqual("特別会員", sale.customer.membership_type.name)
        # 販売日時
        self.assertEqual(
            datetime.fromisoformat("2024-06-01T09:32:02+09:00").replace(tzinfo=JST),
            sale.sold_at,
        )
        # 販売明細
        results = [detail in YOSHINOBU_SALE_DETAILS for detail in sale.sale_details]
        self.assertTrue(all(results))
        # 小計
        self.assertEqual(Decimal("4100"), sale.subtotal)
        # 割引率
        self.assertEqual(Decimal("0.2"), sale.discount_rate)
        # 割引額
        self.assertEqual(Decimal("820"), sale.discount_amount)
        # 課税対象額
        self.assertEqual(Decimal("3280"), sale.taxable_amount)
        # 消費税率
        self.assertEqual(Decimal("0.1"), sale.consumption_tax_rate)
        # 消費税額
        self.assertEqual(Decimal("328"), sale.consumption_tax_amount)
        # 合計額
        self.assertEqual(Decimal("3608"), sale.total)

    def test_by_id(self) -> None:
        """売上IDを指定して、売上を取得できることを確認"""
        # 準備
        id = uuid.UUID("a16cbeba-f3cc-482a-9d41-194bd0a5f14a")
        sut = SaleRepositoryImpl(self.conn)

        # 実行
        sale = sut.by_id(id)

        # 検証
        self.assertIsNotNone(sale)
        # リンターによる警告を抑制
        if sale is None:
            return
        self._validate_sale(sale)

    def test_none_is_returned_when_by_absent_id(self) -> None:
        """存在しない売上IDを指定したとき、売上を取得できないことを確認"""
        sut = SaleRepositoryImpl(self.conn)

        sale = sut.by_id(uuid.uuid4())

        self.assertIsNone(sale)

    def test_register(self) -> None:
        """売上を登録できることを確認"""
        # 準備
        id = uuid.UUID("a16cbeba-f3cc-482a-9d41-194bd0a5f14a")
        sut = SaleRepositoryImpl(self.conn)
        expected = sut.by_id(id)
        if expected is None:
            raise Exception("an unexpected error occurred")
        self.conn.execute("DELETE FROM sales")
        self.conn.commit()

        sut.register(expected)
        actual = sut.by_id(expected.id)

        self.assertIsNotNone(actual)
        # リンターによる警告を抑制
        if actual is None:
            return
        self._validate_sale(actual)

    def test_delete(self) -> None:
        """売上を削除できることを確認"""
        id = uuid.UUID("a16cbeba-f3cc-482a-9d41-194bd0a5f14a")
        sut = SaleRepositoryImpl(self.conn)

        sut.delete(id)
        actual = sut.by_id(id)

        self.assertIsNone(actual)
