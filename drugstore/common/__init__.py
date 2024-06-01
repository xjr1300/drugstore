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


def jst_now() -> datetime:
    """日本標準時で現在日時を返す。

    Returns:
        datetime: 日本標準時の現在日時
    """
    return datetime.now(tz=JST)


def is_jst_datetime(dt: datetime) -> bool:
    """日時が日本標準時か確認する。

    Args:
        dt (datetime): 日時

    Returns:
        bool: 日本標準時の場合はTrue
            タイムゾーンが指定されていない、または日本標準時でない場合はFalse
    """
    return dt.tzinfo == JST
