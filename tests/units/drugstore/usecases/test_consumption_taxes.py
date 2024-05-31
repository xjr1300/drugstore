import copy
import unittest
import uuid
from decimal import Decimal
from typing import Tuple
from unittest.mock import MagicMock, patch

from drugstore.common import jst_datetime
from drugstore.domain.models.consumption_taxes import (
    MAX_CONSUMPTION_TAX_END,
    MIN_CONSUMPTION_TAX_BEGIN,
    ConsumptionTax,
)
from drugstore.usecases.consumption_taxes import (
    register_consumption_tax_and_save_list,
    retrieve_applicable_consumption_tax_rate,
)

from tests.units.drugstore.domain.models.test_consumption_taxes import (
    is_same_consumption_tax_conditions,
)
from tests.units.drugstore.utils.test_consumption_tax_manager import (
    THREE_CONSUMPTION_TAXES,
)


def repository_manager_test_double() -> Tuple[MagicMock, MagicMock]:  # noqa: D103
    """リポジトリマネージャーのテストダブル返す。

    Returns:
        (MagicMock, MagicMock): リポジトリマネージャのテストダブルと、消費税リポジトリの
            テストダブルを格納したタプル
    """
    # 消費税リポジトリのスタブ
    repo_tdbl = MagicMock()
    repo_tdbl.list.return_value = copy.deepcopy(THREE_CONSUMPTION_TAXES)
    # リポジトリマネージャーのスタブ
    repo_manager_tdbl = MagicMock()
    repo_manager_tdbl.consumption_tax.return_value = repo_tdbl
    return repo_manager_tdbl, repo_tdbl


class ConsumptionTaxUsecaseTest(unittest.TestCase):
    """消費税ユースケーステストクラス"""

    def test_retrieve_applicable_consumption_tax_rate(self) -> None:
        """売上に適用する消費税を正しく取得できることを確認"""
        # 準備
        repo_manager_tdbl, _ = repository_manager_test_double()
        dt = jst_datetime(2024, 5, 1)

        # 実行
        with patch(
            "drugstore.domain.repositories.RepositoryManager", repo_manager_tdbl
        ):
            tax = retrieve_applicable_consumption_tax_rate(repo_manager_tdbl, dt)

        # 検証
        self.assertEqual(Decimal("0.1"), tax)

    def test_register_consumption_tax_and_save_list(self) -> None:
        """消費税を消費税リストに追加して、消費税リストを入れ替えるメソッドが呼ばれたことを確認"""
        # 準備
        tax = ConsumptionTax(
            uuid.uuid4(),
            jst_datetime(2024, 5, 1),
            jst_datetime(2024, 6, 1),
            Decimal("0.12"),
        )
        repo_manager_tdbl, repo_tdbl = repository_manager_test_double()
        repo_tdbl.replace_list = MagicMock()
        expected_args = [
            ConsumptionTax(
                THREE_CONSUMPTION_TAXES[0].id,
                MIN_CONSUMPTION_TAX_BEGIN,
                jst_datetime(2024, 4, 1),
                Decimal("0.05"),
            ),
            ConsumptionTax(
                THREE_CONSUMPTION_TAXES[1].id,
                jst_datetime(2024, 4, 1),
                jst_datetime(2024, 5, 1),
                Decimal("0.10"),
            ),
            ConsumptionTax(
                tax.id,
                jst_datetime(2024, 5, 1),
                jst_datetime(2024, 6, 1),
                Decimal("0.12"),
            ),
            ConsumptionTax(
                THREE_CONSUMPTION_TAXES[2].id,
                jst_datetime(2024, 6, 1),
                MAX_CONSUMPTION_TAX_END,
                Decimal("0.15"),
            ),
        ]

        # 実行
        with patch(
            "drugstore.domain.repositories.RepositoryManager", repo_manager_tdbl
        ):
            tax = register_consumption_tax_and_save_list(repo_manager_tdbl, tax)

        # ConsumptionTaxRepositoryのreplace_listメソッドの呼び出しを検証
        self.assertEqual(1, repo_tdbl.replace_list.call_count)
        args = repo_tdbl.replace_list.call_args.args[0]
        self.assertEqual(4, len(args))
        results = [
            is_same_consumption_tax_conditions(a, b)
            for a, b in zip(expected_args, args)
        ]
        self.assertTrue(all(results))
