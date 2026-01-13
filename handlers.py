"""
處理器模組
存放所有 Telegram Bot 的處理函數
"""

import logging
import asyncio
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.error import TimedOut, NetworkError

try:
    from cachetools import TTLCache
    HAS_CACHETOOLS = True
except ImportError:
    HAS_CACHETOOLS = False
    # 注意：此時 logger 尚未定義，所以使用 logging 模組直接記錄
    logging.warning("cachetools 未安裝，將使用簡單的 set 進行消息去重（建議安裝：pip install cachetools）")

from messages import (
    get_profile_message,
    get_start_game_message,
    get_daily_report_message,
    get_weekly_report_message,
    get_account_info_message,
    get_deposit_amount_prompt,
    get_withdraw_amount_prompt,
    get_withdraw_success_message,
    get_deposit_info_message,
    get_user_check_message,
    get_bank_card_binding_message,
    get_bank_card_binding_success_message,
    get_bank_card_binding_failure_message,
    get_wallet_binding_message,
    get_wallet_binding_success_message,
    get_wallet_binding_failure_message,
    get_withdraw_method_selection_message,
    get_withdraw_password_prompt,
    get_withdraw_password_error_message,
    get_bank_card_required_message,
    get_password_mismatch_message,
    get_beginner_room_info_message,
    get_beginner_room_bet_selection_message,
    get_bet_success_message,
    get_waiting_hash_message,
    get_hash_result_message,
    get_current_room_message,
    get_auto_bet_amount_prompt,
    get_hash_wheel_info_message,
    get_win_caption_message
)
from keyboards import (
    get_home_keyboard,
    get_game_level1_keyboard,
    get_game_level2_keyboard,
    get_profile_keyboard,
    get_security_center_keyboard,
    get_personal_report_keyboard,
    get_beginner_room_betting_keyboard,
    get_hash_wheel_betting_keyboard,
    get_auto_bet_amount_keyboard,
    get_auto_bet_count_keyboard
)
from state import (
    get_user_state,
    set_user_state,
    reset_user_state,
    get_user_previous_state,
    get_user_betting_source,
    set_user_betting_source,
    get_user_report_date,
    set_user_report_date,
    get_user_report_game,
    set_user_report_game,
    get_user_report_message_id,
    set_user_report_message_id,
    get_user_weekly_report_start_date,
    set_user_weekly_report_start_date,
    get_user_weekly_report_message_id,
    set_user_weekly_report_message_id,
    get_user_weekly_report_game,
    set_user_weekly_report_game,
    get_user_deposit_withdraw_state,
    set_user_deposit_withdraw_state,
    get_user_account,
    get_user_password,
    get_user_login_status,
    get_user_bank_card_binding_state,
    set_user_bank_card_binding_state,
    get_user_wallet_binding_state,
    set_user_wallet_binding_state,
    get_user_bank_card_number,
    set_user_bank_card_number,
    format_bank_card_number,
    get_user_wallet_address,
    set_user_wallet_address,
    format_wallet_address,
    get_user_bank_card_password,
    set_user_bank_card_password,
    get_user_withdraw_state,
    set_user_withdraw_state,
    get_user_withdraw_method,
    set_user_withdraw_method,
    get_user_withdraw_amount,
    set_user_withdraw_amount,
    get_user_auto_bet_amount,
    set_user_auto_bet_amount,
    get_user_auto_bet_count,
    set_user_auto_bet_count,
    get_user_auto_bet_continuous,
    set_user_auto_bet_continuous,
    get_user_usdt_balance,
    deduct_user_balance,
    add_user_balance
)
from platform_api import (
    check_user_exists,
    register_user,
    login_user,
    check_user_login_status
)

logger = logging.getLogger(__name__)

# 圖片 File ID 緩存字典
# key: 圖片路徑, value: Telegram file_id
cached_media_ids: dict[str, str] = {}

# 通用消息常量
MESSAGE_FEATURE_DEVELOPING = "功能开发中..."

# 遊戲按鈕列表（用於報表功能）
GAME_BUTTONS = [
    "哈希转盘",
    "哈希大小",
    "哈希单双",
    "幸运哈希",
    "幸运庄闲",
    "平倍牛牛",
    "十倍牛牛",
    "百家乐",
]

# 測試用的哈希結果數據（實際應從API獲取）
TEST_HASH_VALUE = "...3c27e7b94**654**feb**32**"
TEST_HASH_URL = "https://tronscan.org/#/transaction/e540d19aa31f8770dec2064ac88e2864849cdc28340f4ba3c27e7b94654feb32"
TEST_BONUS = "1600"

# 所有菜單按鈕集合（用於檢查用戶是否點擊了菜單按鈕）
ALL_MENU_BUTTONS = {
    # 首頁按鈕
    "开始游戏", "个人中心", "充值", "提款",
    # 遊戲菜單按鈕
    "哈希转盘", "平倍牛牛", "十倍牛牛", "幸运庄闲", "更多游戏", "返回主页",
    "幸运哈希", "哈希单双", "哈希大小", "百家乐", "上一页",
    # 個人中心按鈕
    "报表中心", "安全中心", "返回主页",
    # 安全中心按鈕
    "银行卡绑定", "USDT-TRC20绑定", "USDT-ERC20绑定", "返回上页",
    # 個人報表按鈕
    "日统计", "周统计", "返回上页",
    # 初級房投注按鈕
    "2元", "5元", "10元", "30元", "50元", "自动下注", "确认当前房型", "返回房型选单",
    # 自動下注金額選擇按鈕
    # 自動下注次數選擇按鈕
    "10次", "30次", "50次", "100次", "持续下注到返回上页", "返回上页"
}

# 消息去重機制：儲存已處理過的 message_id
# 使用 TTLCache 自動清理過期條目（保留 1 小時，最多 10000 條）
# 如果沒有安裝 cachetools，則使用簡單的 set（最多保留 1000 條）
if HAS_CACHETOOLS:
    # 使用 TTL Cache：1 小時過期，最多 10000 條
    processed_message_ids: TTLCache[int, bool] = TTLCache(maxsize=10000, ttl=3600)
else:
    # 簡單的 set，手動限制大小
    _processed_message_ids_set: set[int] = set()
    _processed_message_ids_max_size = 1000
    
    class ProcessedMessageIds:
        """簡單的消息ID去重容器，限制最大大小"""
        def __init__(self):
            self._set: set[int] = set()
            self._max_size = 1000
        
        def __contains__(self, message_id: int) -> bool:
            return message_id in self._set
        
        def add(self, message_id: int) -> None:
            """添加 message_id，如果超過最大大小則清理最舊的條目"""
            if len(self._set) >= self._max_size:
                # 移除最舊的 100 條（簡單策略：轉為列表後移除前 100 個）
                items_to_remove = list(self._set)[:100]
                for item in items_to_remove:
                    self._set.discard(item)
            self._set.add(message_id)
    
    processed_message_ids = ProcessedMessageIds()

# 遊戲按鈕列表（用於報表功能）
GAME_BUTTONS = [
    "哈希转盘",
    "哈希大小",
    "哈希单双",
    "幸运哈希",
    "幸运庄闲",
    "平倍牛牛",
    "十倍牛牛",
    "百家乐",
]

# 測試用的哈希結果數據（實際應從API獲取）
TEST_HASH_VALUE = "...3c27e7b94**654**feb**32**"
TEST_HASH_URL = "https://tronscan.org/#/transaction/e540d19aa31f8770dec2064ac88e2864849cdc28340f4ba3c27e7b94654feb32"
TEST_BONUS = "1600"

# 所有菜單按鈕集合（用於檢查用戶是否點擊了菜單按鈕）
ALL_MENU_BUTTONS = {
    # 首頁按鈕
    "开始游戏", "个人中心", "充值", "提款",
    # 遊戲菜單按鈕
    "哈希转盘", "平倍牛牛", "十倍牛牛", "幸运庄闲", "更多游戏", "返回主页",
    "幸运哈希", "哈希单双", "哈希大小", "百家乐", "上一页",
    # 個人中心按鈕
    "报表中心", "安全中心", "返回主页",
    # 安全中心按鈕
    "银行卡绑定", "USDT-TRC20绑定", "USDT-ERC20绑定", "返回上页",
    # 個人報表按鈕
    "日统计", "周统计", "返回上页",
    # 初級房投注按鈕
    "2元", "5元", "10元", "30元", "50元", "自动下注", "确认当前房型", "返回房型选单",
    # 自動下注次數選擇按鈕
    "10次", "30次", "50次", "100次", "持续下注到返回上页", "返回上页"
}


