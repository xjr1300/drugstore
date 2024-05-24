from datetime import datetime
from zoneinfo import ZoneInfo

# 日本標準時 (Japan Standard Time)
JST = ZoneInfo("Asia/Tokyo")


def jst_datetime(
    year: int, month: int, day: int, hour: int = 0, minute: int = 0, second: int = 0
) -> datetime:
    """日本標準時で日時をインスタンス化する。

    Args:
        year (int): 年
        month (int): 月
        day (int): 日
        hour (int, optional): 時
        minute (int, optional): 分
        second (int, optional): 秒

    Returns:
        datetime: 日本標準時の日時
    """
    return datetime(year, month, day, hour, minute, second, tzinfo=JST)
