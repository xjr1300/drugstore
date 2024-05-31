import uuid

from drugstore.domain.models.customers import Customer
from drugstore.domain.models.membership_types import MembershipType
from drugstore.infra.repositories.sqlite.customers import CustomerRepositoryImpl

from tests.integrations import IntegrationTestCase

# sql/insert_customer_rows.sqlで登録した徳川家康の顧客ID
IEYASU_CUSTOMER_ID = uuid.UUID("a67cd437-50fd-4667-a54e-5a5f09025359")


class CustomerRepositoryImplTest(IntegrationTestCase):
    """sqlite3の具象顧客リポジトリテスト"""

    def test_list(self) -> None:
        """顧客のリストを取得できることを確認"""
        repo = CustomerRepositoryImpl(self.conn)

        customers = repo.list()

        self.assertEqual(2, len(customers))

    def test_by_id_return_customer_with_valid_customer_id(self) -> None:
        """有効な顧客IDを指定したとき、顧客を取得できることを確認"""
        repo = CustomerRepositoryImpl(self.conn)

        customer = repo.by_id(IEYASU_CUSTOMER_ID)
        self.assertIsNotNone(customer)
        if customer is None:
            return
        self.assertEqual("徳川家康", customer.name)
        self.assertEqual(1, customer.membership_type.code)
        self.assertEqual("一般会員", customer.membership_type.name)

    def test_by_id_return_none_with_invalid_customer_id(self) -> None:
        """無効な顧客IDを指定したとき、Noneを返すことを確認"""
        repo = CustomerRepositoryImpl(self.conn)

        customer = repo.by_id(uuid.uuid4())

        self.assertIsNone(customer)

    def test_register(self) -> None:
        """顧客を登録できることを確認"""
        repo = CustomerRepositoryImpl(self.conn)
        general_membership = MembershipType.general_membership_type()
        customer = Customer(uuid.uuid4(), "徳川秀忠", general_membership)

        repo.register(customer)
        registered = repo.by_id(customer.id)

        self.assertIsNotNone(registered)
        if registered is None:
            return
        self.assertEqual(customer.id, registered.id)
        self.assertEqual(customer.name, registered.name)
        self.assertEqual(customer.membership_type, registered.membership_type)

    def test_update(self) -> None:
        """顧客を更新できることを確認"""
        repo = CustomerRepositoryImpl(self.conn)
        special_membership = MembershipType.special_membership_type()
        customer = Customer(IEYASU_CUSTOMER_ID, "徳川家光", special_membership)

        repo.update(customer)
        updated = repo.by_id(customer.id)

        self.assertIsNotNone(updated)
        if updated is None:
            return
        self.assertEqual(customer.id, updated.id)
        self.assertEqual(customer.name, updated.name)
        self.assertEqual(customer.membership_type, updated.membership_type)

    def test_delete(self) -> None:
        """顧客を削除できることを確認"""
        repo = CustomerRepositoryImpl(self.conn)

        repo.delete(IEYASU_CUSTOMER_ID)
        deleted = repo.by_id(IEYASU_CUSTOMER_ID)

        self.assertIsNone(deleted)
