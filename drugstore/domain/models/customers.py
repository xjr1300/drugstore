import uuid
from dataclasses import dataclass

from .membership_types import MembershipType, MembershipTypeCode


@dataclass
class Customer:
    """顧客"""

    # 顧客ID
    id: uuid.UUID
    # 顧客名
    name: str
    # 会員区分
    membership_type: MembershipType

    def __init__(
        self, id: uuid.UUID, name: str, membership_type: MembershipType
    ) -> None:
        """イニシャライザ

        Args:
            id (uuid.UUID): 顧客ID
            name (str): 顧客名
            membership_type (MembershipType): 会員区分

        Raises:
            ValueError: 顧客の顧客名が空文字です。
        """
        cleaned_name = name.strip()
        if len(cleaned_name) == 0:
            raise ValueError("顧客の顧客名が空文字です。")
        self.id = id
        self.name = cleaned_name
        self.membership_type = membership_type

    def is_general_member(self) -> bool:
        """一般会員か確認する。

        Returns:
            bool: 一般会員の場合はTrue、それ以外の場合はFalse
        """
        return self.membership_type.code == MembershipTypeCode.General.value

    def is_special_member(self) -> bool:
        """特別会員か確認する。

        Returns:
            bool: 特別会員の場合はTrue、それ以外の場合はFalse
        """
        return self.membership_type.code == MembershipTypeCode.Special.value
