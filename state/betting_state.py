"""
狀態管理模組 - betting_state
"""

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


# 用於追蹤用戶的投注確認狀態（支持多個確認消息）
# key: user_id, value: list[{"amount": str, "timestamp": float, "message_id": int, "chat_id": int}]
user_bet_confirmation: dict[int, list] = {}


def get_user_bet_confirmation(user_id: int) -> list:
    """
    獲取用戶的所有投注確認狀態
    :param user_id: 用戶ID
    :return: 確認狀態列表
    """
    return user_bet_confirmation.get(user_id, [])


def get_user_bet_confirmation_by_message_id(user_id: int, message_id: int) -> dict | None:
    """
    根據消息ID獲取特定的投注確認狀態
    :param user_id: 用戶ID
    :param message_id: 消息ID
    :return: 確認狀態或None
    """
    confirmations = get_user_bet_confirmation(user_id)
    for conf in confirmations:
        if conf.get("message_id") == message_id:
            return conf
    return None


def set_user_bet_confirmation(user_id: int, amount: str, message_id: int, chat_id: int, timestamp: float) -> None:
    """
    添加用戶的投注確認狀態（支持多個）
    :param user_id: 用戶ID
    :param amount: 投注金額（字符串）
    :param message_id: 確認消息的ID
    :param chat_id: 聊天ID
    :param timestamp: 時間戳
    """
    if user_id not in user_bet_confirmation:
        user_bet_confirmation[user_id] = []
    
    user_bet_confirmation[user_id].append({
        "amount": amount,
        "timestamp": timestamp,
        "message_id": message_id,
        "chat_id": chat_id
    })


def clear_user_bet_confirmation(user_id: int, message_id: int | None = None) -> None:
    """
    清除用戶的投注確認狀態
    :param user_id: 用戶ID
    :param message_id: 如果提供，只清除該消息ID的確認狀態；否則清除所有
    """
    if user_id not in user_bet_confirmation:
        return
    
    if message_id is None:
        # 清除所有
        del user_bet_confirmation[user_id]
    else:
        # 只清除指定的消息ID
        user_bet_confirmation[user_id] = [
            conf for conf in user_bet_confirmation[user_id]
            if conf.get("message_id") != message_id
        ]
        if not user_bet_confirmation[user_id]:
            del user_bet_confirmation[user_id]


# 用於追蹤用戶的自動下注確認狀態（支持多個確認消息）
# key: user_id, value: list[{"amount": str, "count": int, "timestamp": float, "message_id": int, "chat_id": int}]
user_auto_bet_confirmation: dict[int, list] = {}


def get_user_auto_bet_confirmation(user_id: int) -> list:
    """
    獲取用戶的所有自動下注確認狀態
    :param user_id: 用戶ID
    :return: 確認狀態列表
    """
    return user_auto_bet_confirmation.get(user_id, [])


def get_user_auto_bet_confirmation_by_message_id(user_id: int, message_id: int) -> dict | None:
    """
    根據消息ID獲取特定的自動下注確認狀態
    :param user_id: 用戶ID
    :param message_id: 消息ID
    :return: 確認狀態或None
    """
    confirmations = get_user_auto_bet_confirmation(user_id)
    for conf in confirmations:
        if conf.get("message_id") == message_id:
            return conf
    return None


def set_user_auto_bet_confirmation(user_id: int, amount: str, count: int, message_id: int, chat_id: int, timestamp: float) -> None:
    """
    添加用戶的自動下注確認狀態（支持多個）
    :param user_id: 用戶ID
    :param amount: 每次下注金額（字符串）
    :param count: 下注次數
    :param message_id: 確認消息的ID
    :param chat_id: 聊天ID
    :param timestamp: 時間戳
    """
    if user_id not in user_auto_bet_confirmation:
        user_auto_bet_confirmation[user_id] = []
    
    user_auto_bet_confirmation[user_id].append({
        "amount": amount,
        "count": count,
        "timestamp": timestamp,
        "message_id": message_id,
        "chat_id": chat_id
    })


def clear_user_auto_bet_confirmation(user_id: int, message_id: int | None = None) -> None:
    """
    清除用戶的自動下注確認狀態
    :param user_id: 用戶ID
    :param message_id: 如果提供，只清除該消息ID的確認狀態；否則清除所有
    """
    if user_id not in user_auto_bet_confirmation:
        return
    
    if message_id is None:
        # 清除所有
        del user_auto_bet_confirmation[user_id]
    else:
        # 只清除指定的消息ID
        user_auto_bet_confirmation[user_id] = [
            conf for conf in user_auto_bet_confirmation[user_id]
            if conf.get("message_id") != message_id
        ]
        if not user_auto_bet_confirmation[user_id]:
            del user_auto_bet_confirmation[user_id]

