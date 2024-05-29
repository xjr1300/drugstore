import abc
import uuid
from typing import List, Optional

from drugstore.domain.models.items import Item


class ItemRepository(abc.ABC):
    """商品リポジトリ"""

    @abc.abstractmethod
    def list(self) -> List[Item]:
        """商品のリストを返す。

        Returns:
            List[Item]: 商品のリスト
        """
        pass

    @abc.abstractmethod
    def by_id(self, id: uuid.UUID) -> Optional[Item]:
        """指定された商品IDで示される商品を返す。

        Args:
            id (uuid.UUID): 商品ID

        Returns:
            Optional[Item]: 商品、商品IDが一致する商品が存在しない場合はNone
        """
        pass

    @abc.abstractmethod
    def register(self, item: Item) -> None:
        """商品を登録する。

        Args:
            item (Item): _description_
        """
        pass

    @abc.abstractmethod
    def update(self, item: Item) -> None:
        """商品を更新する。

        Args:
            item (Item): 更新する商品
        """
        pass

    @abc.abstractmethod
    def delete(self, id: uuid.UUID) -> None:
        """商品を削除する。

        Args:
            id (uuid.UUID): 削除する商品の商品ID
        """
        pass
