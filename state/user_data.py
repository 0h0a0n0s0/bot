"""
狀態管理模組 - user_data
"""

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

