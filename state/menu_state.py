"""
狀態管理模組
管理用戶的菜單狀態
"""

# 用於追蹤用戶當前的菜單狀態
# key: user_id, value: "home" | "game_level1" | "game_level2" | "profile" | "security_center" | "personal_report" | "daily_report" | "monthly_report" | "beginner_room_betting"
user_menu_state: dict[int, str] = {}

# 用於追蹤用戶的上一個菜單狀態（用於「返回上页」功能）
# key: user_id, value: 上一個狀態
user_previous_state: dict[int, str] = {}


# 用於追蹤用戶的日統計報表日期（格式：YYYY-MM-DD）
# key: user_id, value: 日期字符串
user_report_date: dict[int, str] = {}

# 用於追蹤用戶當前查看的遊戲類型（用於日統計報表）
# key: user_id, value: 遊戲名稱或 "总计"
user_report_game: dict[int, str] = {}

# 用於追蹤用戶的日統計報表消息ID（用於編輯消息）
# key: user_id, value: message_id
user_report_message_id: dict[int, int] = {}


def get_user_state(user_id: int) -> str:
    """獲取用戶當前狀態，默認為首頁"""
    return user_menu_state.get(user_id, "home")


def set_user_state(user_id: int, state: str) -> None:
    """設置用戶狀態，自動記錄上一個狀態"""
    # 如果當前狀態存在，記錄為上一個狀態
    if user_id in user_menu_state:
        user_previous_state[user_id] = user_menu_state[user_id]
    # 設置新狀態
    user_menu_state[user_id] = state


def get_user_previous_state(user_id: int) -> str:
    """獲取用戶上一個狀態，默認為首頁"""
    return user_previous_state.get(user_id, "home")


def reset_user_state(user_id: int) -> None:
    """重置用戶狀態為首頁"""
    user_menu_state[user_id] = "home"
    # 清除上一個狀態記錄
    if user_id in user_previous_state:
        del user_previous_state[user_id]

