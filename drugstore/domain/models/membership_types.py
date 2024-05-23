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

    def __init__(self, code: int, name: str) -> None:
        """イニシャライザ

        Args:
            code (int): 会員区分コード
            name (str): 会員区分名

        Raises:
            ValueError: 会員区分コードと会員区分名の組み合わせが不正です。
        """
        data = (code, name.strip())
        if data not in MEMBERSHIP_TYPE_DATA:
            raise ValueError("会員区分コードと会員区分名の組み合わせが不正です。")
        self.code = data[0]
        self.name = data[1]
