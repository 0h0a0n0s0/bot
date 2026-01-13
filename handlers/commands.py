"""
命令處理模組
處理所有 Telegram Bot 命令
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from messages import (
    get_start_game_message,
    get_profile_message,
    get_deposit_amount_prompt,
    get_withdraw_method_selection_message
)
from keyboards import (
    get_game_level1_keyboard,
    get_profile_keyboard
)
from state import (
    set_user_state,
    set_user_deposit_withdraw_state,
    get_user_usdt_balance,
    get_user_bank_card_number,
    get_user_wallet_address,
    set_user_withdraw_state
)
from handlers.base import return_to_home
from handlers.utils import send_photo_with_cache
from handlers.message_deduplication import is_message_processed, mark_message_processed

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    處理 /start 命令
    每次使用 /start 都會發送認證訊息
    包含消息去重機制，防止 Telegram 因網絡延遲導致的自動重試
    """
    # 消息去重檢查：防止重複處理同一條消息
    message_id = update.message.message_id
    
    if is_message_processed(message_id):
        logger.warning(f"⚠️ 忽略重複請求：message_id={message_id}, user_id={update.effective_user.id}")
        return
    
    # 將 message_id 加入已處理集合
    mark_message_processed(message_id)
    
    user_id = update.effective_user.id
    logger.info(f"用戶 {user_id} 使用 /start 命令 (message_id={message_id})")
    
    # 調用 return_to_home 執行返回主頁的邏輯
    await return_to_home(update, context)


async def show_start_game_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    顯示開始遊戲的說明文案和官方客服按鈕，並切換到第一層遊戲菜單
    """
    user_id = update.effective_user.id
    
    # 創建官方客服 Inline 按鈕
    official_service_button = InlineKeyboardButton(
        text="官方客服",
        callback_data="official_service"
    )
    
    # 組裝 Inline Keyboard（只有一個按鈕）
    inline_keyboard = InlineKeyboardMarkup([
        [official_service_button]
    ])
    
    # 發送開始遊戲圖片（帶 Inline 按鈕）
    await send_photo_with_cache(
        update,
        context,
        "images/开始游戏.jpg",
        get_start_game_message(),
        reply_markup=inline_keyboard
    )
    
    # 發送「请选择」獨立訊息，並切換到第一層遊戲菜單
    await update.message.reply_text(
        "请选择",
        reply_markup=get_game_level1_keyboard()
    )
    
    # 更新用戶菜單狀態
    set_user_state(user_id, "game_level1")
    
    logger.info(f"已為用戶 {user_id} 顯示開始遊戲說明並切換到第一層遊戲菜單")


async def handle_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    處理「个人中心」按鈕和 /profile 指令
    顯示個人中心圖片和菜單
    :param update: Telegram Update 對象
    :param context: Context 對象
    """
    user_id = update.effective_user.id
    
    await send_photo_with_cache(
        update,
        context,
        "images/个人中心.jpg",
        get_profile_message()
    )
    await update.message.reply_text(
        "请选择",
        reply_markup=get_profile_keyboard()
    )
    set_user_state(user_id, "profile")
    logger.info(f"用戶 {user_id} 進入個人中心")


async def handle_deposit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    處理「充值」按鈕和 /deposit 指令
    提示用戶輸入充值金額
    :param update: Telegram Update 對象
    :param context: Context 對象
    """
    user_id = update.effective_user.id
    
    set_user_deposit_withdraw_state(user_id, "deposit")
    usdt_balance = get_user_usdt_balance(user_id)
    await update.message.reply_text(get_deposit_amount_prompt(f"{usdt_balance:.2f}"))
    logger.info(f"用戶 {user_id} 點擊充值按鈕或使用 /deposit 指令")


async def handle_withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    處理「提款」按鈕和 /withdraw 指令
    顯示提款方式選擇
    :param update: Telegram Update 對象
    :param context: Context 對象
    """
    from state import format_bank_card_number
    
    user_id = update.effective_user.id
    
    # 檢查用戶已綁定的提款方式
    buttons = []
    
    # 檢查銀行卡
    bank_card_number = get_user_bank_card_number(user_id)
    if bank_card_number:
        formatted_card = format_bank_card_number(bank_card_number)
        buttons.append(InlineKeyboardButton(
            text=f"银行卡：尾号 {formatted_card[-6:]}",
            callback_data="withdraw_method_bank_card"
        ))
    
    # 檢查USDT-TRC20
    trc20_address = get_user_wallet_address(user_id, "trc20")
    if trc20_address:
        buttons.append(InlineKeyboardButton(
            text=f"USDT-TRC20：尾数 {trc20_address[-6:]}",
            callback_data="withdraw_method_trc20"
        ))
    
    # 檢查USDT-ERC20
    erc20_address = get_user_wallet_address(user_id, "erc20")
    if erc20_address:
        buttons.append(InlineKeyboardButton(
            text=f"USDT-ERC20：尾数 {erc20_address[-6:]}",
            callback_data="withdraw_method_erc20"
        ))
    
    # 如果沒有任何綁定的提款方式，提示用戶
    if not buttons:
        await update.message.reply_text("您尚未绑定任何提款方式，请先前往安全中心绑定")
        logger.info(f"用戶 {user_id} 點擊提款按鈕或使用 /withdraw 指令，但未綁定任何提款方式")
        return
    
    # 創建 Inline Keyboard
    inline_keyboard = InlineKeyboardMarkup([buttons])
    
    # 設置提款狀態為選擇方式
    set_user_withdraw_state(user_id, "select_method")
    
    # 發送選擇提款方式訊息
    await update.message.reply_text(
        get_withdraw_method_selection_message(),
        reply_markup=inline_keyboard
    )
    logger.info(f"用戶 {user_id} 點擊提款按鈕或使用 /withdraw 指令，顯示 {len(buttons)} 個提款方式選項")


async def handle_customer_service(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    處理 /customer_service 指令
    發送系統訊息，提示用戶聯繫客服
    :param update: Telegram Update 對象
    :param context: Context 對象
    """
    user_id = update.effective_user.id
    
    # 獲取機器人的 username
    bot_info = await context.bot.get_me()
    bot_username = bot_info.username
    
    # 發送系統訊息
    message = f"请联系客服(@{bot_username})"
    await update.message.reply_text(message)
    
    logger.info(f"用戶 {user_id} 使用 /customer_service 指令，已發送客服聯繫訊息")
