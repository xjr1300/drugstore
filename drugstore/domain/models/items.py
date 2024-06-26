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

    def __init__(self, id: uuid.UUID, name: str, unit_price: Decimal) -> None:
        """イニシャライザ

        Args:
            id (uuid.UUID): 商品ID
            name (str): 商品名
            unit_price (Decimal): 商品単価

        Raises:
            ValueError: 商品の商品名が空文字です。
            ValueError: 商品の単価が0円未満です。
        """
        cleaned_name = name.strip()
        if len(cleaned_name) == 0:
            raise ValueError("商品の商品名が空文字です。")
        if unit_price < 0:
            raise ValueError("商品の単価が0円未満です。")
        self.id = id
        self.name = cleaned_name
        self.unit_price = unit_price
