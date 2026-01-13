"""
狀態管理模組 - withdraw_state
"""

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

