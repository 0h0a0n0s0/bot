"""
狀態管理模組 - binding_state
"""

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


# 用於追蹤用戶是否在設置提款密碼
# key: user_id, value: "inputting" | "confirming" | None
user_withdrawal_password_state: dict[int, str | None] = {}

# 用於存儲用戶正在輸入的提款密碼（臨時）
# key: user_id, value: str (已輸入的密碼，最多4位)
user_withdrawal_password_input: dict[int, str] = {}

# 用於存儲用戶正在確認的提款密碼（臨時）
# key: user_id, value: str (已輸入的確認密碼，最多4位)
user_withdrawal_password_confirm: dict[int, str] = {}

# 用於存儲提款密碼設置的消息ID（用於更新消息）
# key: user_id, value: int (消息ID)
user_withdrawal_password_message_id: dict[int, int] = {}


def get_user_withdrawal_password_state(user_id: int) -> str | None:
    """獲取用戶提款密碼設置狀態，返回 "inputting" | "confirming" | None"""
    return user_withdrawal_password_state.get(user_id)


def set_user_withdrawal_password_state(user_id: int, state: str | None) -> None:
    """設置用戶提款密碼設置狀態，state 為 "inputting" | "confirming" | None"""
    if state is None:
        if user_id in user_withdrawal_password_state:
            del user_withdrawal_password_state[user_id]
        if user_id in user_withdrawal_password_input:
            del user_withdrawal_password_input[user_id]
        if user_id in user_withdrawal_password_confirm:
            del user_withdrawal_password_confirm[user_id]
        if user_id in user_withdrawal_password_message_id:
            del user_withdrawal_password_message_id[user_id]
    else:
        user_withdrawal_password_state[user_id] = state


def get_user_withdrawal_password_input(user_id: int) -> str:
    """獲取用戶已輸入的提款密碼（臨時）"""
    return user_withdrawal_password_input.get(user_id, "")


def set_user_withdrawal_password_input(user_id: int, password: str) -> None:
    """設置用戶已輸入的提款密碼（臨時）"""
    if password:
        user_withdrawal_password_input[user_id] = password
    else:
        if user_id in user_withdrawal_password_input:
            del user_withdrawal_password_input[user_id]


def get_user_withdrawal_password_confirm(user_id: int) -> str:
    """獲取用戶已輸入的確認密碼（臨時）"""
    return user_withdrawal_password_confirm.get(user_id, "")


def set_user_withdrawal_password_confirm(user_id: int, password: str) -> None:
    """設置用戶已輸入的確認密碼（臨時）"""
    if password:
        user_withdrawal_password_confirm[user_id] = password
    else:
        if user_id in user_withdrawal_password_confirm:
            del user_withdrawal_password_confirm[user_id]


def get_user_withdrawal_password_message_id(user_id: int) -> int | None:
    """獲取提款密碼設置的消息ID"""
    return user_withdrawal_password_message_id.get(user_id)


def set_user_withdrawal_password_message_id(user_id: int, message_id: int | None) -> None:
    """設置提款密碼設置的消息ID"""
    if message_id is None:
        if user_id in user_withdrawal_password_message_id:
            del user_withdrawal_password_message_id[user_id]
    else:
        user_withdrawal_password_message_id[user_id] = message_id

