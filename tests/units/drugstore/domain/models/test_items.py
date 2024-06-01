import unittest
import uuid
from decimal import Decimal

from drugstore.domain.models.items import Item


class ItemTest(unittest.TestCase):
    """商品テストクラス"""

    def test_instantiate_item_by_valid_attributes(self) -> None:
        """妥当な属性で商品を構築できることを確認"""
        # 準備
        id = uuid.uuid4()
        name = "正露丸"
        unit_price = Decimal("1000")

        # 実行
        sut = Item(id, name, unit_price)

        # 検証
        self.assertEqual(id, sut.id)
        self.assertEqual(name, sut.name)
        self.assertEqual(1000, sut.unit_price)

    def test_instantiate_item_by_removing_blank_chars_at_beginning_of_the_item_name(
        self,
    ) -> None:
        """商品名の先頭に空白文字が含まれている場合に、先頭の空白文字を削除した商品名になっていることを確認"""
        # 準備
        id = uuid.uuid4()
        name = "    正露丸"
        unit_price = Decimal("1000")

        # 実行
        sut = Item(id, name, unit_price)

        # 検証
        self.assertEqual("正露丸", sut.name)

    def test_instantiate_item_by_removing_blank_chars_at_both_end_of_the_item_name(
        self,
    ) -> None:
        """商品名の先頭と末尾に空白文字が含まれている場合に、先頭と末尾の空白文字を削除した商品名になっていることを確認"""
        # 準備
        id = uuid.uuid4()
        name = "    正露丸    "
        unit_price = Decimal("1000")

        # 実行
        sut = Item(id, name, unit_price)

        # 検証
        self.assertEqual("正露丸", sut.name)

    def test_instantiate_item_by_removing_blank_chars_at_end_of_the_item_name(
        self,
    ) -> None:
        """商品名の末尾に空白文字が含まれている場合に、先頭の空白文字を削除した商品名になっていることを確認"""
        # 準備
        id = uuid.uuid4()
        name = "正露丸    "
        unit_price = Decimal("1000")

        # 実行
        sut = Item(id, name, unit_price)

        # 検証
        self.assertEqual("正露丸", sut.name)

    def test_can_not_instantiate_item_by_empty_item_name(self) -> None:
        """空文字列の商品名で商品を構築できないことを確認"""
        # 準備
        id = uuid.uuid4()
        name = ""
        unit_price = Decimal("1000")

        # 実行と検証
        with self.assertRaises(ValueError):
            _ = Item(id, name, unit_price)

    def test_can_not_instantiate_item_by_blank_chars_item_name(self) -> None:
        """空白文字だけの商品名で商品を構築できないことを確認"""
        # 準備
        id = uuid.uuid4()
        name = "    "
        unit_price = Decimal("1000")

        # 実行と検証
        with self.assertRaises(ValueError):
            _ = Item(id, name, unit_price)

    def test_can_not_instantiate_item_if_unit_price_is_less_than_zero(self) -> None:
        """0円より小さい単価で商品を構築できないことを確認"""
        # 準備
        id = uuid.uuid4()
        name = "正露丸"
        unit_price = Decimal("-1")

        # 実行と検証
        with self.assertRaises(ValueError):
            _ = Item(id, name, unit_price)


def create_seirogan(unit_price: Decimal) -> Item:
    """正露丸を作成する。

    Args:
        unit_price (Decimal): 単価

    Returns:
        Item: 正露丸を表現する商品
    """
    return Item(uuid.uuid4(), "正露丸", unit_price)


def create_bufferin(unit_price: Decimal) -> Item:
    """バファリンを作成する。

    Args:
        unit_price (Decimal): 単価

    Returns:
        Item: バファリンを表現する商品
    """
    return Item(uuid.uuid4(), "バファリン", unit_price)
