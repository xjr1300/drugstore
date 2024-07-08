import sqlite3
import uuid
from decimal import Decimal
from typing import List, Optional, Tuple

from drugstore.domain.models.items import Item
from drugstore.domain.repositories.items import ItemRepository


def item_from_row(row: Tuple[str, str, int]) -> Item:
    """商品ID、商品名、単価の順に格納したタプルから商品を返す。

    Args:
        row (Tuple[str, str, int]): 商品ID、商品名、単価の順に格納したタプル

    Returns:
        Item: 商品
    """
    return Item(uuid.UUID(row[0]), row[1], Decimal(row[2]))


class ItemRepositoryImpl(ItemRepository):
    """商品リポジトリ"""

    def __init__(self, conn: sqlite3.Connection) -> None:
        """イニシャライザ"""
        super().__init__()
        self.conn = conn

    def list(self) -> List[Item]:
        """商品のリストを返す。

        Returns:
            List[Item]: 商品のリスト
        """
        sql = "SELECT id, name, unit_price FROM items ORDER BY name"
        cursor = self.conn.execute(sql)
        items: List[Item] = []
        for row in cursor:
            items.append(item_from_row(row))
        return items

    def by_id(self, id: uuid.UUID) -> Optional[Item]:
        """指定された商品IDで示される商品を返す。

        Args:
            id (uuid.UUID): 商品ID

        Returns:
            Optional[Item]: 商品、商品IDが一致する商品が存在しない場合はNone
        """
        sql = "SELECT id, name, unit_price FROM items WHERE id = ?"
        cursor = self.conn.execute(sql, (str(id),))
        row = cursor.fetchone()
        if row:
            return item_from_row(row)
        else:
            return None

    def register(self, item: Item) -> None:
        """商品を登録する。

        Args:
            item (Item): 商品
        """
        sql = "INSERT INTO items (id, name, unit_price) VALUES (?, ?, ?)"
        self.conn.execute(
            sql,
            (
                str(item.id),
                item.name,
                int(item.unit_price),
            ),
        )
        self.conn.commit()

    def update(self, item: Item) -> None:
        """商品を更新する。

        Args:
            item (Item): 更新する商品
        """
        sql = """
            UPDATE items
            SET name = ?,
                unit_price = ?
            WHERE id = ?"""
        self.conn.execute(
            sql,
            (
                item.name,
                int(item.unit_price),
                str(item.id),
            ),
        )
        self.conn.commit()

    def delete(self, id: uuid.UUID) -> None:
        """商品を削除する。

        Args:
            id (uuid.UUID): 削除する商品の商品ID
        """
        sql = "DELETE FROM items WHERE id = ?"
        self.conn.execute(sql, (str(id),))
        self.conn.commit()