def _create_game_buttons(prefix: str) -> list[InlineKeyboardButton]:
    """
    創建遊戲按鈕列表（用於報表功能）
    :param prefix: 回調數據前綴（"daily_report_game_" 或 "weekly_report_game_"）
    :return: 按鈕列表
    """
    return [
        InlineKeyboardButton(text=f"查看 {game}", callback_data=f"{prefix}{game}")
        for game in GAME_BUTTONS
    ]


async def send_photo_with_cache(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    image_path: str,
    caption: str,
    reply_markup=None
) -> None:
    """
    使用 File ID 緩存機制發送圖片
    
    :param update: Telegram Update 對象
    :param context: Context 對象
    :param image_path: 圖片文件路徑（相對於項目根目錄）
    :param caption: 圖片說明文字
    :param reply_markup: 可選的鍵盤標記
    """
    try:
        # 檢查緩存中是否已有 file_id
        if image_path in cached_media_ids:
            file_id = cached_media_ids[image_path]
            logger.info(f"使用緩存的 file_id 發送圖片: {image_path}")
            
            # 使用 file_id 發送圖片
            await update.message.reply_photo(
                photo=file_id,
                caption=caption,
                reply_markup=reply_markup,
                parse_mode="HTML"
            )
        else:
            # 緩存中沒有，從本地讀取並發送
            try:
                with open(image_path, 'rb') as photo_file:
                    sent_message = await update.message.reply_photo(
                        photo=photo_file,
                        caption=caption,
                        reply_markup=reply_markup,
                        parse_mode="HTML"
                    )
                
                # 提取 file_id 並存入緩存
                if sent_message.photo:
                    file_id = sent_message.photo[-1].file_id
                    cached_media_ids[image_path] = file_id
                    logger.info(f"已緩存圖片 file_id: {image_path} -> {file_id}")
                else:
                    logger.warning(f"發送圖片成功但無法提取 file_id: {image_path}")
            
            except FileNotFoundError:
                # 圖片文件不存在，降級為只發送文字
                logger.warning(f"圖片文件不存在，降級為純文字發送: {image_path}")
                await update.message.reply_text(
                    caption,
                    reply_markup=reply_markup,
                    parse_mode="HTML"
                )
    
    except Exception as e:
        # 其他異常，降級為只發送文字
        logger.error(f"發送圖片時發生錯誤，降級為純文字發送: {image_path}, 錯誤: {e}")
        await update.message.reply_text(
            caption,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )


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


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    處理 /start 命令
    每次使用 /start 都會發送認證訊息
    包含消息去重機制，防止 Telegram 因網絡延遲導致的自動重試
    """
    # 消息去重檢查：防止重複處理同一條消息
    message_id = update.message.message_id
    
    if message_id in processed_message_ids:
        logger.warning(f"⚠️ 忽略重複請求：message_id={message_id}, user_id={update.effective_user.id}")
        return
    
    # 將 message_id 加入已處理集合
    if HAS_CACHETOOLS:
        processed_message_ids[message_id] = True
    else:
        processed_message_ids.add(message_id)
    
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


async def handle_inline_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    處理 Inline 按鈕點擊（双向客服、官方客服、观战频道、日統計報表等）
    """
    query = update.callback_query
    user_id = update.effective_user.id
    
    # 清除所有綁定狀態（用戶點擊了 Inline 按鈕，表示要進行其他操作）
    if get_user_bank_card_binding_state(user_id):
        set_user_bank_card_binding_state(user_id, False)
        logger.info(f"用戶 {user_id} 點擊 Inline 按鈕，清除銀行卡綁定狀態")
    
    if get_user_wallet_binding_state(user_id):
        set_user_wallet_binding_state(user_id, None)
        logger.info(f"用戶 {user_id} 點擊 Inline 按鈕，清除錢包綁定狀態")
    
    if get_user_deposit_withdraw_state(user_id):
        set_user_deposit_withdraw_state(user_id, None)
        logger.info(f"用戶 {user_id} 點擊 Inline 按鈕，清除充值/提款狀態")
    
    if get_user_withdraw_state(user_id):
        set_user_withdraw_state(user_id, None)
        set_user_withdraw_method(user_id, None)
        set_user_withdraw_amount(user_id, None)
        logger.info(f"用戶 {user_id} 點擊 Inline 按鈕，清除提款流程狀態")
    
    # 回答回調查詢（防止 Telegram 顯示加載動畫）
    try:
        await query.answer()
    except Exception as e:
        logger.warning(f"回答回調查詢時發生錯誤（可忽略）: {e}")
    
    callback_data = query.data
    logger.info(f"用戶 {user_id} 點擊了 Inline 按鈕: {callback_data}")
    
    # 處理日統計報表的按鈕
    if callback_data.startswith("daily_report_"):
        await handle_daily_report_buttons(update, context, callback_data)
        return
    
    # 處理周統計報表的按鈕
    if callback_data.startswith("weekly_report_"):
        await handle_weekly_report_buttons(update, context, callback_data)
        return
    
    
    # 處理提款方式選擇
    if callback_data.startswith("withdraw_method_"):
        method = callback_data.replace("withdraw_method_", "")
        set_user_withdraw_method(user_id, method)
        set_user_withdraw_state(user_id, "enter_amount")
        
        # 刪除選擇提款方式的消息
        try:
            await query.message.delete()
        except Exception as e:
            logger.warning(f"刪除消息失敗（可忽略）: {e}")
        
        # 發送輸入金額提示
        usdt_balance = get_user_usdt_balance(user_id)
        await query.message.chat.send_message(get_withdraw_amount_prompt(f"{usdt_balance:.2f}"))
        logger.info(f"用戶 {user_id} 選擇提款方式: {method}")
        return
    
    # 處理初級房投注金額選擇（已廢棄，改用 execute_single_bet）
    if callback_data.startswith("beginner_bet_"):
        bet_amount = callback_data.replace("beginner_bet_", "")
        await execute_single_bet(context, query.message.chat.id, user_id, bet_amount)
        return
    
    # 處理官方客服按鈕
    if callback_data == "official_service":
        # 獲取機器人的 username
        bot_info = await context.bot.get_me()
        bot_username = bot_info.username
        
        # 發送系統訊息（與 /customer_service 相同）
        message = f"请联系客服(@{bot_username})"
        await query.message.reply_text(message)
        logger.info(f"用戶 {user_id} 點擊官方客服按鈕，已發送客服聯繫訊息")
        return
    
    # 處理其他已廢棄的按鈕（保留以兼容舊代碼）
    if callback_data in ("two_way_service", "official_channel", "watch_channel"):
        await query.message.reply_text(MESSAGE_FEATURE_DEVELOPING)


async def handle_daily_report_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
    """
    處理日統計報表的 Inline 按鈕點擊
    """
    query = update.callback_query
    user_id = update.effective_user.id
    
    current_date = get_user_report_date(user_id)
    current_game = get_user_report_game(user_id)
    
    # 處理「上一日」
    if callback_data == "daily_report_prev_day":
        # 日期減一天
        date_obj = datetime.strptime(current_date, "%Y-%m-%d")
        new_date = (date_obj - timedelta(days=1)).strftime("%Y-%m-%d")
        set_user_report_date(user_id, new_date)
        current_date = new_date
        logger.info(f"用戶 {user_id} 切換到上一日：{new_date}")
    
    # 處理「下一日」
    elif callback_data == "daily_report_next_day":
        # 日期加一天
        date_obj = datetime.strptime(current_date, "%Y-%m-%d")
        new_date = (date_obj + timedelta(days=1)).strftime("%Y-%m-%d")
        set_user_report_date(user_id, new_date)
        current_date = new_date
        logger.info(f"用戶 {user_id} 切換到下一日：{new_date}")
    
    # 處理遊戲類型按鈕
    elif callback_data.startswith("daily_report_game_"):
        game_name = callback_data.replace("daily_report_game_", "")
        set_user_report_game(user_id, game_name)
        current_game = game_name
        logger.info(f"用戶 {user_id} 切換遊戲類型：{game_name}")
    
    # 創建 Inline 按鈕（與之前相同）
    prev_day_button = InlineKeyboardButton(
        text="上一日",
        callback_data="daily_report_prev_day"
    )
    next_day_button = InlineKeyboardButton(
        text="下一日",
        callback_data="daily_report_next_day"
    )
    total_button = InlineKeyboardButton(
        text="总计",
        callback_data="daily_report_game_总计"
    )
    
    game_buttons = _create_game_buttons("daily_report_game_")
    
    inline_keyboard = InlineKeyboardMarkup([
        [prev_day_button, total_button, next_day_button],  # 下一日和总计互换位置
        [game_buttons[0], game_buttons[1]],
        [game_buttons[2], game_buttons[3]],
        [game_buttons[4], game_buttons[5]],
        [game_buttons[6], game_buttons[7]]
    ])
    
    # 刪除原消息並重新發送
    try:
        await query.message.delete()
    except Exception as e:
        logger.warning(f"刪除消息失敗（可忽略）: {e}")
    
    # 重新發送更新後的報表訊息
    sent_message = await query.message.chat.send_message(
        get_daily_report_message(current_date, current_game),
        reply_markup=inline_keyboard
    )
    
    # 更新消息ID
    set_user_report_message_id(user_id, sent_message.message_id)


