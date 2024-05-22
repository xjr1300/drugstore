import uuid
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from drugstore.common import JST

# 最も過去の消費税の起点日
MIN_CONSUMPTION_TAX_BEGIN = datetime.min.replace(tzinfo=JST)
# 最も将来の消費税の終点日
MAX_CONSUMPTION_TAX_END = datetime.max.replace(tzinfo=JST)


@dataclass
class ConsumptionTax:
    """消費税"""

    # 消費税率ID
    id: uuid.UUID
    # 消費税を適用する起点日時 (左閉区間)
    begin: datetime
    # 消費税を適用する終点日時 (右開区間)
    end: datetime
    # 消費税率
    rate: Decimal
