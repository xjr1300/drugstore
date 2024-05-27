import uuid
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from drugstore.common import is_jst_datetime
from drugstore.domain.models.consumption_taxes import validate_consumption_tax_rate
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
            id: (uuid.UUID): 売上ID
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

        Raises:
            ValueError: 売上日は日本標準時で指定してください。
            ValueError: 消費税の税率が0.0未満または1.0以上です。
        """
        if not is_jst_datetime(sold_at):
            raise ValueError("売上日は日本標準時で指定してください。")
        if not validate_consumption_tax_rate(consumption_tax_rate):
            raise ValueError("消費税の税率が0.0未満または1.0以上です。")
        self.id = uuid.uuid4()
        self.customer = customer
        self.sold_at = sold_at
        self.sale_details = []
        self.subtotal = Decimal("0")
        self.discount_rate = Decimal("0.0")
        self.discount_amount = Decimal("0")
        self.consumption_tax_rate = consumption_tax_rate
        self.consumption_tax_amount = Decimal("0")
        self.total = Decimal("0")