async def show_daily_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    顯示日統計報表（輔助函數，可在不同狀態下調用）
    """
    user_id = update.effective_user.id
    current_date = get_user_report_date(user_id)
    current_game = get_user_report_game(user_id)
    
    # 創建日統計報表的 Inline 按鈕
    prev_day_button = InlineKeyboardButton(
        text="上一日",
        callback_data="daily_report_prev_day"
    )
    next_day_button = InlineKeyboardButton(
        text="下一日",
        callback_data="daily_report_next_day"
    )
    total_button = InlineKeyboardButton(
        text="总计",
        callback_data="daily_report_game_总计"
    )
    
    # 遊戲按鈕
    game_buttons = [
        InlineKeyboardButton(text="查看 哈希转盘", callback_data="daily_report_game_哈希转盘"),
        InlineKeyboardButton(text="查看 哈希大小", callback_data="daily_report_game_哈希大小"),
        InlineKeyboardButton(text="查看 哈希单双", callback_data="daily_report_game_哈希单双"),
        InlineKeyboardButton(text="查看 幸运哈希", callback_data="daily_report_game_幸运哈希"),
        InlineKeyboardButton(text="查看 幸运庄闲", callback_data="daily_report_game_幸运庄闲"),
        InlineKeyboardButton(text="查看 平倍牛牛", callback_data="daily_report_game_平倍牛牛"),
        InlineKeyboardButton(text="查看 十倍牛牛", callback_data="daily_report_game_十倍牛牛"),
        InlineKeyboardButton(text="查看 百家乐", callback_data="daily_report_game_百家乐"),
    ]
    
    # 組裝 Inline Keyboard（下一日和总计互换位置）
    inline_keyboard = InlineKeyboardMarkup([
        [prev_day_button, total_button, next_day_button],  # 第一行：上一日、总计、下一日
        [game_buttons[0], game_buttons[1]],  # 第二行：哈希转盘、哈希大小
        [game_buttons[2], game_buttons[3]],  # 第三行：哈希单双、幸运哈希
        [game_buttons[4], game_buttons[5]],  # 第四行：幸运庄闲、平倍牛牛
        [game_buttons[6], game_buttons[7]]   # 第五行：十倍牛牛、百家乐
    ])
    
    # 發送日統計報表訊息（帶 Inline 按鈕）
    sent_message = await update.message.reply_text(
        get_daily_report_message(current_date, current_game),
        reply_markup=inline_keyboard
    )
    
    # 保存消息ID
    set_user_report_message_id(user_id, sent_message.message_id)
    set_user_state(user_id, "daily_report")
    logger.info(f"用戶 {user_id} 進入日統計報表，日期：{current_date}，遊戲：{current_game}")


async def show_weekly_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    顯示周統計報表（輔助函數，可在不同狀態下調用）
    """
    user_id = update.effective_user.id
    start_date = get_user_weekly_report_start_date(user_id)
    current_game = get_user_weekly_report_game(user_id)
    
    # 創建周統計報表的 Inline 按鈕
    prev_week_button = InlineKeyboardButton(
        text="上一周",
        callback_data="weekly_report_prev_week"
    )
    next_week_button = InlineKeyboardButton(
        text="下一周",
        callback_data="weekly_report_next_week"
    )
    total_button = InlineKeyboardButton(
        text="总计",
        callback_data="weekly_report_game_总计"
    )
    
    # 遊戲按鈕
    game_buttons = _create_game_buttons("weekly_report_game_")
    
    # 組裝 Inline Keyboard（與日統計相同的布局）
    inline_keyboard = InlineKeyboardMarkup([
        [prev_week_button, total_button, next_week_button],  # 第一行：上一周、总计、下一周
        [game_buttons[0], game_buttons[1]],  # 第二行：哈希转盘、哈希大小
        [game_buttons[2], game_buttons[3]],  # 第三行：哈希单双、幸运哈希
        [game_buttons[4], game_buttons[5]],  # 第四行：幸运庄闲、平倍牛牛
        [game_buttons[6], game_buttons[7]]   # 第五行：十倍牛牛、百家乐
    ])
    
    # 發送周統計報表訊息（帶 Inline 按鈕）
    sent_message = await update.message.reply_text(
        get_weekly_report_message(start_date, current_game),
        reply_markup=inline_keyboard
    )
    
    # 保存消息ID
    set_user_weekly_report_message_id(user_id, sent_message.message_id)
    set_user_state(user_id, "weekly_report")
    logger.info(f"用戶 {user_id} 進入周統計報表，開始日期：{start_date}，遊戲：{current_game}")


async def handle_weekly_report_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
    """
    處理周統計報表的 Inline 按鈕點擊
    """
    from datetime import datetime, timedelta
    
    query = update.callback_query
    user_id = update.effective_user.id
    
    # 獲取當前開始日期和遊戲類型
    current_start_date_str = get_user_weekly_report_start_date(user_id)
    current_start_date = datetime.strptime(current_start_date_str, "%Y-%m-%d")
    current_game = get_user_weekly_report_game(user_id)
    
    # 處理「上一周」和「下一周」
    if callback_data == "weekly_report_prev_week":
        # 往前推7天
        new_start_date = current_start_date - timedelta(days=7)
        new_start_date_str = new_start_date.strftime("%Y-%m-%d")
        set_user_weekly_report_start_date(user_id, new_start_date_str)
        logger.info(f"用戶 {user_id} 點擊「上一周」，日期從 {current_start_date_str} 變更為 {new_start_date_str}")
    elif callback_data == "weekly_report_next_week":
        # 往後推7天
        new_start_date = current_start_date + timedelta(days=7)
        new_start_date_str = new_start_date.strftime("%Y-%m-%d")
        set_user_weekly_report_start_date(user_id, new_start_date_str)
        logger.info(f"用戶 {user_id} 點擊「下一周」，日期從 {current_start_date_str} 變更為 {new_start_date_str}")
    elif callback_data.startswith("weekly_report_game_"):
        # 處理遊戲類型切換
        game_name = callback_data.replace("weekly_report_game_", "")
        set_user_weekly_report_game(user_id, game_name)
        current_game = game_name
        logger.info(f"用戶 {user_id} 切換周統計遊戲類型為：{game_name}")
    else:
        return
    
    # 獲取更新後的開始日期和遊戲類型
    updated_start_date_str = get_user_weekly_report_start_date(user_id)
    updated_game = get_user_weekly_report_game(user_id)
    
    # 重新構建 Inline 按鈕
    prev_week_button = InlineKeyboardButton(
        text="上一周",
        callback_data="weekly_report_prev_week"
    )
    next_week_button = InlineKeyboardButton(
        text="下一周",
        callback_data="weekly_report_next_week"
    )
    total_button = InlineKeyboardButton(
        text="总计",
        callback_data="weekly_report_game_总计"
    )
    
    # 遊戲按鈕
    game_buttons = _create_game_buttons("weekly_report_game_")
    
    # 組裝 Inline Keyboard（與日統計相同的布局）
    inline_keyboard = InlineKeyboardMarkup([
        [prev_week_button, total_button, next_week_button],  # 第一行：上一周、总计、下一周
        [game_buttons[0], game_buttons[1]],  # 第二行：哈希转盘、哈希大小
        [game_buttons[2], game_buttons[3]],  # 第三行：哈希单双、幸运哈希
        [game_buttons[4], game_buttons[5]],  # 第四行：幸运庄闲、平倍牛牛
        [game_buttons[6], game_buttons[7]]   # 第五行：十倍牛牛、百家乐
    ])
    
    # 刪除原消息並重新發送
    try:
        await query.message.delete()
    except Exception as e:
        logger.warning(f"刪除消息失敗（可忽略）: {e}")
    
    # 重新發送更新後的報表訊息
    sent_message = await query.message.chat.send_message(
        get_weekly_report_message(updated_start_date_str, updated_game),
        reply_markup=inline_keyboard
    )
    
    # 更新消息ID
    set_user_weekly_report_message_id(user_id, sent_message.message_id)


