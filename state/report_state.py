"""
狀態管理模組 - report_state
"""

def get_user_report_date(user_id: int) -> str:
    """獲取用戶的日統計報表日期，默認為今天"""
    from datetime import datetime
    if user_id not in user_report_date:
        user_report_date[user_id] = datetime.now().strftime("%Y-%m-%d")
    return user_report_date[user_id]


def set_user_report_date(user_id: int, date: str) -> None:
    """設置用戶的日統計報表日期"""
    user_report_date[user_id] = date


def get_user_report_game(user_id: int) -> str:
    """獲取用戶當前查看的遊戲類型，默認為「总计」"""
    return user_report_game.get(user_id, "总计")


def set_user_report_game(user_id: int, game: str) -> None:
    """設置用戶當前查看的遊戲類型"""
    user_report_game[user_id] = game


def get_user_report_message_id(user_id: int) -> int | None:
    """獲取用戶的日統計報表消息ID"""
    return user_report_message_id.get(user_id)


def set_user_report_message_id(user_id: int, message_id: int) -> None:
    """設置用戶的日統計報表消息ID"""
    user_report_message_id[user_id] = message_id


# 用於追蹤用戶的月統計報表月份（格式：YYYY-MM）
# key: user_id, value: 月份字符串（例如："2026-01"）
user_monthly_report_month: dict[int, str] = {}

# 用於追蹤用戶的月統計報表消息ID（用於編輯消息）
# key: user_id, value: message_id
user_monthly_report_message_id: dict[int, int] = {}

# 用於追蹤用戶當前查看的遊戲類型（用於月統計報表）
# key: user_id, value: 遊戲名稱或 "总计"
user_monthly_report_game: dict[int, str] = {}


def get_user_monthly_report_month(user_id: int) -> str:
    """獲取用戶的月統計報表月份，默認為當月（格式：YYYY-MM）"""
    from datetime import datetime
    if user_id not in user_monthly_report_month:
        # 默認為當月
        today = datetime.now()
        month_str = today.strftime("%Y-%m")
        user_monthly_report_month[user_id] = month_str
    return user_monthly_report_month[user_id]


def set_user_monthly_report_month(user_id: int, month: str) -> None:
    """設置用戶的月統計報表月份（格式：YYYY-MM）"""
    user_monthly_report_month[user_id] = month


def get_user_monthly_report_message_id(user_id: int) -> int | None:
    """獲取用戶的月統計報表消息ID"""
    return user_monthly_report_message_id.get(user_id)


def set_user_monthly_report_message_id(user_id: int, message_id: int) -> None:
    """設置用戶的月統計報表消息ID"""
    user_monthly_report_message_id[user_id] = message_id


def get_user_monthly_report_game(user_id: int) -> str:
    """獲取用戶當前查看的遊戲類型（月統計），默認為「总计」"""
    return user_monthly_report_game.get(user_id, "总计")


def set_user_monthly_report_game(user_id: int, game: str) -> None:
    """設置用戶當前查看的遊戲類型（月統計）"""
    user_monthly_report_game[user_id] = game

