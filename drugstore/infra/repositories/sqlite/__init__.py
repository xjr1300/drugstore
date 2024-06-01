import sqlite3

from drugstore.domain.repositories import RepositoryManager
from drugstore.domain.repositories.consumption_taxes import ConsumptionTaxRepository
from drugstore.domain.repositories.customers import CustomerRepository
from drugstore.domain.repositories.items import ItemRepository
from drugstore.domain.repositories.sales import SaleRepository
from drugstore.infra.repositories.sqlite.consumption_taxes import (
    ConsumptionTaxRepositoryImpl,
)
from drugstore.infra.repositories.sqlite.customers import CustomerRepositoryImpl
from drugstore.infra.repositories.sqlite.items import ItemRepositoryImpl
from drugstore.infra.repositories.sqlite.sales import SaleRepositoryImpl


class RepositoryManagerImpl(RepositoryManager):
    """sqliteのリポジトリマネージャー"""

    def __init__(self, conn: sqlite3.Connection) -> None:
        """イニシャライザ

        Args:
            conn (sqlite3.Connection): データベースコネクション
        """
        self.conn = conn

    def customer(self) -> CustomerRepository:
        """顧客リポジトリを返す。

        Returns:
            CustomerRepository: 顧客リポジトリ
        """
        return CustomerRepositoryImpl(self.conn)

    def item(self) -> ItemRepository:
        """商品リポジトリを返す。

        Returns:
            ItemRepository: 商品リポジトリ
        """
        return ItemRepositoryImpl(self.conn)

    def consumption_tax(self) -> ConsumptionTaxRepository:
        """消費税リポジトリを返す。

        Returns:
            ConsumptionTaxRepository: 消費税リポジトリ
        """
        return ConsumptionTaxRepositoryImpl(self.conn)

    def sale(self) -> SaleRepository:
        """売上リポジトリを返す。

        Returns:
            SaleRepository: 売上リポジトリ
        """
        return SaleRepositoryImpl(self.conn)
