import uuid
from decimal import Decimal

from drugstore.domain.models.items import Item
from drugstore.infra.repositories.sqlite.items import ItemRepositoryImpl

from tests.integrations import IntegrationTestCase

# sql/insert_item_rows.sqlで登録した正露丸の商品ID
SEIROGAN_ITEM_ID = uuid.UUID("6e0d4fbe-cafe-4af7-bc95-a564b5029322")


class ItemRepositoryImplTest(IntegrationTestCase):
    """sqlite3の商品リポジトリテスト"""

    def test_list(self) -> None:
        """商品のリストを取得できることを確認"""
        repo = ItemRepositoryImpl(self.conn)

        items = repo.list()

        self.assertEqual(3, len(items))

    def test_by_id_return_item_with_valid_item_id(self) -> None:
        """有効な商品IDを指定したとき、商品を取得できることを確認"""
        repo = ItemRepositoryImpl(self.conn)

        item = repo.by_id(SEIROGAN_ITEM_ID)
        self.assertIsNotNone(item)
        # リンターからの警告を抑制するために型を制限
        if item is None:
            return
        self.assertEqual("正露丸", item.name)
        self.assertEqual(Decimal("300"), item.unit_price)

    def test_by_id_return_none_with_invalid_item_id(self) -> None:
        """無効な商品IDを指定したとき、Noneを返すことを確認"""
        repo = ItemRepositoryImpl(self.conn)

        item = repo.by_id(uuid.uuid4())

        self.assertIsNone(item)

    def test_register(self) -> None:
        """商品を登録できることを確認"""
        repo = ItemRepositoryImpl(self.conn)
        item = Item(uuid.uuid4(), "イソジン", Decimal("600"))

        repo.register(item)
        registered = repo.by_id(item.id)

        self.assertIsNotNone(registered)
        # リンターからの警告を抑制するために型を制限
        if registered is None:
            return
        self.assertEqual(item.id, registered.id)
        self.assertEqual(item.name, registered.name)
        self.assertEqual(item.unit_price, registered.unit_price)

    def test_update(self) -> None:
        """商品を更新できることを確認"""
        repo = ItemRepositoryImpl(self.conn)
        item = Item(SEIROGAN_ITEM_ID, "イソジン", Decimal("600"))

        repo.update(item)
        updated = repo.by_id(item.id)

        self.assertIsNotNone(updated)
        # リンターからの警告を抑制するために型を制限
        if updated is None:
            return
        self.assertEqual(item.id, updated.id)
        self.assertEqual(item.name, updated.name)
        self.assertEqual(item.unit_price, updated.unit_price)

    def test_delete(self) -> None:
        """商品を削除できることを確認"""
        repo = ItemRepositoryImpl(self.conn)

        repo.delete(SEIROGAN_ITEM_ID)
        deleted = repo.by_id(SEIROGAN_ITEM_ID)

        self.assertIsNone(deleted)
