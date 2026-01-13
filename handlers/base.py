"""
基礎處理模組
處理用戶註冊、登入、返回首頁等基礎功能
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

from messages import (
    get_user_check_message,
    get_account_info_message
)
from keyboards import get_home_keyboard
from state import (
    set_user_state,
    get_user_account,
    get_user_password,
    get_user_usdt_balance
)
from platform_api import (
    check_user_exists,
    register_user,
    login_user,
    check_user_login_status
)
from handlers.utils import send_photo_with_cache

logger = logging.getLogger(__name__)


async def handle_user_registration_and_login(update: Update, context: ContextTypes.DEFAULT_TYPE) -> tuple[str, str]:
    """
    處理用戶註冊和登入邏輯
    :param update: Telegram Update 對象
    :param context: Context 對象
    :return: (說明報文, 賬戶信息訊息) 元組
    """
    user = update.effective_user
    user_id = user.id
    
    # 檢查TG ID用戶是否存在
    user_exists = check_user_exists(user_id)
    user_logged_in = False
    
    if not user_exists:
        # 如果沒有這個TG ID用戶，於網投平台註冊該TG用戶
        username, password = register_user(user)
        show_password = False  # 新註冊用戶不顯示密碼
        user_logged_in = False
        logger.info(f"新用戶註冊: TG ID={user_id}, 用戶名={username}")
    else:
        # 如果有這個TG ID用戶
        username = get_user_account(user_id)
        password = get_user_password(user_id)
        
        # 檢查用戶登入狀態
        if check_user_login_status(user_id):
            # 用戶有登入，不顯示密碼
            show_password = False
            user_logged_in = True
            logger.info(f"用戶已登入: TG ID={user_id}, 用戶名={username}")
        else:
            # 用戶無登入，幫用戶登入，不顯示密碼
            login_user(user_id)
            show_password = False
            user_logged_in = True  # 登入後視為已登入
            logger.info(f"幫用戶登入: TG ID={user_id}, 用戶名={username}")
    
    # 生成說明報文（純文案）
    check_message = get_user_check_message(user_exists, user_logged_in)
    
    # 獲取用戶USDT餘額
    usdt_balance = get_user_usdt_balance(user_id)
    
    # 生成賬戶信息訊息（第二則訊息）
    account_message = get_account_info_message(
        telegram_id=user_id,
        username=username,
        show_password=show_password,
        password=password if show_password else "",
        usdt_balance=f"{usdt_balance:.2f}"
    )
    
    return check_message, account_message


async def return_to_home(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    返回主頁的通用函數
    處理用戶註冊/登入並發送主頁訊息
    :param update: Telegram Update 對象
    :param context: Context 對象
    """
    user_id = update.effective_user.id
    
    # 處理用戶註冊和登入，獲取說明報文和賬戶信息訊息
    check_message, account_message = await handle_user_registration_and_login(update, context)
    
    # 發送主要圖片和說明報文（作為圖片caption）
    await send_photo_with_cache(
        update,
        context,
        "images/主要图片.jpeg",
        check_message
    )
    
    # 發送賬戶信息訊息（第二則訊息）
    await update.message.reply_text(account_message)
    
    # 設置 Reply Keyboard（底部常駐菜單）
    await update.message.reply_text(
        "💡 使用底部按钮快速操作",
        reply_markup=get_home_keyboard()
    )
    
    set_user_state(user_id, "home")
    logger.info(f"用戶 {user_id} 返回首頁")
