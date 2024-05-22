from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple


class MembershipTypeCode(Enum):
    """会員区分コード"""

    # 一般会員
    General = 1
    # 特別会員
    Special = 2


# 会員区分データ
MEMBERSHIP_TYPE_DATA: List[Tuple[int, str]] = [
    (MembershipTypeCode.General.value, "一般会員"),
    (MembershipTypeCode.Special.value, "特別会員"),
]


@dataclass
class MembershipType:
    """会員区分"""

    # 会員区分コード
    code: int
    # 会員区分名
    name: str
