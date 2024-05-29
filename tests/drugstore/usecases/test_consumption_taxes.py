import copy
import unittest
from decimal import Decimal
from typing import Tuple
from unittest.mock import MagicMock, patch

from drugstore.common import jst_datetime
from drugstore.usecases.consumption_taxes import (
    retrieve_applicable_consumption_tax_rate,
)
from tests.drugstore.utils.test_consumption_tax_manager import THREE_CONSUMPTION_TAXES


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
