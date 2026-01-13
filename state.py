"""
狀態管理模組
管理用戶的菜單狀態
"""

# 用於追蹤用戶當前的菜單狀態
# key: user_id, value: "home" | "game_level1" | "game_level2" | "profile" | "security_center" | "personal_report" | "daily_report" | "weekly_report" | "beginner_room_betting"
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


# 用於追蹤用戶的周統計報表開始日期（格式：YYYY-MM-DD）
# key: user_id, value: 日期字符串（周的第一天）
user_weekly_report_start_date: dict[int, str] = {}

# 用於追蹤用戶的周統計報表消息ID（用於編輯消息）
# key: user_id, value: message_id
user_weekly_report_message_id: dict[int, int] = {}

# 用於追蹤用戶當前查看的遊戲類型（用於周統計報表）
# key: user_id, value: 遊戲名稱或 "总计"
user_weekly_report_game: dict[int, str] = {}


def get_user_weekly_report_start_date(user_id: int) -> str:
    """獲取用戶的周統計報表開始日期，默認為今天往前推6天（共7天）"""
    from datetime import datetime, timedelta
    if user_id not in user_weekly_report_start_date:
        # 以當日起算向前推6天，共7天
        today = datetime.now()
        start_date = (today - timedelta(days=6)).strftime("%Y-%m-%d")
        user_weekly_report_start_date[user_id] = start_date
    return user_weekly_report_start_date[user_id]


def set_user_weekly_report_start_date(user_id: int, date: str) -> None:
    """設置用戶的周統計報表開始日期"""
    user_weekly_report_start_date[user_id] = date


def get_user_weekly_report_message_id(user_id: int) -> int | None:
    """獲取用戶的周統計報表消息ID"""
    return user_weekly_report_message_id.get(user_id)


def set_user_weekly_report_message_id(user_id: int, message_id: int) -> None:
    """設置用戶的周統計報表消息ID"""
    user_weekly_report_message_id[user_id] = message_id


def get_user_weekly_report_game(user_id: int) -> str:
    """獲取用戶當前查看的遊戲類型（周統計），默認為「总计」"""
    return user_weekly_report_game.get(user_id, "总计")


def set_user_weekly_report_game(user_id: int, game: str) -> None:
    """設置用戶當前查看的遊戲類型（周統計）"""
    user_weekly_report_game[user_id] = game


# 用於追蹤用戶是否在輸入充值/提現金額
# key: user_id, value: "deposit" | "withdraw" | None
user_deposit_withdraw_state: dict[int, str | None] = {}


def get_user_deposit_withdraw_state(user_id: int) -> str | None:
    """獲取用戶的充值/提現狀態，None 表示不在輸入狀態"""
    return user_deposit_withdraw_state.get(user_id)


def set_user_deposit_withdraw_state(user_id: int, state: str | None) -> None:
    """設置用戶的充值/提現狀態，'deposit' 表示正在輸入充值金額，'withdraw' 表示正在輸入提現金額，None 表示清除狀態"""
    if state is None:
        if user_id in user_deposit_withdraw_state:
            del user_deposit_withdraw_state[user_id]
    else:
        user_deposit_withdraw_state[user_id] = state


# 用於存儲用戶的網投平台賬號
# key: user_id (TG ID), value: username
user_account: dict[int, str] = {}

# 用於存儲用戶的網投平台密碼
# key: user_id (TG ID), value: password
user_password: dict[int, str] = {}

# 用於追蹤用戶的登入狀態
# key: user_id (TG ID), value: True/False
user_login_status: dict[int, bool] = {}


def get_user_account(user_id: int) -> str | None:
    """獲取用戶的網投平台賬號，如果不存在返回None"""
    return user_account.get(user_id)


def set_user_account(user_id: int, username: str) -> None:
    """設置用戶的網投平台賬號"""
    user_account[user_id] = username


def get_user_password(user_id: int) -> str | None:
    """獲取用戶的網投平台密碼，如果不存在返回None"""
    return user_password.get(user_id)


def set_user_password(user_id: int, password: str) -> None:
    """設置用戶的網投平台密碼"""
    user_password[user_id] = password


def get_user_login_status(user_id: int) -> bool:
    """獲取用戶的登入狀態，默認為False"""
    return user_login_status.get(user_id, False)


def set_user_login_status(user_id: int, is_logged_in: bool) -> None:
    """設置用戶的登入狀態"""
    user_login_status[user_id] = is_logged_in


# 用於追蹤用戶是否在輸入銀行卡資料
# key: user_id, value: True/False
user_bank_card_binding_state: dict[int, bool] = {}


def get_user_bank_card_binding_state(user_id: int) -> bool:
    """獲取用戶是否在輸入銀行卡資料狀態，默認為False"""
    return user_bank_card_binding_state.get(user_id, False)


def set_user_bank_card_binding_state(user_id: int, is_binding: bool) -> None:
    """設置用戶是否在輸入銀行卡資料狀態"""
    if is_binding:
        user_bank_card_binding_state[user_id] = True
    else:
        if user_id in user_bank_card_binding_state:
            del user_bank_card_binding_state[user_id]


