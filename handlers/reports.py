"""
報表處理模組
處理日統計和月統計報表相關功能
"""

import logging
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from messages import (
    get_daily_report_message,
    get_monthly_report_message
)
from state import (
    get_user_report_date,
    set_user_report_date,
    get_user_report_game,
    set_user_report_game,
    set_user_report_message_id,
    get_user_monthly_report_month,
    set_user_monthly_report_month,
    get_user_monthly_report_game,
    set_user_monthly_report_game,
    set_user_monthly_report_message_id,
    set_user_state
)
from handlers.utils import _create_game_buttons

logger = logging.getLogger(__name__)


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


async def show_monthly_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    顯示月統計報表（輔助函數，可在不同狀態下調用）
    """
    user_id = update.effective_user.id
    current_month = get_user_monthly_report_month(user_id)
    current_game = get_user_monthly_report_game(user_id)
    
    # 創建月統計報表的 Inline 按鈕
    prev_month_button = InlineKeyboardButton(
        text="上一月",
        callback_data="monthly_report_prev_month"
    )
    next_month_button = InlineKeyboardButton(
        text="下一月",
        callback_data="monthly_report_next_month"
    )
    total_button = InlineKeyboardButton(
        text="总计",
        callback_data="monthly_report_game_总计"
    )
    
    # 遊戲按鈕
    game_buttons = _create_game_buttons("monthly_report_game_")
    
    # 組裝 Inline Keyboard（與日統計相同的布局）
    inline_keyboard = InlineKeyboardMarkup([
        [prev_month_button, total_button, next_month_button],  # 第一行：上一月、总计、下一月
        [game_buttons[0], game_buttons[1]],  # 第二行：哈希转盘、哈希大小
        [game_buttons[2], game_buttons[3]],  # 第三行：哈希单双、幸运哈希
        [game_buttons[4], game_buttons[5]],  # 第四行：幸运庄闲、平倍牛牛
        [game_buttons[6], game_buttons[7]]   # 第五行：十倍牛牛、百家乐
    ])
    
    # 發送月統計報表訊息（帶 Inline 按鈕）
    sent_message = await update.message.reply_text(
        get_monthly_report_message(current_month, current_game),
        reply_markup=inline_keyboard
    )
    
    # 保存消息ID
    set_user_monthly_report_message_id(user_id, sent_message.message_id)
    set_user_state(user_id, "monthly_report")
    logger.info(f"用戶 {user_id} 進入月統計報表，月份：{current_month}，遊戲：{current_game}")


async def handle_monthly_report_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
    """
    處理月統計報表的 Inline 按鈕點擊
    """
    query = update.callback_query
    user_id = update.effective_user.id
    
    # 獲取當前月份和遊戲類型
    current_month_str = get_user_monthly_report_month(user_id)
    current_game = get_user_monthly_report_game(user_id)
    
    # 解析當前月份
    year, month_num = map(int, current_month_str.split("-"))
    current_month = datetime(year, month_num, 1)
    
    # 處理「上一月」和「下一月」
    if callback_data == "monthly_report_prev_month":
        # 往前推一個月
        if month_num == 1:
            new_month = datetime(year - 1, 12, 1)
        else:
            new_month = datetime(year, month_num - 1, 1)
        new_month_str = new_month.strftime("%Y-%m")
        set_user_monthly_report_month(user_id, new_month_str)
        logger.info(f"用戶 {user_id} 點擊「上一月」，月份從 {current_month_str} 變更為 {new_month_str}")
    elif callback_data == "monthly_report_next_month":
        # 往後推一個月
        if month_num == 12:
            new_month = datetime(year + 1, 1, 1)
        else:
            new_month = datetime(year, month_num + 1, 1)
        new_month_str = new_month.strftime("%Y-%m")
        set_user_monthly_report_month(user_id, new_month_str)
        logger.info(f"用戶 {user_id} 點擊「下一月」，月份從 {current_month_str} 變更為 {new_month_str}")
    elif callback_data.startswith("monthly_report_game_"):
        # 處理遊戲類型切換
        game_name = callback_data.replace("monthly_report_game_", "")
        set_user_monthly_report_game(user_id, game_name)
        current_game = game_name
        logger.info(f"用戶 {user_id} 切換月統計遊戲類型為：{game_name}")
    else:
        return
    
    # 獲取更新後的月份和遊戲類型
    updated_month_str = get_user_monthly_report_month(user_id)
    updated_game = get_user_monthly_report_game(user_id)
    
    # 重新構建 Inline 按鈕
    prev_month_button = InlineKeyboardButton(
        text="上一月",
        callback_data="monthly_report_prev_month"
    )
    next_month_button = InlineKeyboardButton(
        text="下一月",
        callback_data="monthly_report_next_month"
    )
    total_button = InlineKeyboardButton(
        text="总计",
        callback_data="monthly_report_game_总计"
    )
    
    # 遊戲按鈕
    game_buttons = _create_game_buttons("monthly_report_game_")
    
    # 組裝 Inline Keyboard（與日統計相同的布局）
    inline_keyboard = InlineKeyboardMarkup([
        [prev_month_button, total_button, next_month_button],  # 第一行：上一月、总计、下一月
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
        get_monthly_report_message(updated_month_str, updated_game),
        reply_markup=inline_keyboard
    )
    
    # 更新消息ID
    set_user_monthly_report_message_id(user_id, sent_message.message_id)
