"""
處理器工具模組
存放所有處理器使用的工具函數
"""

import logging
from telegram import Update, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.error import TimedOut, NetworkError

from handlers.constants import GAME_BUTTONS

logger = logging.getLogger(__name__)

# 圖片 File ID 緩存字典
# key: 圖片路徑, value: Telegram file_id
cached_media_ids: dict[str, str] = {}


def _create_game_buttons(prefix: str) -> list[InlineKeyboardButton]:
    """
    創建遊戲按鈕列表（用於報表功能）
    :param prefix: 回調數據前綴（"daily_report_game_" 或 "monthly_report_game_"）
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


# 導出工具函數供其他模組使用
__all__ = ['send_photo_with_cache', '_create_game_buttons', 'cached_media_ids']