# 用於追蹤用戶是否在輸入錢包資料
# key: user_id, value: "trc20" | "erc20" | None
user_wallet_binding_state: dict[int, str | None] = {}


def get_user_wallet_binding_state(user_id: int) -> str | None:
    """獲取用戶是否在輸入錢包資料狀態，返回 "trc20" | "erc20" | None"""
    return user_wallet_binding_state.get(user_id)


def set_user_wallet_binding_state(user_id: int, wallet_type: str | None) -> None:
    """設置用戶是否在輸入錢包資料狀態，wallet_type 為 "trc20" | "erc20" | None"""
    if wallet_type is None:
        if user_id in user_wallet_binding_state:
            del user_wallet_binding_state[user_id]
    else:
        user_wallet_binding_state[user_id] = wallet_type


# 用於存儲用戶已綁定的銀行卡號
# key: user_id, value: 銀行卡號（完整）
user_bank_card_number: dict[int, str] = {}


def get_user_bank_card_number(user_id: int) -> str | None:
    """獲取用戶已綁定的銀行卡號，如果不存在返回None"""
    return user_bank_card_number.get(user_id)


def set_user_bank_card_number(user_id: int, card_number: str) -> None:
    """設置用戶已綁定的銀行卡號"""
    user_bank_card_number[user_id] = card_number


def format_bank_card_number(card_number: str) -> str:
    """
    格式化銀行卡號，只顯示末六位，前面用*隱藏
    :param card_number: 完整銀行卡號
    :return: 格式化後的銀行卡號（如：****123456）
    """
    if len(card_number) <= 6:
        return card_number
    return "*" * (len(card_number) - 6) + card_number[-6:]


# 用於存儲用戶已綁定的錢包地址
# key: user_id, value: {"trc20": address, "erc20": address} 或 {}
user_wallet_addresses: dict[int, dict[str, str]] = {}


def get_user_wallet_address(user_id: int, wallet_type: str) -> str | None:
    """
    獲取用戶已綁定的錢包地址
    :param user_id: 用戶ID
    :param wallet_type: "trc20" 或 "erc20"
    :return: 錢包地址，如果不存在返回None
    """
    if user_id not in user_wallet_addresses:
        return None
    return user_wallet_addresses[user_id].get(wallet_type)


def set_user_wallet_address(user_id: int, wallet_type: str, address: str) -> None:
    """
    設置用戶已綁定的錢包地址
    :param user_id: 用戶ID
    :param wallet_type: "trc20" 或 "erc20"
    :param address: 錢包地址
    """
    if user_id not in user_wallet_addresses:
        user_wallet_addresses[user_id] = {}
    user_wallet_addresses[user_id][wallet_type] = address


def format_wallet_address(address: str) -> str:
    """
    格式化錢包地址，只顯示前兩位和末六位，中間用*隱藏
    :param address: 完整錢包地址
    :return: 格式化後的錢包地址（如：TW******JS4V）
    """
    if len(address) <= 8:
        return address
    return address[:2] + "*" * (len(address) - 8) + address[-6:]


# 用於存儲用戶已綁定的銀行卡密碼
# key: user_id, value: 4位數提款密碼
user_bank_card_password: dict[int, str] = {}


def get_user_bank_card_password(user_id: int) -> str | None:
    """獲取用戶已綁定的銀行卡密碼，如果不存在返回None"""
    return user_bank_card_password.get(user_id)


def set_user_bank_card_password(user_id: int, password: str) -> None:
    """設置用戶已綁定的銀行卡密碼"""
    user_bank_card_password[user_id] = password


# 用於追蹤用戶提款流程狀態
# key: user_id, value: "select_method" | "enter_amount" | "enter_password" | None
user_withdraw_state: dict[int, str | None] = {}


def get_user_withdraw_state(user_id: int) -> str | None:
    """獲取用戶提款流程狀態，返回 "select_method" | "enter_amount" | "enter_password" | None"""
    return user_withdraw_state.get(user_id)


def set_user_withdraw_state(user_id: int, state: str | None) -> None:
    """設置用戶提款流程狀態"""
    if state is None:
        if user_id in user_withdraw_state:
            del user_withdraw_state[user_id]
    else:
        user_withdraw_state[user_id] = state


# 用於存儲用戶選擇的提款方式
# key: user_id, value: "bank_card" | "trc20" | "erc20"
user_withdraw_method: dict[int, str] = {}


def get_user_withdraw_method(user_id: int) -> str | None:
    """獲取用戶選擇的提款方式，返回 "bank_card" | "trc20" | "erc20" | None"""
    return user_withdraw_method.get(user_id)


def set_user_withdraw_method(user_id: int, method: str | None) -> None:
    """設置用戶選擇的提款方式"""
    if method is None:
        if user_id in user_withdraw_method:
            del user_withdraw_method[user_id]
    else:
        user_withdraw_method[user_id] = method


