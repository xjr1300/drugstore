import abc
import uuid
from typing import List, Optional

from drugstore.domain.models.sales import Sale


class SaleRepository(abc.ABC):
    """売上リポジトリ"""

    @abc.abstractmethod
    def list(self) -> List[Sale]:
        """売上のリストを返す。

        Returns:
            List[Sale]: 売上のリスト
        """
        pass

    @abc.abstractmethod
    def by_id(self, id: uuid.UUID) -> Optional[Sale]:
        """指定された売上IDで示される売上を返す。

        Args:
            id (uuid.UUID): 売上ID

        Returns:
            Optional[Sale]: 売上、売上IDが一致する売上が存在しない場合はNone
        """
        pass

    @abc.abstractmethod
    def register(self, sale: Sale) -> None:
        """売上を登録する。

        Args:
            sale (Sale): _description_
        """
        pass

    @abc.abstractmethod
    def delete(self, id: uuid.UUID) -> None:
        """売上を削除する。

        Args:
            id (uuid.UUID): 削除する売上の売上ID
        """
        pass
