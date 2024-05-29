import abc
import uuid
from typing import List, Optional

from drugstore.domain.models.customers import Customer


class CustomerRepository(abc.ABC):
    """顧客リポジトリ"""

    @abc.abstractmethod
    def list(self) -> List[Customer]:
        """顧客のリストを返す。

        Returns:
            List[Customer]: 顧客のリスト
        """
        pass

    @abc.abstractmethod
    def by_id(self, id: uuid.UUID) -> Optional[Customer]:
        """指定された顧客IDで示される顧客を返す。

        Args:
            id (uuid.UUID): 顧客ID

        Returns:
            Optional[Customer]: 顧客、顧客IDが一致する顧客が存在しない場合はNone
        """
        pass

    @abc.abstractmethod
    def register(self, customer: Customer) -> None:
        """顧客を登録する。

        Args:
            customer (Customer): _description_
        """
        pass

    @abc.abstractmethod
    def update(self, customer: Customer) -> None:
        """顧客を更新する。

        Args:
            customer (Customer): 更新する顧客
        """
        pass

    @abc.abstractmethod
    def delete(self, id: uuid.UUID) -> None:
        """顧客を削除する。

        Args:
            id (uuid.UUID): 削除する顧客の顧客ID
        """
        pass
