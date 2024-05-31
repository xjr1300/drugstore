# sqlite3用の具象消費税リポジトリ
#
# sqlite3は固定少数点数を扱えないため、消費税率を10,000倍してデータベースに記録する。

import sqlite3
import uuid
from datetime import datetime
from decimal import Decimal
from typing import List, Tuple

from drugstore.common import JST
from drugstore.domain.models.consumption_taxes import ConsumptionTax
from drugstore.domain.repositories.consumption_taxes import ConsumptionTaxRepository


def consumption_tax_from_row(row: Tuple[str, str, str, int]) -> ConsumptionTax:
    """消費税ID、消費税名、単価の順に格納したタプルから消費税を返す。

    Args:
        row (Tuple[str, str, str, float]): 消費税ID、起点日時、終点日時、
            10,000倍した税率の順に格納したタプル

    Returns:
        ConsumptionTax: 消費税
    """
    id = uuid.UUID(row[0])
    begin = datetime.fromisoformat(row[1]).replace(tzinfo=JST)
    end = datetime.fromisoformat(row[2]).replace(tzinfo=JST)
    rate = Decimal(row[3]) / 10_000
    return ConsumptionTax(id, begin, end, rate)


class ConsumptionTaxRepositoryImpl(ConsumptionTaxRepository):
    """消費税リポジトリ"""

    def __init__(self, conn: sqlite3.Connection) -> None:
        """イニシャライザ"""
        super().__init__()
        self.conn = conn

    def list(self) -> List[ConsumptionTax]:
        """消費税リストを返す。

        Returns:
            List[ConsumptionTax]: 消費税リスト
        """
        sql = """
            SELECT id, begin_dt, end_dt, rate
            FROM consumption_taxes
            ORDER BY begin_dt
        """
        cursor = self.conn.execute(sql)
        consumption_taxes: List[ConsumptionTax] = []
        for row in cursor:
            consumption_taxes.append(consumption_tax_from_row(row))
        return consumption_taxes

    def replace_list(self, consumption_taxes: List[ConsumptionTax]) -> None:
        """消費税リストを入れ替える。

        Args:
            consumption_taxes (List[ConsumptionTax]): 消費税リスト
        """
        sql = "DELETE FROM consumption_taxes"
        self.conn.execute(sql)
        sql = "INSERT INTO consumption_taxes VALUES (?, ?, ?, ?)"
        for tax in consumption_taxes:
            self.conn.execute(
                sql,
                (
                    str(tax.id),
                    tax.begin.isoformat(),
                    tax.end.isoformat(),
                    int(tax.rate * 10_000),
                ),
            )
        self.conn.commit()
