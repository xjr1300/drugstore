from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Self, Tuple


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


def find_membership_data(code: int) -> Optional[Tuple[int, str]]:
    """会員区分データを返す。

    Args:
        code (int): 会員区分コード

    Returns:
        Tuple[int, str]: 会員区分コードと会員区分名を格納したタプル
    """
    for pair in MEMBERSHIP_TYPE_DATA:
        if pair[0] == code:
            return pair
    return None


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

    @classmethod
    def general_membership_type(cls) -> Self:
        """一般会員を取得

        Returns:
            Self: 一般会員
        """
        data = find_membership_data(MembershipTypeCode.General.value)
        if data:
            return cls(data[0], data[1])
        else:
            raise NotImplementedError

    @classmethod
    def special_membership_type(cls) -> Self:
        """特別会員を取得

        Returns:
            Self: 特別会員
        """
        data = find_membership_data(MembershipTypeCode.Special.value)
        if data:
            return cls(data[0], data[1])
        else:
            raise NotImplementedError
