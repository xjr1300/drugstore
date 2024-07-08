import abc

from .consumption_taxes import ConsumptionTaxRepository
from .customers import CustomerRepository
from .items import ItemRepository
from .sales import SaleRepository


class RepositoryManager(abc.ABC):
    """リポジトリマネージャー"""

    @abc.abstractmethod
    def customer(self) -> CustomerRepository:
        """顧客リポジトリを返す。

        Returns:
            CustomerRepository: 顧客リポジトリ
        """
        pass

    @abc.abstractmethod
    def item(self) -> ItemRepository:
        """商品リポジトリを返す。

        Returns:
            ItemRepository: 商品リポジトリ
        """
        pass

    @abc.abstractmethod
    def consumption_tax(self) -> ConsumptionTaxRepository:
        """消費税リポジトリを返す。

        Returns:
            ConsumptionTaxRepository: 消費税リポジトリ
        """
        pass

    @abc.abstractmethod
    def sale(self) -> SaleRepository:
        """売上リポジトリを返す。

        Returns:
            SaleRepository: 売上リポジトリ
        """
        pass
