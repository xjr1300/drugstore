import unittest
import uuid

from drugstore.domain.models.customers import Customer
from drugstore.domain.models.membership_types import MembershipType


class CustomerTest(unittest.TestCase):
    """顧客テストクラス"""

    def test_instantiate_customer_by_valid_attrs(self) -> None:
        """妥当な属性で顧客をインスタンス化できることを確認"""
        id = uuid.uuid4()
        name = "徳川　家康"
        membership_type = MembershipType.general_membership_type()

        sut = Customer(id, name, membership_type)

        self.assertEqual(id, sut.id)
        self.assertEqual(name, sut.name)
        self.assertEqual(membership_type, sut.membership_type)

    def test_instantiate_customer_by_removing_blank_chars_of_the_names(
        self,
    ) -> None:
        """先頭または末尾の空白文字を除去した顧客名で、顧客をインスタンス化できることを確認"""
        id = uuid.uuid4()
        names = [" 徳川　家康", "徳川　家康 ", " 徳川　家康 "]
        membership_type = MembershipType.general_membership_type()
        expected = "徳川　家康"

        for name in names:
            sut = Customer(id, name, membership_type)
            self.assertEqual(expected, sut.name)

    def test_can_not_instantiate_customer_by_blank_names(self) -> None:
        """空白文字の顧客名で、顧客をインスタンス化できないことを確認"""
        id = uuid.uuid4()
        names = [
            "",
            "    ",
        ]
        membership_type = MembershipType.general_membership_type()

        for name in names:
            with self.assertRaises(ValueError):
                _ = Customer(id, name, membership_type)
