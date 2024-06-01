import uuid
from typing import List

from drugstore import DATABASE_FILE_NAME, connect_to_database
from drugstore.common import jst_now
from drugstore.infra.repositories.sqlite import RepositoryManagerImpl
from drugstore.usecases.sales import SoldItem, record_sales


def scan_membership_card() -> uuid.UUID:
    """会員カードに記載されたバーコードを読み込み、顧客IDを返す。

    Returns:
        uuid.UUID: 顧客ID
    """
    return uuid.UUID("a67cd437-50fd-4667-a54e-5a5f09025359")


def check_items_and_quantities_to_sale() -> List[SoldItem]:
    """売上を計上する商品のバーコードを読み込み、総品の商品IDをと売上する商品の数量を確認する。

    Returns:
        List[UUID]: 売上する商品の商品IDとその数量
    """
    return [
        SoldItem(uuid.UUID("6e0d4fbe-cafe-4af7-bc95-a564b5029322"), 1),
        SoldItem(uuid.UUID("0734980b-ca7e-4bf4-81df-39ac95920ce0"), 2),
    ]


def customer_buys_items(repo_manager: RepositoryManagerImpl):
    """顧客が商品を購入する。

    Args:
        repo_manager (RepositoryManagerImpl): sqlite3のリポジトリマネージャー
    """
    # 顧客から会員カードを受け取り、バーコードを読み込むことで顧客IDを入手
    customer_id = scan_membership_card()

    # 売上する商品の商品IDと商品の数量を確認
    sold_items = check_items_and_quantities_to_sale()

    # 売上を計上するユースケースを実行
    record_sales(repo_manager, customer_id, jst_now(), sold_items)


if __name__ == "__main__":
    # データベースに接続
    conn = connect_to_database(DATABASE_FILE_NAME)

    # sqlite3のリポジトリマネージャーを構築
    repo_manager = RepositoryManagerImpl(conn)

    # 顧客が商品を購入
    customer_buys_items(repo_manager)
