from drugstore.infra.repositories.sqlite.consumption_taxes import (
    ConsumptionTaxRepositoryImpl,
    consumption_tax_from_row,
)

from tests.integrations import IntegrationTestCase
from tests.units.drugstore.domain.models.test_consumption_taxes import (
    is_same_consumption_tax_conditions,
)

# 初期データベースに登録されている消費税リスト
INITIAL_CONSUMPTION_TAXES = [
    consumption_tax_from_row(
        (
            "cdbef090-7258-4453-afab-3b1e06129b11",
            "0001-01-01T00:00:00+09:18:59",
            "1989-04-01T00:00:00+09:00",
            0,
        )
    ),
    consumption_tax_from_row(
        (
            "d087c967-e62d-43aa-ac3f-39689e7368df",
            "1989-04-01T00:00:00+09:00",
            "1997-04-01T00:00:00+09:00",
            300,
        )
    ),
    consumption_tax_from_row(
        (
            "dcf0afb7-be3e-41c1-a892-e3db7915ba47",
            "1997-04-01T00:00:00+09:00",
            "2014-04-01T00:00:00+09:00",
            500,
        )
    ),
    consumption_tax_from_row(
        (
            "d71b582f-6e4d-41e9-8b45-2d63a88d8897",
            "2014-04-01T00:00:00+09:00",
            "2019-10-01T00:00:00+09:00",
            800,
        )
    ),
    consumption_tax_from_row(
        (
            "c78b3cf6-a328-449e-85e9-2750fbbeb702",
            "2019-10-01T00:00:00+09:00",
            "9999-12-31T23:59:59.999999+09:00",
            1000,
        )
    ),
]


class ConsumptionTaxRepositoryImplTest(IntegrationTestCase):
    """sqlite3の具象消費税リポジトリテスト"""

    def test_list(self) -> None:
        """消費税リストを取得できることを確認"""
        sut = ConsumptionTaxRepositoryImpl(self.conn)

        actual_list = sut.list()

        self.assertEqual(5, len(actual_list))
        for expected, actual in zip(INITIAL_CONSUMPTION_TAXES, actual_list):
            self.assertTrue(is_same_consumption_tax_conditions(expected, actual))

    def test_replace_list(self) -> None:
        """消費税リストを入れ替えられることを確認"""
        expected_list = [
            consumption_tax_from_row(
                (
                    "cdbef090-7258-4453-afab-3b1e06129b11",
                    "0001-01-01T00:00:00+09:18:59",
                    "2000-01-01T00:00:00+09:00",
                    0,
                )
            ),
            consumption_tax_from_row(
                (
                    "d087c967-e62d-43aa-ac3f-39689e7368df",
                    "2000-01-01T00:00:00+09:00",
                    "2010-01-01T00:00:00+09:00",
                    500,
                )
            ),
            consumption_tax_from_row(
                (
                    "dcf0afb7-be3e-41c1-a892-e3db7915ba47",
                    "2010-01-01T00:00:00+09:00",
                    "9999-12-31T23:59:59.999999+09:00",
                    1000,
                )
            ),
        ]
        sut = ConsumptionTaxRepositoryImpl(self.conn)

        sut.replace_list(expected_list)
        actual_list = sut.list()

        self.assertEqual(3, len(actual_list))
        for expected, actual in zip(expected_list, actual_list):
            self.assertTrue(is_same_consumption_tax_conditions(expected, actual))