async def execute_single_bet(context: ContextTypes.DEFAULT_TYPE, chat_id: int, user_id: int, bet_amount: str) -> bool:
    """
    執行單次下注的輔助函數
    :param context: Context 對象
    :param chat_id: 聊天ID
    :param user_id: 用戶ID
    :param bet_amount: 下注金額（字符串，如 "2", "5", "10"）
    :return: 是否成功執行（False表示失敗，應該停止自動下注）
    """
    import random
    
    try:
        # 轉換投注金額為浮點數
        bet_amount_float = float(bet_amount)
        
        # 檢查餘額是否足夠
        current_balance = get_user_usdt_balance(user_id)
        if current_balance < bet_amount_float:
            try:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"余额不足！当前余额：{current_balance:.2f} USDT，需要：{bet_amount_float:.2f} USDT"
                )
            except (TimedOut, NetworkError) as e:
                logger.error(f"發送餘額不足消息時發生網絡錯誤: {e}")
            logger.warning(f"用戶 {user_id} 餘額不足，當前餘額: {current_balance:.2f}，需要: {bet_amount_float:.2f}")
            return False
        
        # 扣除餘額
        deduct_user_balance(user_id, bet_amount_float)
        new_balance = get_user_usdt_balance(user_id)
        logger.info(f"用戶 {user_id} 扣除投注金額: {bet_amount_float:.2f} USDT，剩餘餘額: {new_balance:.2f} USDT")
        
        # 發送第一則報文：投注成功（帶金額和餘額）
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=get_bet_success_message(f"{bet_amount_float:.2f}", f"{new_balance:.2f}")
            )
        except (TimedOut, NetworkError) as e:
            logger.error(f"發送投注成功消息時發生網絡錯誤: {e}，但繼續執行下注流程")
        
        # 發送第二則報文：請稍等哈希結果
        try:
            await context.bot.send_message(chat_id=chat_id, text=get_waiting_hash_message())
        except (TimedOut, NetworkError) as e:
            logger.error(f"發送等待哈希結果消息時發生網絡錯誤: {e}，但繼續執行下注流程")
        
        logger.info(f"用戶 {user_id} 執行單次下注，金額: {bet_amount_float:.2f} USDT")
        
        # 等待3秒
        await asyncio.sleep(3)
        
        # 中獎判定：50%機率中獎
        is_winner = random.random() < 0.5
        
        # 記錄投注時間
        bet_time = datetime.now()
        
        if is_winner:
            # 中獎：生成隨機中獎金額（0.05-100.00，保留兩位小數）
            bonus_amount = round(random.uniform(0.05, 100.00), 2)
            
            # 增加餘額（派獎）
            add_user_balance(user_id, bonus_amount)
            final_balance = get_user_usdt_balance(user_id)
            logger.info(f"用戶 {user_id} 中獎，彩金: {bonus_amount:.2f} USDT，當前餘額: {final_balance:.2f} USDT")
            
            # 準備生成中獎圖片所需的資料
            try:
                # 獲取遊戲名稱（從 betting_source 轉換）
                betting_source = get_user_betting_source(user_id)
                if betting_source == "hash_wheel":
                    game_name = "哈希轉盤"
                else:
                    game_name = "哈希轉盤"  # 默認值
                
                # 獲取交易哈希（清理格式）
                transaction_hash = TEST_HASH_VALUE.replace("**", "")
                
                # 獲取投注玩家名稱
                player_name = get_user_account(user_id) or f"用戶{user_id}"
                
                # 計算遊戲結果（從哈希值提取最後一位數字）
                # TEST_HASH_VALUE 格式：...3c27e7b94**654**feb**32**
                # 提取最後的數字部分作為結果
                import re
                hash_numbers = re.findall(r'\d+', TEST_HASH_VALUE)
                if hash_numbers:
                    # 取最後一個數字的最後一位作為結果
                    last_digit = hash_numbers[-1][-1] if hash_numbers[-1] else "0"
                    game_result = f"尾數 {last_digit}"
                else:
                    game_result = "未知"
                
                # 生成中獎圖片
                from win_image_generator import generate_win_image
                image_path = generate_win_image(
                    game_name=game_name,
                    transaction_hash=transaction_hash,
                    player_name=player_name,
                    bet_amount=bet_amount_float,
                    win_amount=bonus_amount,
                    game_result=game_result,
                    bet_time=bet_time
                )
                
                # 生成 caption
                caption = get_win_caption_message(
                    game_name=game_name,
                    bet_amount=f"{bet_amount_float:.2f}",
                    win_amount=f"{bonus_amount:.2f}",
                    bet_time=bet_time.strftime("%Y-%m-%d %H:%M:%S"),
                    final_balance=f"{final_balance:.2f}"
                )
                
                # 使用 sendPhoto 發送圖片和 caption
                try:
                    with open(image_path, 'rb') as photo_file:
                        await context.bot.send_photo(
                            chat_id=chat_id,
                            photo=photo_file,
                            caption=caption,
                            parse_mode="HTML"
                        )
                    logger.info(f"已發送中獎圖片: {image_path}")
                except (TimedOut, NetworkError) as e:
                    logger.error(f"發送中獎圖片時發生網絡錯誤: {e}")
                    # 如果發送圖片失敗，降級為只發送文字訊息
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=get_hash_result_message(
                            f"{bonus_amount:.2f}",
                            TEST_HASH_VALUE,
                            TEST_HASH_URL,
                            f"{final_balance:.2f}"
                        ),
                        parse_mode="HTML"
                    )
                except Exception as e:
                    logger.error(f"發送中獎圖片時發生未知錯誤: {e}", exc_info=True)
                    # 如果發送圖片失敗，降級為只發送文字訊息
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=get_hash_result_message(
                            f"{bonus_amount:.2f}",
                            TEST_HASH_VALUE,
                            TEST_HASH_URL,
                            f"{final_balance:.2f}"
                        ),
                        parse_mode="HTML"
                    )
            except Exception as e:
                logger.error(f"生成中獎圖片時發生錯誤: {e}", exc_info=True)
                # 如果圖片生成失敗，降級為只發送文字訊息
                try:
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=get_hash_result_message(
                            f"{bonus_amount:.2f}",
                            TEST_HASH_VALUE,
                            TEST_HASH_URL,
                            f"{final_balance:.2f}"
                        ),
                        parse_mode="HTML"
                    )
                except (TimedOut, NetworkError) as send_error:
                    logger.error(f"發送中獎結果消息時發生網絡錯誤: {send_error}")
                # 即使發送失敗，下注流程也算完成
        else:
            # 未中獎
            logger.info(f"用戶 {user_id} 未中獎，當前餘額: {new_balance:.2f} USDT")
            
            # 發送第二則報文：哈希結果（未中獎）
            try:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=get_hash_result_message("0.00", TEST_HASH_VALUE, TEST_HASH_URL),
                    parse_mode="HTML"
                )
            except (TimedOut, NetworkError) as e:
                logger.error(f"發送未中獎結果消息時發生網絡錯誤: {e}")
                # 即使發送失敗，下注流程也算完成
        
        return True
        
    except Exception as e:
        logger.error(f"執行單次下注時發生未知錯誤: {e}", exc_info=True)
        # 發生未知錯誤時，返回False表示失敗，應該停止自動下注
        return False


