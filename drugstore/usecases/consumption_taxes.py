from datetime import datetime
from decimal import Decimal

from drugstore.domain.models.consumption_taxes import ConsumptionTax
from drugstore.domain.repositories import RepositoryManager
from drugstore.utils.consumption_tax_manager import ConsumptionTaxManager


def retrieve_applicable_consumption_tax_rate(
    repo_manager: RepositoryManager, dt: datetime
) -> Decimal:
    """売上に適用する消費税の税率を返す。

    Args:
        repo_manager (RepositoryManager): リポジトリマネージャー
        dt (datetime): 消費税の税率の基準日時

    Returns:
        Decimal: 売上に適用する消費税の税率
    """
    repo = repo_manager.consumption_tax()
    taxes = repo.list()
    tax_manager = ConsumptionTaxManager(taxes)
    return tax_manager.consumption_tax_rate(dt)


def register_consumption_tax_and_save_list(
    repo_manager: RepositoryManager,
    tax: ConsumptionTax,
) -> None:
    """消費税を消費税リストに追加して、消費税リストを保存する。

    Args:
        repo_manager (RepositoryManager): リポジトリマネージャー
        tax (ConsumptionTax): 追加する消費税

    TODO: 次の単体テストを実装すること
    - 消費税を消費税リストに追加して、消費税リストを入れ替えるメソッドが呼ばれたことを確認
    """  # noqa: E501
    repo = repo_manager.consumption_tax()
    taxes = repo.list()
    tax_manager = ConsumptionTaxManager(taxes)
    tax_manager.add_consumption_tax(tax)
    repo.replace_list(tax_manager.consumption_taxes)
