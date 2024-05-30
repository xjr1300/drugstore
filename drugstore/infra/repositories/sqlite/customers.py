import sqlite3
import uuid
from typing import List, Optional, Tuple

from drugstore.domain.models.customers import Customer
from drugstore.domain.models.membership_types import MembershipType
from drugstore.domain.repositories.customers import CustomerRepository


def customer_from_row(row: Tuple[str, str, int, str]) -> Customer:
    """顧客ID、顧客名、単価の順に格納したタプルから顧客を返す。

    Args:
        row (Tuple[str, str, int, str]): 顧客ID、顧客名、会員区分コード, 会員区分名の順
            に格納したタプル

    Returns:
        Customer: 顧客
    """
    membership_type = MembershipType(row[2], row[3])
    return Customer(uuid.UUID(row[0]), row[1], membership_type)


class CustomerRepositoryImpl(CustomerRepository):
    """顧客リポジトリ"""

    query_sql = """
        SELECT
            c.id, c.name, c.membership_type_code, m.name membership_type_name
        FROM customers c
        INNER JOIN membership_types m
            ON c.membership_type_code = m.code
    """

    def __init__(self, conn: sqlite3.Connection) -> None:
        """イニシャライザ"""
        super().__init__()
        self.conn = conn

    def list(self) -> List[Customer]:
        """顧客のリストを返す。

        Returns:
            List[Customer]: 顧客のリスト
        """
        sql = f"{self.query_sql} ORDER BY c.name"
        cursor = self.conn.execute(sql)
        customers: List[Customer] = []
        for row in cursor:
            customers.append(customer_from_row(row))
        return customers

    def by_id(self, id: uuid.UUID) -> Optional[Customer]:
        """指定された顧客IDで示される顧客を返す。

        Args:
            id (uuid.UUID): 顧客ID

        Returns:
            Optional[Customer]: 顧客、顧客IDが一致する顧客が存在しない場合はNone
        """
        sql = f"{self.query_sql} WHERE c.id = ? ORDER BY c.name"
        cursor = self.conn.execute(sql, (str(id),))
        row = cursor.fetchone()
        if row:
            return customer_from_row(row)
        else:
            return None

    def register(self, customer: Customer) -> None:
        """顧客を登録する。

        Args:
            customer (Customer): 顧客
        """
        sql = "INSERT INTO customers (id, name, membership_type_code) VALUES (?, ?, ?)"
        self.conn.execute(
            sql,
            (
                str(customer.id),
                customer.name,
                customer.membership_type.code,
            ),
        )
        self.conn.commit()

    def update(self, customer: Customer) -> None:
        """顧客を更新する。

        Args:
            customer (Customer): 更新する顧客
        """
        sql = """
            UPDATE customers
            SET name = ?,
                membership_type_code = ?
            WHERE id = ?"""
        self.conn.execute(
            sql,
            (
                customer.name,
                customer.membership_type.code,
                str(customer.id),
            ),
        )
        self.conn.commit()
        pass

    def delete(self, id: uuid.UUID) -> None:
        """顧客を削除する。

        Args:
            id (uuid.UUID): 削除する顧客の顧客ID
        """
        sql = "DELETE FROM customers WHERE id = ?"
        self.conn.execute(sql, (str(id),))
        self.conn.commit()
