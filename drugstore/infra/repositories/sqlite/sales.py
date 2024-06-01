import sqlite3
import uuid
from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

from drugstore.common import JST
from drugstore.domain.models.customers import Customer
from drugstore.domain.models.items import Item
from drugstore.domain.models.membership_types import MembershipType
from drugstore.domain.models.sales import Sale, SaleDetail
from drugstore.domain.repositories.sales import SaleRepository

SaleRow = Tuple[
    str,  # 0: 売上ID
    Optional[str],  # 1: 顧客ID
    Optional[str],  # 2: 顧客名
    Optional[int],  # 3: 会員区分コード
    Optional[str],  # 4: 会員区分名
    str,  # 5: 売上日時
    str,  # 6: 商品ID
    str,  # 7: 商品名
    int,  # 8: 単価
    int,  # 9: 数量
    int,  # 10: 消費税率(*10000)
]


@dataclass
class RawSaleDetail:  # noqa: D101
    # 売上ID
    id: uuid.UUID
    # 顧客ID
    customer_id: Optional[uuid.UUID]
    # 顧客名
    customer_name: Optional[str]
    # 会員区分コード
    membership_type_code: Optional[int]
    # 会員区分名
    membership_type_name: Optional[str]
    # 売上日時
    sold_dt: datetime
    # 商品ID
    item_id: uuid.UUID
    # 商品名
    item_name: str
    # 商品単価
    item_unit_price: Decimal
    # 売上明細数量
    detail_quantities: int
    # 消費税率
    consumption_tax_rate: Decimal

    def __init__(self, row: SaleRow) -> None:  # noqa: D107
        self.sale_id = uuid.UUID(row[0])
        self.customer_id = uuid.UUID(row[1]) if row[1] else None
        self.customer_name = row[2]
        self.membership_type_code = row[3]
        self.membership_type_name = row[4]
        self.sold_dt = datetime.fromisoformat(row[5]).replace(tzinfo=JST)
        self.item_id = uuid.UUID(row[6])
        self.item_name = row[7]
        self.item_unit_price = Decimal(row[8])
        self.sale_detail_quantities = row[9]
        self.consumption_tax_rate = Decimal(row[10]) / 10_000

    def create_sale(self) -> Sale:  # noqa: D102
        id = uuid.uuid4()
        customer = (
            Customer(
                self.customer_id,
                self.customer_name,  # type: ignore
                MembershipType(
                    self.membership_type_code,  # type: ignore
                    self.membership_type_name,  # type: ignore
                ),
            )
            if self.customer_id
            else None
        )
        sale = Sale(id, customer, self.sold_dt, self.consumption_tax_rate)
        sale.id = self.sale_id
        return sale

    def create_sale_detail(self) -> SaleDetail:  # noqa: D102
        return SaleDetail(
            self.sale_id,
            Item(self.item_id, self.item_name, self.item_unit_price),
            self.sale_detail_quantities,
        )


QUERY_RAW_SALE_DETAIL_SQL = """
    SELECT
        s.id,
        s.customer_id,
        c.name customer_name,
        c.membership_type_code,
        m.name membership_type_name,
        s.sold_at,
        d.item_id,
        i.name item_name,
        i.unit_price,
        d.quantities,
        s.consumption_tax_rate
    FROM sales s
    LEFT OUTER JOIN customers c ON s.customer_id = c.id
    LEFT OUTER JOIN membership_types m ON c.membership_type_code = m.code
    INNER JOIN sale_details d ON d.sale_id = s.id
    INNER JOIN items i ON i.id = d.item_id
"""


class SaleRepositoryImpl(SaleRepository):
    """売上ポジトリ"""

    def __init__(self, conn: sqlite3.Connection) -> None:
        """イニシャライザ"""
        super().__init__()
        self.conn = conn

    def list(self) -> List[Sale]:
        """売上のリストを返す。

        Returns:
            List[Sale]: 売上のリスト
        """
        # 売上日時、売上ID、商品名の昇順で取得
        sql = f"""
            {QUERY_RAW_SALE_DETAIL_SQL}
            ORDER BY s.sold_at, s.id, i.name
        """
        cursor = self.conn.execute(sql)
        sales: Dict[uuid.UUID, Sale] = OrderedDict()
        for row in cursor:
            raw_sale_detail = RawSaleDetail(row)
            if raw_sale_detail.sale_id in sales.keys():
                sales[raw_sale_detail.sale_id].add_sale_detail(
                    raw_sale_detail.create_sale_detail()
                )
            else:
                sales[raw_sale_detail.sale_id] = raw_sale_detail.create_sale()
                sales[raw_sale_detail.sale_id].add_sale_detail(
                    raw_sale_detail.create_sale_detail()
                )
        return list(sales.values())

    def by_id(self, id: uuid.UUID) -> Optional[Sale]:
        """指定された売上IDで示される売上を返す。

        Args:
            id (uuid.UUID): 売上ID

        Returns:
            Optional[Sale]: 売上、売上IDが一致する売上が存在しない場合はNone
        """
        # 売上日時、売上ID、商品名の昇順で取得
        sql = f"""
            {QUERY_RAW_SALE_DETAIL_SQL}
            WHERE s.id = ?
            ORDER BY s.sold_at, s.id, i.name
        """
        cursor = self.conn.execute(sql, (str(id),))
        try:
            row = next(cursor)
        except StopIteration:
            return None
        raw_sale_detail = RawSaleDetail(row)
        sale = raw_sale_detail.create_sale()
        sale.add_sale_detail(raw_sale_detail.create_sale_detail())
        for row in cursor:
            raw_sale_detail = RawSaleDetail(row)
            sale.add_sale_detail(raw_sale_detail.create_sale_detail())
        return sale

    def register(self, sale: Sale) -> None:
        """売上を登録する。

        Args:
            sale (Sale): _description_
        """
        # 売上を登録
        sql = """
            INSERT INTO sales (
                id, customer_id, sold_at, subtotal, discount_rate, discount_amount,
                taxable_amount, consumption_tax_rate, consumption_tax_amount, total
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        self.conn.execute(
            sql,
            (
                str(sale.id),
                str(sale.customer.id) if sale.customer else None,
                sale.sold_at.isoformat(),
                int(sale.subtotal),
                int(sale.discount_rate * 10_000),
                int(sale.discount_amount),
                int(sale.taxable_amount),
                int(sale.consumption_tax_rate * 10_000),
                int(sale.consumption_tax_amount),
                int(sale.total),
            ),
        )
        # 売上明細を登録
        sql = """
            INSERT INTO sale_details (sale_id, item_id, quantities, amount)
            VALUES (?, ?, ?, ?)
        """
        for detail in sale.sale_details:
            self.conn.execute(
                sql,
                (
                    str(sale.id),
                    str(detail.item.id),
                    detail.quantities,
                    int(detail.amount),
                ),
            )
        # コミット
        self.conn.commit()

    def delete(self, id: uuid.UUID) -> None:
        """売上を削除する。

        Args:
            id (uuid.UUID): 削除する売上の売上ID
        """
        sql = "DELETE FROM sales WHERE id = ?"
        self.conn.execute(sql, (str(id),))
        self.conn.commit()
