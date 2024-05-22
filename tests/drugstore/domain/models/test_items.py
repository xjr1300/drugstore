import unittest
import uuid
from decimal import Decimal

from drugstore.domain.models.items import Item


class ItemTest(unittest.TestCase):
    """商品テストクラス

    TODO: 次の単体テストを実装すること

    - 商品名の先頭に空白文字が含まれている場合に、先頭の空白文字を削除した商品名になっていることを確認
    - 商品名の末尾にに空白文字が含まれている場合に、末尾の空白文字を削除した商品名になっていることを確認
    - 商品名の先頭と末尾に空白文字が含まれている場合に、先頭と末尾の空白文字を削除した商品名になっていることを確認
    - 空文字列の商品名で商品を構築できないことを確認
    - 空白文字だけの商品名で商品を構築できないことを確認
    - 0円より小さい単価で商品を構築できないことを確認
    """  # noqa: E501

    def test_instantiate_item_by_valid_attributes(self) -> None:
        """妥当な属性で商品を構築できることを確認"""
        # 準備
        id = uuid.uuid4()
        name = "正露丸"
        unit_price = Decimal("1000")

        # 実行
        item = Item(id, name, unit_price)

        # 検証
        self.assertEqual(id, item.id)
        self.assertEqual(name, item.name)
        self.assertEqual(1000, item.unit_price)