# 用於存儲用戶輸入的提款金額
# key: user_id, value: 提款金額字符串
user_withdraw_amount: dict[int, str] = {}


def get_user_withdraw_amount(user_id: int) -> str | None:
    """獲取用戶輸入的提款金額"""
    return user_withdraw_amount.get(user_id)


def set_user_withdraw_amount(user_id: int, amount: str | None) -> None:
    """設置用戶輸入的提款金額"""
    if amount is None:
        if user_id in user_withdraw_amount:
            del user_withdraw_amount[user_id]
    else:
        user_withdraw_amount[user_id] = amount


# 用於存儲用戶選擇的自動下注金額
# key: user_id, value: 下注金額字符串（如："2", "5", "10", "30", "50"）
user_auto_bet_amount: dict[int, str] = {}


def get_user_auto_bet_amount(user_id: int) -> str | None:
    """獲取用戶選擇的自動下注金額"""
    return user_auto_bet_amount.get(user_id)


def set_user_auto_bet_amount(user_id: int, amount: str | None) -> None:
    """設置用戶選擇的自動下注金額"""
    if amount is None:
        if user_id in user_auto_bet_amount:
            del user_auto_bet_amount[user_id]
    else:
        user_auto_bet_amount[user_id] = amount


# 用於存儲用戶選擇的自動下注次數（None 表示持續下注）
# key: user_id, value: 次數（整數）或 None（表示持續下注）
user_auto_bet_count: dict[int, int | None] = {}


def get_user_auto_bet_count(user_id: int) -> int | None:
    """獲取用戶選擇的自動下注次數，None 表示持續下注"""
    return user_auto_bet_count.get(user_id)


def set_user_auto_bet_count(user_id: int, count: int | None) -> None:
    """設置用戶選擇的自動下注次數，None 表示持續下注"""
    if count is None:
        if user_id in user_auto_bet_count:
            del user_auto_bet_count[user_id]
    else:
        user_auto_bet_count[user_id] = count


# 用於追蹤用戶是否正在進行持續自動下注（用於"持續下注到返回上頁"功能）
# key: user_id, value: True/False
user_auto_bet_continuous: dict[int, bool] = {}


def get_user_auto_bet_continuous(user_id: int) -> bool:
    """獲取用戶是否正在進行持續自動下注，默認為False"""
    return user_auto_bet_continuous.get(user_id, False)


def set_user_auto_bet_continuous(user_id: int, is_continuous: bool) -> None:
    """設置用戶是否正在進行持續自動下注"""
    if is_continuous:
        user_auto_bet_continuous[user_id] = True
    else:
        if user_id in user_auto_bet_continuous:
            del user_auto_bet_continuous[user_id]


# 用於存儲用戶的USDT餘額
# key: user_id, value: 餘額（浮點數）
user_usdt_balance: dict[int, float] = {}

# 初始餘額
INITIAL_BALANCE = 500.0


def get_user_usdt_balance(user_id: int) -> float:
    """
    獲取用戶的USDT餘額，如果不存在則返回初始餘額500
    :param user_id: 用戶ID
    :return: USDT餘額
    """
    if user_id not in user_usdt_balance:
        user_usdt_balance[user_id] = INITIAL_BALANCE
    return user_usdt_balance[user_id]


def set_user_usdt_balance(user_id: int, balance: float) -> None:
    """
    設置用戶的USDT餘額
    :param user_id: 用戶ID
    :param balance: 餘額
    """
    user_usdt_balance[user_id] = balance


def deduct_user_balance(user_id: int, amount: float) -> bool:
    """
    扣除用戶餘額
    :param user_id: 用戶ID
    :param amount: 扣除金額
    :return: 如果扣除成功返回True，餘額不足返回False
    """
    current_balance = get_user_usdt_balance(user_id)
    if current_balance < amount:
        return False
    user_usdt_balance[user_id] = current_balance - amount
    return True


def add_user_balance(user_id: int, amount: float) -> None:
    """
    增加用戶餘額（派獎）
    :param user_id: 用戶ID
    :param amount: 增加金額
    """
    current_balance = get_user_usdt_balance(user_id)
    user_usdt_balance[user_id] = current_balance + amount


# 用於追蹤用戶進入投注選擇的來源（用於區分哈希轉盤和初級房）
# key: user_id, value: "hash_wheel" | "beginner_room" | None
user_betting_source: dict[int, str | None] = {}


def get_user_betting_source(user_id: int) -> str | None:
    """
    獲取用戶進入投注選擇的來源
    :param user_id: 用戶ID
    :return: "hash_wheel" | "beginner_room" | None
    """
    return user_betting_source.get(user_id)


def set_user_betting_source(user_id: int, source: str | None) -> None:
    """
    設置用戶進入投注選擇的來源
    :param user_id: 用戶ID
    :param source: "hash_wheel" | "beginner_room" | None
    """
    if source is None:
        if user_id in user_betting_source:
            del user_betting_source[user_id]
    else:
        user_betting_source[user_id] = source

