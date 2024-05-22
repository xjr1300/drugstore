import uuid
from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Item:
    """商品"""

    # 商品ID
    id: uuid.UUID
    # 商品名
    name: str
    # 単価
    unit_price: Decimal
