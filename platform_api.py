"""
網投平台 API 模組
處理用戶註冊、登入、查詢等功能
"""

import random
import string
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


def generate_random_password(length: int = 8) -> str:
    """
    生成隨機密碼（小寫英文+數字）
    :param length: 密碼長度，默認為8
    :return: 隨機密碼字符串
    """
    characters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def generate_username(
    telegram_user,
    platform_member_id: Optional[int] = None
) -> str:
    """
    生成用戶名（Mock模式）
    使用格式：tg + TG ID（例如：tg123456789）
    :param telegram_user: Telegram User 對象
    :param platform_member_id: 平台會員ID（可選，已廢棄，保留以兼容舊代碼）
    :return: 生成的用戶名
    """
    # 使用格式：tg + TG ID
    return f"tg{telegram_user.id}"


def check_user_exists(telegram_id: int) -> bool:
    """
    檢查TG ID用戶是否存在於網投平台（Mock模式）
    :param telegram_id: Telegram ID
    :return: 如果用戶存在返回True，否則返回False
    """
    # Mock模式：使用本地存儲來模擬
    from state import get_user_account
    account = get_user_account(telegram_id)
    return account is not None


def register_user(
    telegram_user,
    platform_member_id: Optional[int] = None
) -> Tuple[str, str]:
    """
    在網投平台註冊新用戶（Mock模式）
    :param telegram_user: Telegram User 對象
    :param platform_member_id: 平台會員ID（可選）
    :return: (username, password) 元組
    """
    username = generate_username(telegram_user, platform_member_id)
    password = generate_random_password(8)
    
    # Mock模式：使用本地存儲來模擬註冊
    from state import set_user_account, set_user_password, set_user_login_status
    
    # 保存用戶信息
    set_user_account(telegram_user.id, username)
    set_user_password(telegram_user.id, password)
    set_user_login_status(telegram_user.id, False)  # 剛註冊，未登入
    
    logger.info(f"[Mock] 註冊新用戶: TG ID={telegram_user.id}, 用戶名={username}, 密碼={password}")
    
    return username, password


def login_user(telegram_id: int) -> bool:
    """
    幫用戶登入網投平台（Mock模式）
    :param telegram_id: Telegram ID
    :return: 登入是否成功
    """
    # Mock模式：使用本地存儲來模擬登入
    from state import get_user_account, get_user_password, set_user_login_status
    
    account = get_user_account(telegram_id)
    if account is None:
        logger.warning(f"[Mock] 嘗試登入不存在的用戶: TG ID={telegram_id}")
        return False
    
    password = get_user_password(telegram_id)
    
    # Mock模式：直接設置登入狀態為True
    set_user_login_status(telegram_id, True)
    
    logger.info(f"[Mock] 用戶登入成功: TG ID={telegram_id}, 用戶名={account}")
    
    return True


def check_user_login_status(telegram_id: int) -> bool:
    """
    獲取用戶登入狀態
    :param telegram_id: Telegram ID
    :return: 如果已登入返回True，否則返回False
    """
    from state import get_user_login_status
    return get_user_login_status(telegram_id)

