import uuid
from dataclasses import dataclass
from datetime import datetime
from decimal import ROUND_DOWN, Decimal
from typing import Callable, List, Optional

from drugstore.common import is_jst_datetime
from drugstore.domain.models.consumption_taxes import validate_consumption_tax_rate
from drugstore.domain.models.customers import Customer
from drugstore.domain.models.items import Item


@dataclass
class SaleDetail:
    """売上明細"""

    # 売上ID
    sale_id: uuid.UUID
    # 商品
    item: Item
    # 数量
    quantities: int
    # 小計
    amount: Decimal

    def __init__(self, sale_id: uuid.UUID, item: Item, quantities: int) -> None:
        """イニシャライザ

        Args:
            sale_id: (uuid.UUID): 売上ID
            item (Item): 商品
            quantities (int): 数量

        Raises:
            ValueError: 販売明細の数量が0以下です。
        """
        if quantities <= 0:
            raise ValueError("販売明細の数量が0以下です。")
        self.sale_id = sale_id
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

    def add_sale_detail(self, sale_detail: SaleDetail) -> None:
        """売上に売上明細を追加する。

        Args:
            sale_detail (SaleDetail): 売上明細

        Raises:
            ValueError: 売上明細に記録されている売上IDが、追加する売上の売上IDと
                異なります。
        """
        # 追加する売上明細の売上IDが、この売上の売上IDと一致するか確認
        if self.id != sale_detail.sale_id:
            raise ValueError(
                "売上明細に記録されている売上IDが、追加する売上の売上IDと異なります。"
            )
        # 追加する売上明細の商品が、すでに登録されている売上明細の商品であるか確認
        func: Callable[[SaleDetail], bool] = lambda sd: sd.item == sale_detail.item
        existence = next(filter(func, self.sale_details), None)
        if existence is None:
            # 登録されていない売上明細の商品の場合は売上明細を登録
            self.sale_details.append(sale_detail)
        else:
            # すでに登録されている売上明細の商品の場合は数量と小計を足す
            existence.quantities += sale_detail.quantities
            existence.amount += sale_detail.amount
        # 小計、割引率、割引額、課税対象額、消費税額、合計を計算してメンバ変数に設定
        self._calculate_overall()

    def _calculate_overall(self) -> None:
        """小計、割引率、割引額、課税対象額、消費税額、合計を計算してメンバ変数に設定する。"""
        # 小計
        self.subtotal = sum([sd.amount for sd in self.sale_details], start=Decimal("0"))
        # 割引率
        self.discount_rate = DiscountRateDeterminer.discount_rate(
            self.customer, self.subtotal
        )
        # 円未満を切り捨てた割引額
        self.discount_amount = (self.subtotal * self.discount_rate).quantize(
            Decimal("0"), ROUND_DOWN
        )
        # 課税対象額
        self.taxable_amount = self.subtotal - self.discount_amount
        # 円未満を切り捨てた消費税額
        self.consumption_tax_amount = (
            self.taxable_amount * self.consumption_tax_rate
        ).quantize(Decimal("0"), ROUND_DOWN)
        # 合計
        self.total = self.taxable_amount + self.consumption_tax_amount


class DiscountRateDeterminer:
    """割引率決定者"""

    @classmethod
    def discount_rate(cls, customer: Optional[Customer], subtotal: Decimal) -> Decimal:
        """割引率を決定する。

        - 会員でない場合の割引率は0%
        - 一般会員で小計が3,000円未満の場合の割引率は5%、小計が3,000円以上の場合は10%
        - 特別会員で小計が3,000円未満の場合の割引率は10%、小計が3,000円以上の場合は20%

        Args:
            customer (Optional[Customer]): 顧客
            subtotal (Decimal): 小計

        Returns:
            Decimal: 割引率
        """
        if customer is None:
            # 会員でない場合
            return Decimal("0.0")
        if customer.is_general_member():
            # 一般会員の場合
            if subtotal < Decimal("3000"):
                # 小計が3,000円未満の場合
                return Decimal("0.05")
            else:
                # 小計が3,000円以上の場合
                return Decimal("0.10")
        else:
            # 特別会員の場合
            if subtotal < Decimal("3000"):
                # 小計が3,000円未満の場合
                return Decimal("0.10")
            else:
                # 小計が3,000円以上の場合
                return Decimal("0.20")
