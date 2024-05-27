import uuid
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from drugstore.domain.models.customers import Customer
from drugstore.domain.models.items import Item


@dataclass
class SaleDetail:
    """売上明細"""

    # 売上ID
    id: uuid.UUID
    # 商品
    item: Item
    # 数量
    quantities: int
    # 小計
    amount: Decimal

    def __init__(self, id: uuid.UUID, item: Item, quantities: int) -> None:
        """イニシャライザ

        Args:
            id (uuid.UUID): 売上ID
            item (Item): 商品
            quantities (int): 数量

        Raises:
            ValueError: 販売明細の数量が0以下です。
        """
        if quantities <= 0:
            raise ValueError("販売明細の数量が0以下です。")
        self.id = id
        self.item = item
        self.quantities = quantities
        self.amount = item.unit_price * quantities


@dataclass
class Sale:
    """売上"""

    # 売上ID
    id: uuid.UUID
    # 顧客
    customer: Optional[Customer]
    # 売上日時
    sold_at: datetime
    # 販売明細
    sale_details: List[SaleDetail]
    # 小計
    subtotal: Decimal
    # 割引率
    discount_rate: Decimal
    # 割引額
    discount_amount: Decimal
    # 課税対象額
    taxable_amount: Decimal
    # 消費税率
    consumption_tax_rate: Decimal
    # 消費税額
    consumption_tax_amount: Decimal
    # 合計額
    total: Decimal

    def __init__(
        self,
        customer: Optional[Customer],
        sold_at: datetime,
        consumption_tax_rate: Decimal,
    ) -> None:
        """イニシャライザ

        Args:
            customer (Optional[Customer]): 顧客
            sold_at (datetime): 売上日時
            consumption_tax_rate (Decimal): 消費税率

        TODO: 次の単体テストを実装

        - 妥当な引数でインスタンスを構築できることを確認
        - 売上日時が日本標準時以外の場合に、例外をスローすることを確認
        - 消費税額がドメインで定められた範囲外の場合に、例外をスローすることを確認
        """
