import uuid
from dataclasses import dataclass

from .membership_types import MembershipType


@dataclass
class Customer:
    """顧客"""

    # 顧客ID
    id: uuid.UUID
    # 顧客名
    name: str
    # 会員区分
    membership_type: MembershipType
