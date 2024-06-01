import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from drugstore.domain.models.sales import Sale, SaleDetail
from drugstore.domain.repositories import RepositoryManager
from drugstore.domain.repositories.items import ItemRepository
from drugstore.utils.consumption_tax_manager import ConsumptionTaxManager


@dataclass
class SoldItem:
    """売上商品と数量"""

    # 売上する商品の商品ID
    id: uuid.UUID
    # 売上数量
    quantities: int


def create_sale_detail(
    item_repo: ItemRepository, sale_id: uuid.UUID, sold_item: SoldItem
) -> SaleDetail:
    """売上明細を作成する。

    Args:
        item_repo (ItemRepository): 商品リポジトリ
        sale_id (uuid.UUID): 売上ID
        sold_item (SoldItem): 売上を計上する商品とその数量

    Returns:
        SaleDetail: 売上明細
    """
    item = item_repo.by_id(sold_item.id)
    if item is None:
        raise Exception(f"商品ID({sold_item.id})と一致する商品が見つかりません。")
    return SaleDetail(sale_id, item, sold_item.quantities)


def record_sales(
    repo_manager: RepositoryManager,
    customer_id: Optional[uuid.UUID],
    sold_at: datetime,
    sold_items: List[SoldItem],
) -> None:
    """売上を計上する。

    Args:
        repo_manager (RepositoryManager): リポジトリマネージャー
        customer_id (Optional[uuid.UUID]): 顧客ID
        sold_at: (datetime): 売上日時
        sold_items (List[SoldItem]): 顧客が購入する商品を格納したリスト
    """
    # 顧客を取得
    if customer_id is not None:
        customer_repo = repo_manager.customer()
        customer = customer_repo.by_id(customer_id)
    else:
        customer = None

    # 消費税リストを取得
    tax_repo = repo_manager.consumption_tax()
    taxes = tax_repo.list()
    # 消費税マネージャーを構築
    tax_manager = ConsumptionTaxManager(taxes)
    # 適用する消費税の税率を決定
    tax_rate = tax_manager.consumption_tax_rate(sold_at)

    # 商品リポジトリを取得
    item_repo = repo_manager.item()

    # 売上を構築
    sale_id = uuid.uuid4()
    sale = Sale(sale_id, customer, sold_at, tax_rate)
    for sold_item in sold_items:
        sale.add_sale_detail(create_sale_detail(item_repo, sale_id, sold_item))

    # 打ち上げを計上
    sale_repo = repo_manager.sale()
    sale_repo.register(sale)
