import unittest

from drugstore.domain.models.membership_types import MembershipType


class MembershipTypeTest(unittest.TestCase):
    """会員区分テスト"""

    def test_instantiate_general_membership_type(self) -> None:
        """一般会員をインスタンス化できることを確認"""
        code = 1
        name = "一般会員"

        sut = MembershipType(code, name)

        self.assertEqual(code, sut.code)
        self.assertEqual(name, sut.name)

    def test_instantiate_special_membership_type(self) -> None:
        """特別会員をインスタンス化できることを確認"""
        code = 2
        name = "特別会員"

        sut = MembershipType(code, name)

        self.assertEqual(code, sut.code)
        self.assertEqual(name, sut.name)

    def test_can_not_instantiate_membership_type_by_invalid_code(self) -> None:
        """会員区分コードに1と2以外の値を指定して、会員区分をインスタンス化できないことを確認"""
        codes = [0, 3]
        name = "一般会員"

        for code in codes:
            with self.assertRaises(ValueError):
                _ = MembershipType(code, name)

    def test_can_not_instantiate_membership_type_by_invalid_name(self) -> None:
        """会員区分名に一般会員と特別会員以外の値を指定して、会員区分をインスタンス化できないことを確認"""
        code = 1
        name = "優待会員"

        with self.assertRaises(ValueError):
            _ = MembershipType(code, name)

    def test_can_not_instantiate_membership_type_by_valid_code_and_name_but_wrong_pairs(
        self,
    ) -> None:
        """妥当な会員区分コードと妥当な会員区分名の誤った組み合わせで、会員区分をインスタンス化できないことを確認"""
        data = [(1, "特別会員"), (2, "一般会員")]

        for code, name in data:
            with self.assertRaises(ValueError):
                _ = MembershipType(code, name)