async def handle_reply_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    處理 Reply Keyboard 按鈕點擊
    當用戶點擊底部常駐菜單的按鈕時，會發送對應的文字訊息
    """
    user_id = update.effective_user.id
    message_text = update.message.text
    
    # 獲取所有已知的菜單按鈕集合
    all_menu_buttons = ALL_MENU_BUTTONS
    
    # 如果用戶點擊了菜單按鈕，清除所有綁定狀態
    if message_text in all_menu_buttons:
        # 清除銀行卡綁定狀態
        if get_user_bank_card_binding_state(user_id):
            set_user_bank_card_binding_state(user_id, False)
            logger.info(f"用戶 {user_id} 點擊菜單按鈕，清除銀行卡綁定狀態")
        
        # 清除錢包綁定狀態
        if get_user_wallet_binding_state(user_id):
            set_user_wallet_binding_state(user_id, None)
            logger.info(f"用戶 {user_id} 點擊菜單按鈕，清除錢包綁定狀態")
        
        # 清除充值/提款狀態
        if get_user_deposit_withdraw_state(user_id):
            set_user_deposit_withdraw_state(user_id, None)
            logger.info(f"用戶 {user_id} 點擊菜單按鈕，清除充值/提款狀態")
        
        # 清除提款流程狀態
        if get_user_withdraw_state(user_id):
            set_user_withdraw_state(user_id, None)
            set_user_withdraw_method(user_id, None)
            set_user_withdraw_amount(user_id, None)
            logger.info(f"用戶 {user_id} 點擊菜單按鈕，清除提款流程狀態")
    
    # 檢查用戶是否在輸入銀行卡資料（只有在不是菜單按鈕時才檢查）
    if message_text not in all_menu_buttons and get_user_bank_card_binding_state(user_id):
        # 用戶正在輸入銀行卡資料
        bank_card_data = message_text.strip()
        # 檢查是否符合格式（5行資料）
        lines = [line.strip() for line in bank_card_data.split('\n') if line.strip()]
        if len(lines) == 5:
            # 符合格式
            # 保存銀行卡號（第二行是銀行卡號）
            card_number = lines[1]
            # 保存提款密碼（第五行是4位數提款密碼）
            password = lines[4]
            
            # 檢查是否已經綁定過銀行卡（綁定第二張銀行卡時需要驗證密碼）
            existing_password = get_user_bank_card_password(user_id)
            if existing_password:
                # 已經綁定過銀行卡，需要驗證密碼是否一致
                if password != existing_password:
                    await update.message.reply_text(get_password_mismatch_message())
                    logger.info(f"用戶 {user_id} 綁定第二張銀行卡時密碼不一致")
                    return
            
            # 密碼驗證通過或首次綁定，保存資料
            set_user_bank_card_number(user_id, card_number)
            set_user_bank_card_password(user_id, password)
            await update.message.reply_text(get_bank_card_binding_success_message())
            set_user_bank_card_binding_state(user_id, False)
            logger.info(f"用戶 {user_id} 銀行卡綁定成功，卡號: {card_number}")
        else:
            # 不符合格式，綁定失敗
            await update.message.reply_text(get_bank_card_binding_failure_message())
            logger.info(f"用戶 {user_id} 銀行卡綁定失敗，資料行數: {len(lines)}")
        return
    
    # 檢查用戶是否在輸入錢包資料（只有在不是菜單按鈕時才檢查）
    wallet_binding_state = get_user_wallet_binding_state(user_id)
    if message_text not in all_menu_buttons and wallet_binding_state in {"trc20", "erc20"}:
        # 用戶正在輸入錢包資料
        wallet_data = message_text.strip()
        # 檢查是否符合格式（2行資料：錢包地址 + 提款密碼）
        lines = [line.strip() for line in wallet_data.split('\n') if line.strip()]
        if len(lines) == 2:
            # 符合格式
            # 保存錢包地址（第一行是錢包地址）
            wallet_address = lines[0]
            # 獲取提款密碼（第二行是提款密碼）
            password = lines[1]
            
            # 驗證密碼是否與首次綁定銀行卡的密碼一致
            bank_card_password = get_user_bank_card_password(user_id)
            if not bank_card_password:
                # 如果沒有綁定銀行卡，不應該到這裡（應該在點擊按鈕時就檢查）
                await update.message.reply_text(get_bank_card_required_message())
                set_user_wallet_binding_state(user_id, None)
                logger.warning(f"用戶 {user_id} 嘗試綁定錢包但未綁定銀行卡")
                return
            
            if password != bank_card_password:
                # 密碼不一致
                await update.message.reply_text(get_password_mismatch_message())
                logger.info(f"用戶 {user_id} {wallet_binding_state.upper()} 錢包綁定時密碼不一致")
                return
            
            # 密碼驗證通過，保存錢包地址
            set_user_wallet_address(user_id, wallet_binding_state, wallet_address)
            await update.message.reply_text(get_wallet_binding_success_message())
            set_user_wallet_binding_state(user_id, None)
            logger.info(f"用戶 {user_id} {wallet_binding_state.upper()} 錢包綁定成功，地址: {wallet_address}")
        else:
            # 不符合格式，綁定失敗
            await update.message.reply_text(get_wallet_binding_failure_message())
            logger.info(f"用戶 {user_id} {wallet_binding_state.upper()} 錢包綁定失敗，資料行數: {len(lines)}")
        return
    
    # 檢查用戶是否在輸入充值/提現金額（只有在不是菜單按鈕時才檢查）
    deposit_withdraw_state = get_user_deposit_withdraw_state(user_id)
    if message_text not in all_menu_buttons:
        if deposit_withdraw_state == "deposit":
            # 用戶正在輸入充值金額
            amount = message_text.strip()
            # 發送充值地址圖片和訊息
            await send_photo_with_cache(
                update,
                context,
                "images/地址二维码.jpg",
                get_deposit_info_message(amount)
            )
            # 清除狀態
            set_user_deposit_withdraw_state(user_id, None)
            logger.info(f"用戶 {user_id} 輸入充值金額: {amount}")
            return
        elif deposit_withdraw_state == "withdraw":
            # 舊的提款流程（已廢棄，保留以備兼容）
            amount = message_text.strip()
            await update.message.reply_text(get_withdraw_success_message())
            set_user_deposit_withdraw_state(user_id, None)
            logger.info(f"用戶 {user_id} 輸入提款金額: {amount}")
            return
    
    # 檢查新的提款流程狀態
    withdraw_state = get_user_withdraw_state(user_id)
    if message_text not in all_menu_buttons and withdraw_state:
        if withdraw_state == "enter_amount":
            # 用戶正在輸入提款金額
            amount = message_text.strip()
            set_user_withdraw_amount(user_id, amount)
            set_user_withdraw_state(user_id, "enter_password")
            await update.message.reply_text(get_withdraw_password_prompt())
            logger.info(f"用戶 {user_id} 輸入提款金額: {amount}")
            return
        elif withdraw_state == "enter_password":
            # 用戶正在輸入提款密碼
            password = message_text.strip()
            # 獲取用戶綁定的銀行卡密碼
            bank_card_password = get_user_bank_card_password(user_id)
            
            if bank_card_password and password == bank_card_password:
                # 密碼正確
                await update.message.reply_text(get_withdraw_success_message())
                # 清除所有提款相關狀態
                set_user_withdraw_state(user_id, None)
                set_user_withdraw_method(user_id, None)
                set_user_withdraw_amount(user_id, None)
                logger.info(f"用戶 {user_id} 提款密碼驗證成功，提款申請已送出")
            else:
                # 密碼錯誤
                await update.message.reply_text(get_withdraw_password_error_message())
                logger.info(f"用戶 {user_id} 提款密碼驗證失敗")
            return
    
    # 獲取用戶當前的菜單狀態（默認為首頁）
    current_state = get_user_state(user_id)
    
    logger.info(f"用戶 {user_id} 點擊了按鈕: {message_text}，當前菜單狀態: {current_state}")
    
    # ==========================================
    # 處理首頁按鈕
    # ==========================================
    if current_state == "home":
        home_buttons = {"开始游戏", "个人中心", "充值", "提款"}
        
        if message_text not in home_buttons:
            return
        
        # 處理「开始游戏」按鈕
        if message_text == "开始游戏":
            await show_start_game_info(update, context)
            return
        
        # 處理「个人中心」按鈕
        if message_text == "个人中心":
            await handle_profile(update, context)
            return
        
        # 處理「充值」按鈕
        if message_text == "充值":
            await handle_deposit(update, context)
            return
        
        # 處理「提款」按鈕
        if message_text == "提款":
            await handle_withdraw(update, context)
            return
        
        # 其他首頁按鈕
        await update.message.reply_text(MESSAGE_FEATURE_DEVELOPING)
        return
    
    # ==========================================
    # 處理第一層遊戲菜單按鈕
    # ==========================================
    elif current_state == "game_level1":
        level1_buttons = {"哈希转盘", "平倍牛牛", "十倍牛牛", "幸运庄闲", "更多游戏", "返回主页"}
        
        if message_text not in level1_buttons:
            return
        
        # 處理「返回主页」
        if message_text == "返回主页":
            await return_to_home(update, context)
            return
        
        # 處理「更多游戏」
        if message_text == "更多游戏":
            await update.message.reply_text(
                "请选择",
                reply_markup=get_game_level2_keyboard()
            )
            set_user_state(user_id, "game_level2")
            logger.info(f"用戶 {user_id} 進入第二層遊戲菜單")
            return
        
        # 處理第一層遊戲按鈕（平倍牛牛、十倍牛牛、幸运庄闲）
        game_image_map = {
            "平倍牛牛": "images/平倍牛牛.jpg",
            "十倍牛牛": "images/十倍牛牛.jpg",
            "幸运庄闲": "images/幸运庄闲.jpg"
        }
        
        if message_text in game_image_map:
            await send_photo_with_cache(
                update,
                context,
                game_image_map[message_text],
                message_text
            )
            logger.info(f"用戶 {user_id} 查看遊戲: {message_text}")
            return
        
        # 處理「哈希转盘」按鈕
        if message_text == "哈希转盘":
            # 發送第一段詳細說明報文（移除「初級房」標題）
            await update.message.reply_text(get_hash_wheel_info_message())
            
            # 發送第二段報文（帶 Reply Keyboard，直接進入投注選擇）
            usdt_balance = get_user_usdt_balance(user_id)
            await update.message.reply_text(
                get_beginner_room_bet_selection_message(f"{usdt_balance:.2f}", "0"),
                reply_markup=get_hash_wheel_betting_keyboard()
            )
            # set_user_state 會自動記錄上一個狀態為 "game_level1"
            set_user_state(user_id, "beginner_room_betting")
            # 標記來源為哈希轉盤
            set_user_betting_source(user_id, "hash_wheel")
            logger.info(f"用戶 {user_id} 點擊哈希轉盤，直接進入投注選擇")
            return
        
        # 其他第一層遊戲按鈕（遊戲功能）
        await update.message.reply_text(MESSAGE_FEATURE_DEVELOPING)
        return
    
    # ==========================================
    # 處理第二層遊戲菜單按鈕
    # ==========================================
    elif current_state == "game_level2":
        level2_buttons = {"幸运哈希", "哈希单双", "哈希大小", "百家乐", "上一页"}
        
        if message_text not in level2_buttons:
            return
        
        # 處理「上一页」
        if message_text == "上一页":
            await update.message.reply_text(
                "请选择",
                reply_markup=get_game_level1_keyboard()
            )
            set_user_state(user_id, "game_level1")
            logger.info(f"用戶 {user_id} 返回第一層遊戲菜單")
            return
        
        # 處理第二層遊戲按鈕（幸运哈希、哈希单双、哈希大小、百家乐）
        game_image_map = {
            "幸运哈希": "images/幸运哈希.jpg",
            "哈希单双": "images/哈希单双.jpg",
            "哈希大小": "images/哈希大小.jpg",
            "百家乐": "images/百家乐.jpg"
        }
        
        if message_text in game_image_map:
            await send_photo_with_cache(
                update,
                context,
                game_image_map[message_text],
                message_text
            )
            logger.info(f"用戶 {user_id} 查看遊戲: {message_text}")
            return
        
        # 其他第二層遊戲按鈕（遊戲功能）
        await update.message.reply_text(MESSAGE_FEATURE_DEVELOPING)
        return
    
    # ==========================================
    # 處理個人中心菜單按鈕
    # ==========================================
    elif current_state == "profile":
        profile_buttons = {"报表中心", "安全中心", "返回主页"}
        
        if message_text not in profile_buttons:
            return
        
        # 處理「报表中心」
        if message_text == "报表中心":
            # 直接進入個人報表菜單
            await update.message.reply_text(
                "请选择",
                reply_markup=get_personal_report_keyboard()
            )
            set_user_state(user_id, "personal_report")
            logger.info(f"用戶 {user_id} 進入個人報表菜單")
            return
        
        # 處理「安全中心」
        if message_text == "安全中心":
            await update.message.reply_text(
                "请选择",
                reply_markup=get_security_center_keyboard()
            )
            set_user_state(user_id, "security_center")
            logger.info(f"用戶 {user_id} 進入安全中心菜單")
            return
        
        # 處理「返回主页」
        if message_text == "返回主页":
            await return_to_home(update, context)
            return
    
    # ==========================================
    # 處理安全中心菜單按鈕
    # ==========================================
    elif current_state == "security_center":
        security_buttons = {"银行卡绑定", "USDT-TRC20绑定", "USDT-ERC20绑定", "返回上页"}
        
        if message_text not in security_buttons:
            return
        
        # 處理「返回上页」
        if message_text == "返回上页":
            await update.message.reply_text(
                "请选择",
                reply_markup=get_profile_keyboard()
            )
            set_user_state(user_id, "profile")
            logger.info(f"用戶 {user_id} 從安全中心返回個人中心")
            return
        
        # 處理「银行卡绑定」按鈕
        if message_text == "银行卡绑定":
            set_user_bank_card_binding_state(user_id, True)
            # 檢查是否已有綁定的銀行卡號
            current_card_number = get_user_bank_card_number(user_id)
            formatted_card_number = None
            if current_card_number:
                formatted_card_number = format_bank_card_number(current_card_number)
            await update.message.reply_text(get_bank_card_binding_message(formatted_card_number))
            logger.info(f"用戶 {user_id} 點擊銀行卡綁定按鈕")
            return
        
        # 處理「USDT-TRC20绑定」按鈕
        if message_text == "USDT-TRC20绑定":
            # 檢查是否已綁定銀行卡
            if not get_user_bank_card_password(user_id):
                await update.message.reply_text(get_bank_card_required_message())
                logger.info(f"用戶 {user_id} 點擊 USDT-TRC20 綁定按鈕，但未綁定銀行卡")
                return
            
            set_user_wallet_binding_state(user_id, "trc20")
            # 檢查是否已有綁定的錢包地址
            current_address = get_user_wallet_address(user_id, "trc20")
            formatted_address = None
            if current_address:
                formatted_address = format_wallet_address(current_address)
            await update.message.reply_text(get_wallet_binding_message(formatted_address))
            logger.info(f"用戶 {user_id} 點擊 USDT-TRC20 綁定按鈕")
            return
        
        # 處理「USDT-ERC20绑定」按鈕
        if message_text == "USDT-ERC20绑定":
            # 檢查是否已綁定銀行卡
            if not get_user_bank_card_password(user_id):
                await update.message.reply_text(get_bank_card_required_message())
                logger.info(f"用戶 {user_id} 點擊 USDT-ERC20 綁定按鈕，但未綁定銀行卡")
                return
            
            set_user_wallet_binding_state(user_id, "erc20")
            # 檢查是否已有綁定的錢包地址
            current_address = get_user_wallet_address(user_id, "erc20")
            formatted_address = None
            if current_address:
                formatted_address = format_wallet_address(current_address)
            await update.message.reply_text(get_wallet_binding_message(formatted_address))
            logger.info(f"用戶 {user_id} 點擊 USDT-ERC20 綁定按鈕")
            return
    
    # ==========================================
    # 處理報表中心菜單按鈕
    # ==========================================
    
    # ==========================================
    # 處理個人報表菜單按鈕
    # ==========================================
    elif current_state == "personal_report":
        personal_report_buttons = {"日统计", "周统计", "返回上页"}
        
        if message_text not in personal_report_buttons:
            return
        
        # 處理「返回上页」
        if message_text == "返回上页":
            previous_state = get_user_previous_state(user_id)
            
            # 根據上一個狀態返回對應的菜單
            if previous_state == "profile":
                # 從個人中心進入的，返回個人中心
                await update.message.reply_text(
                    "请选择",
                    reply_markup=get_profile_keyboard()
                )
                set_user_state(user_id, "profile")
                logger.info(f"用戶 {user_id} 從個人報表返回個人中心")
            else:
                # 默認返回首頁
                await update.message.reply_text(
                    "💡 使用底部按钮快速操作",
                    reply_markup=get_home_keyboard()
                )
                set_user_state(user_id, "home")
                logger.info(f"用戶 {user_id} 從個人報表返回首頁（默認）")
            return
        
        # 處理「日统计」
        if message_text == "日统计":
            await show_daily_report(update, context)
            return
        
        # 處理「周统计」
        if message_text == "周统计":
            await show_weekly_report(update, context)
            return
    
    # ==========================================
    # 處理日統計報表狀態下的按鈕
    # ==========================================
    elif current_state == "daily_report":
        # 允許在日統計狀態下切換到周統計或返回上頁
        personal_report_buttons = {"日统计", "周统计", "返回上页"}
        
        if message_text not in personal_report_buttons:
            return
        
        # 處理「返回上页」
        if message_text == "返回上页":
            previous_state = get_user_previous_state(user_id)
            
            # 根據上一個狀態返回對應的菜單
            if previous_state == "profile":
                # 從個人中心進入的，返回個人中心
                await update.message.reply_text(
                    "请选择",
                    reply_markup=get_profile_keyboard()
                )
                set_user_state(user_id, "profile")
                logger.info(f"用戶 {user_id} 從日統計返回個人中心")
            else:
                # 默認返回首頁
                await update.message.reply_text(
                    "💡 使用底部按钮快速操作",
                    reply_markup=get_home_keyboard()
                )
                set_user_state(user_id, "home")
                logger.info(f"用戶 {user_id} 從日統計返回首頁（默認）")
            return
        
        # 處理「周统计」
        if message_text == "周统计":
            await show_weekly_report(update, context)
            return
        
        # 處理「日统计」（重新顯示日統計）
        if message_text == "日统计":
            await show_daily_report(update, context)
            return
    
    # ==========================================
    # 處理周統計報表狀態下的按鈕
    # ==========================================
    elif current_state == "weekly_report":
        # 允許在周統計狀態下切換到日統計或返回上頁
        personal_report_buttons = {"日统计", "周统计", "返回上页"}
        
        if message_text not in personal_report_buttons:
            return
        
        # 處理「返回上页」
        if message_text == "返回上页":
            previous_state = get_user_previous_state(user_id)
            
            # 根據上一個狀態返回對應的菜單
            if previous_state == "profile":
                # 從個人中心進入的，返回個人中心
                await update.message.reply_text(
                    "请选择",
                    reply_markup=get_profile_keyboard()
                )
                set_user_state(user_id, "profile")
                logger.info(f"用戶 {user_id} 從周統計返回個人中心")
            else:
                # 默認返回首頁
                await update.message.reply_text(
                    "💡 使用底部按钮快速操作",
                    reply_markup=get_home_keyboard()
                )
                set_user_state(user_id, "home")
                logger.info(f"用戶 {user_id} 從周統計返回首頁（默認）")
            return
        
        # 處理「日统计」
        if message_text == "日统计":
            await show_daily_report(update, context)
            return
        
        # 處理「周统计」（重新顯示周統計）
        if message_text == "周统计":
            await show_weekly_report(update, context)
            return
    
    # ==========================================
    # 處理初級房投注狀態下的按鈕
    # ==========================================
    elif current_state == "beginner_room_betting":
        betting_buttons = {"2元", "5元", "10元", "30元", "50元", "100元", "150元", "200元", "300元", "500元", "自动下注", "确认当前房型", "返回房型选单", "返回上页"}
        
        if message_text not in betting_buttons:
            return
        
        # 處理「返回上页」按鈕（從哈希轉盤進入時使用）
        if message_text == "返回上页":
            betting_source = get_user_betting_source(user_id)
            if betting_source == "hash_wheel":
                # 從哈希轉盤進入的，返回到第一層遊戲菜單
                await update.message.reply_text(
                    "请选择",
                    reply_markup=get_game_level1_keyboard()
                )
                set_user_state(user_id, "game_level1")
                # 清除來源標記
                set_user_betting_source(user_id, None)
                logger.info(f"用戶 {user_id} 從哈希轉盤投注返回第一層遊戲菜單")
            else:
                # 從其他途徑進入的，預設返回第一層遊戲菜單
                await update.message.reply_text(
                    "请选择",
                    reply_markup=get_game_level1_keyboard()
                )
                set_user_state(user_id, "game_level1")
                # 清除來源標記
                set_user_betting_source(user_id, None)
                logger.info(f"用戶 {user_id} 從投注選擇返回第一層遊戲菜單")
            return
        
        # 處理「自动下注」按鈕
        if message_text == "自动下注":
            usdt_balance = get_user_usdt_balance(user_id)
            await update.message.reply_text(
                get_auto_bet_amount_prompt(f"{usdt_balance:.2f}"),
                reply_markup=get_auto_bet_amount_keyboard()
            )
            set_user_state(user_id, "auto_bet_amount_selection")
            logger.info(f"用戶 {user_id} 選擇自動下注，進入金額選擇")
            return
        
        # 處理投注金額按鈕（2元、5元、10元、30元、50元、100元、150元、200元、300元、500元）
        if message_text in {"2元", "5元", "10元", "30元", "50元", "100元", "150元", "200元", "300元", "500元"}:
            # 提取投注金額（移除"元"字）
            bet_amount = message_text.replace("元", "")
            bet_amount_float = float(bet_amount)
            
            # 檢查餘額是否足夠
            current_balance = get_user_usdt_balance(user_id)
            if current_balance < bet_amount_float:
                await update.message.reply_text(
                    f"余额不足！当前余额：{current_balance:.2f} USDT，需要：{bet_amount_float:.2f} USDT"
                )
                logger.warning(f"用戶 {user_id} 餘額不足，當前餘額: {current_balance:.2f}，需要: {bet_amount_float:.2f}")
                return
            
            logger.info(f"用戶 {user_id} 選擇初級房投注金額: {message_text}")
            
            # 使用 execute_single_bet 處理投注
            asyncio.create_task(
                execute_single_bet(context, update.message.chat.id, user_id, bet_amount)
            )
            return
        
        # 處理「确认当前房型」按鈕
        if message_text == "确认当前房型":
            await update.message.reply_text(get_current_room_message())
            logger.info(f"用戶 {user_id} 確認當前房型")
            return
        
        # 處理「返回房型选单」按鈕（返回到第一層遊戲菜單）
        if message_text == "返回房型选单":
            await update.message.reply_text(
                "请选择",
                reply_markup=get_game_level1_keyboard()
            )
            set_user_state(user_id, "game_level1")
            logger.info(f"用戶 {user_id} 從初級房投注返回第一層遊戲菜單")
            return
    
    # ==========================================
    # 處理自動下注金額選擇狀態下的按鈕
    # ==========================================
    elif current_state == "auto_bet_amount_selection":
        amount_buttons = {"2元", "5元", "10元", "30元", "50元", "100元", "150元", "200元", "300元", "500元", "返回上页"}
        
        if message_text not in amount_buttons:
            return
        
        # 處理「返回上页」按鈕
        if message_text == "返回上页":
            # 檢查用戶來源，決定返回到哪個菜單
            betting_source = get_user_betting_source(user_id)
            usdt_balance = get_user_usdt_balance(user_id)
            
            if betting_source == "hash_wheel":
                # 從哈希轉盤進入的，返回哈希轉盤投注菜單
                await update.message.reply_text(
                    get_beginner_room_bet_selection_message(f"{usdt_balance:.2f}", "0"),
                    reply_markup=get_hash_wheel_betting_keyboard()
                )
                set_user_state(user_id, "beginner_room_betting")
                # 保持來源標記
                set_user_betting_source(user_id, "hash_wheel")
                logger.info(f"用戶 {user_id} 從自動下注金額選擇返回哈希轉盤投注")
            else:
                # 從其他途徑進入的，返回初級房投注菜單
                await update.message.reply_text(
                    get_beginner_room_bet_selection_message(f"{usdt_balance:.2f}", "0"),
                    reply_markup=get_beginner_room_betting_keyboard()
                )
                set_user_state(user_id, "beginner_room_betting")
                # 保持來源標記（如果有的話）
                if betting_source:
                    set_user_betting_source(user_id, betting_source)
                logger.info(f"用戶 {user_id} 從自動下注金額選擇返回初級房投注")
            return
        
        # 處理金額選擇按鈕（2元、5元、10元、30元、50元、100元、150元、200元、300元、500元）
        if message_text in {"2元", "5元", "10元", "30元", "50元", "100元", "150元", "200元", "300元", "500元"}:
            # 保存選擇的金額
            bet_amount = message_text.replace("元", "")
            set_user_auto_bet_amount(user_id, bet_amount)
            
            # 切換到次數選擇
            usdt_balance = get_user_usdt_balance(user_id)
            await update.message.reply_text(
                f"当前USDT余额：{usdt_balance:.2f}\n请选择下注次数",
                reply_markup=get_auto_bet_count_keyboard()
            )
            set_user_state(user_id, "auto_bet_count_selection")
            logger.info(f"用戶 {user_id} 選擇自動下注金額: {bet_amount}元，進入次數選擇")
            return
    
    # ==========================================
    # 處理自動下注次數選擇狀態下的按鈕
    # ==========================================
    elif current_state == "auto_bet_count_selection":
        count_buttons = {"10次", "30次", "50次", "100次", "持续下注到返回上页", "返回上页"}
        
        if message_text not in count_buttons:
            return
        
        # 處理「返回上页」按鈕
        if message_text == "返回上页":
            # 檢查用戶來源，決定返回到哪個菜單
            betting_source = get_user_betting_source(user_id)
            
            # 檢查是否正在持續下注
            if get_user_auto_bet_continuous(user_id):
                # 停止持續下注
                set_user_auto_bet_continuous(user_id, False)
                usdt_balance = get_user_usdt_balance(user_id)
                
                if betting_source == "hash_wheel":
                    # 從哈希轉盤進入的，返回哈希轉盤投注菜單
                    await update.message.reply_text(
                        "已停止持续自动下注",
                        reply_markup=get_hash_wheel_betting_keyboard()
                    )
                    # 保持來源標記
                    set_user_betting_source(user_id, "hash_wheel")
                else:
                    # 從其他途徑進入的，返回初級房投注菜單
                    await update.message.reply_text(
                        "已停止持续自动下注",
                        reply_markup=get_beginner_room_betting_keyboard()
                    )
                    # 保持來源標記（如果有的話）
                    if betting_source:
                        set_user_betting_source(user_id, betting_source)
                set_user_state(user_id, "beginner_room_betting")
                set_user_auto_bet_amount(user_id, None)
                set_user_auto_bet_count(user_id, None)
                logger.info(f"用戶 {user_id} 停止持續自動下注")
            else:
                # 檢查是否有固定次數下注正在執行
                bet_count = get_user_auto_bet_count(user_id)
                if bet_count:
                    # 固定次數下注正在執行，允許返回但不停止下注（下注會繼續執行）
                    await update.message.reply_text(
                        "已返回，但自动下注将继续执行直到完成",
                        reply_markup=get_auto_bet_amount_keyboard()
                    )
                    set_user_state(user_id, "auto_bet_amount_selection")
                    # 不清除金額和次數，讓下注循環繼續
                    logger.info(f"用戶 {user_id} 從自動下注次數選擇返回金額選擇，但下注繼續執行")
                else:
                    # 沒有正在執行的下注，正常返回
                    usdt_balance = get_user_usdt_balance(user_id)
                    await update.message.reply_text(
                        get_auto_bet_amount_prompt(f"{usdt_balance:.2f}"),
                        reply_markup=get_auto_bet_amount_keyboard()
                    )
                    set_user_state(user_id, "auto_bet_amount_selection")
                    # 清除已選擇的金額
                    set_user_auto_bet_amount(user_id, None)
                    logger.info(f"用戶 {user_id} 從自動下注次數選擇返回金額選擇")
            return
        
        # 獲取選擇的金額
        bet_amount = get_user_auto_bet_amount(user_id)
        if not bet_amount:
            # 如果沒有金額，返回金額選擇
            usdt_balance = get_user_usdt_balance(user_id)
            await update.message.reply_text(
                get_auto_bet_amount_prompt(f"{usdt_balance:.2f}"),
                reply_markup=get_auto_bet_amount_keyboard()
            )
            set_user_state(user_id, "auto_bet_amount_selection")
            logger.warning(f"用戶 {user_id} 選擇次數但沒有金額，返回金額選擇")
            return
        
        # 處理次數選擇
        if message_text == "持续下注到返回上页":
            # 持續下注模式
            set_user_auto_bet_count(user_id, None)  # None 表示持續下注
            set_user_auto_bet_continuous(user_id, True)
            await update.message.reply_text(
                "已开始持续自动下注，点击「返回上页」可停止下注",
                reply_markup=get_auto_bet_count_keyboard()
            )
            logger.info(f"用戶 {user_id} 開始持續自動下注，金額: {bet_amount}元")
            
            # 啟動持續下注循環（異步執行）
            async def continuous_bet_loop():
                chat_id = update.message.chat.id
                bet_amount_float = float(bet_amount)
                try:
                    while get_user_auto_bet_continuous(user_id):
                        # 檢查餘額是否足夠
                        current_balance = get_user_usdt_balance(user_id)
                        if current_balance < bet_amount_float:
                            try:
                                await context.bot.send_message(
                                    chat_id=chat_id,
                                    text=f"余额不足，自动下注已停止。当前余额：{current_balance:.2f} USDT"
                                )
                            except (TimedOut, NetworkError) as e:
                                logger.error(f"發送餘額不足消息時發生網絡錯誤: {e}")
                            set_user_auto_bet_continuous(user_id, False)
                            break
                        
                        # 執行單次下注，如果返回False則停止
                        success = await execute_single_bet(context, chat_id, user_id, bet_amount)
                        if not success:
                            logger.warning(f"用戶 {user_id} 持續自動下注因執行失敗而停止")
                            set_user_auto_bet_continuous(user_id, False)
                            break
                except Exception as e:
                    logger.error(f"持續自動下注循環發生錯誤: {e}", exc_info=True)
                    set_user_auto_bet_continuous(user_id, False)
                    try:
                        await context.bot.send_message(
                            chat_id=chat_id,
                            text="自动下注过程中发生错误，已自动停止"
                        )
                    except Exception as send_error:
                        logger.error(f"發送錯誤消息時發生異常: {send_error}")
                finally:
                    logger.info(f"用戶 {user_id} 持續自動下注已停止")
            
            asyncio.create_task(continuous_bet_loop())
            return
        
        elif message_text in {"10次", "30次", "50次", "100次"}:
            # 固定次數下注模式
            count = int(message_text.replace("次", ""))
            set_user_auto_bet_count(user_id, count)
            set_user_auto_bet_continuous(user_id, False)
            
            await update.message.reply_text(
                f"已开始自动下注 {count} 次，金额: {bet_amount} USDT",
                reply_markup=get_auto_bet_count_keyboard()
            )
            logger.info(f"用戶 {user_id} 開始自動下注 {count} 次，金額: {bet_amount}元")
            
            # 啟動固定次數下注循環（異步執行）
            async def fixed_count_bet_loop():
                chat_id = update.message.chat.id
                saved_count = count  # 保存次數，因為可能會被清除
                saved_bet_amount = bet_amount  # 保存金額
                saved_bet_amount_float = float(saved_bet_amount)
                completed_count = 0
                
                try:
                    # 無論用戶是否點擊返回上頁，都執行完所有次數（除非餘額不足或執行失敗）
                    for i in range(saved_count):
                        # 檢查餘額是否足夠
                        current_balance = get_user_usdt_balance(user_id)
                        if current_balance < saved_bet_amount_float:
                            try:
                                await context.bot.send_message(
                                    chat_id=chat_id,
                                    text=f"余额不足，自动下注已停止。当前余额：{current_balance:.2f} USDT，已完成 {i}/{saved_count} 次"
                                )
                            except (TimedOut, NetworkError) as e:
                                logger.error(f"發送餘額不足消息時發生網絡錯誤: {e}")
                            break
                        
                        # 執行單次下注，如果返回False則停止
                        success = await execute_single_bet(context, chat_id, user_id, saved_bet_amount)
                        if not success:
                            logger.warning(f"用戶 {user_id} 自動下注第 {i+1} 次執行失敗，停止下注")
                            break
                        completed_count = i + 1
                    
                    # 完成後發送完成消息並清理狀態
                    try:
                        await context.bot.send_message(
                            chat_id=chat_id,
                            text=f"自动下注 {saved_count} 次已完成（实际完成 {completed_count} 次）"
                        )
                    except (TimedOut, NetworkError) as e:
                        logger.error(f"發送完成消息時發生網絡錯誤: {e}")
                    
                    # 清理自動下注相關狀態
                    current_state = get_user_state(user_id)
                    # 如果當前在自動下注相關狀態，恢復到對應的投注菜單
                    if current_state in {"auto_bet_count_selection", "auto_bet_amount_selection"}:
                        try:
                            # 檢查用戶來源，決定返回到哪個菜單
                            betting_source = get_user_betting_source(user_id)
                            if betting_source == "hash_wheel":
                                # 從哈希轉盤進入的，返回哈希轉盤投注菜單
                                await context.bot.send_message(
                                    chat_id=chat_id,
                                    text="请选择",
                                    reply_markup=get_hash_wheel_betting_keyboard()
                                )
                                # 保持來源標記
                                set_user_betting_source(user_id, "hash_wheel")
                            else:
                                # 從其他途徑進入的，返回初級房投注菜單
                                await context.bot.send_message(
                                    chat_id=chat_id,
                                    text="请选择",
                                    reply_markup=get_beginner_room_betting_keyboard()
                                )
                                # 保持來源標記（如果有的話）
                                if betting_source:
                                    set_user_betting_source(user_id, betting_source)
                            set_user_state(user_id, "beginner_room_betting")
                        except (TimedOut, NetworkError) as e:
                            logger.error(f"恢復菜單狀態時發生網絡錯誤: {e}")
                    
                    set_user_auto_bet_amount(user_id, None)
                    set_user_auto_bet_count(user_id, None)
                    logger.info(f"用戶 {user_id} 自動下注 {saved_count} 次已完成（实际完成 {completed_count} 次）")
                    
                except Exception as e:
                    logger.error(f"固定次數自動下注循環發生錯誤: {e}", exc_info=True)
                    try:
                        await context.bot.send_message(
                            chat_id=chat_id,
                            text=f"自动下注过程中发生错误，已停止。实际完成 {completed_count}/{saved_count} 次"
                        )
                    except Exception as send_error:
                        logger.error(f"發送錯誤消息時發生異常: {send_error}")
                    # 清理狀態
                    set_user_auto_bet_amount(user_id, None)
                    set_user_auto_bet_count(user_id, None)
            
            asyncio.create_task(fixed_count_bet_loop())
            return
    
    # 如果狀態未知，重置為首頁
    else:
        reset_user_state(user_id)
        await update.message.reply_text(
            "💡 使用底部按钮快速操作",
            reply_markup=get_home_keyboard()
        )

