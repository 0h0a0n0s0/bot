"""
Telegram Bot - 主程式入口
使用 python-telegram-bot (v20+)
"""

import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from telegram.error import TimedOut, NetworkError

# 導入配置
from config import (
    BOT_TOKEN,
    READ_TIMEOUT,
    WRITE_TIMEOUT,
    CONNECT_TIMEOUT,
    POOL_TIMEOUT
)

# 導入處理器
from handlers import (
    start_command,
    show_start_game_info,
    handle_profile,
    handle_deposit,
    handle_withdraw,
    handle_customer_service,
    handle_inline_buttons,
    handle_reply_keyboard
)

# 日誌配置
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def run_bot_async():
    """運行 Telegram Bot（異步版本）"""
    # 配置 Application，設置超時時間
    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .read_timeout(READ_TIMEOUT)
        .write_timeout(WRITE_TIMEOUT)
        .connect_timeout(CONNECT_TIMEOUT)
        .pool_timeout(POOL_TIMEOUT)
        .build()
    )
    
    # 註冊命令處理器
    # /start - 回到主页
    application.add_handler(CommandHandler("start", start_command))
    # /game - 开始游戏
    application.add_handler(CommandHandler("game", show_start_game_info))
    # /profile - 个人中心
    application.add_handler(CommandHandler("profile", handle_profile))
    # /deposit - 充值
    application.add_handler(CommandHandler("deposit", handle_deposit))
    # /withdraw - 提款
    application.add_handler(CommandHandler("withdraw", handle_withdraw))
    # /customerservice - 客戶服務
    application.add_handler(CommandHandler("customer_service", handle_customer_service))
    
    # 註冊回調查詢處理器（處理 Inline 按鈕點擊）
    application.add_handler(CallbackQueryHandler(handle_inline_buttons))
    
    # 註冊訊息處理器（處理 Reply Keyboard 按鈕點擊）
    application.add_handler(
        MessageHandler(
            filters.TEXT,
            handle_reply_keyboard
        )
    )
    
    # 註冊全局錯誤處理器
    async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """處理所有未捕獲的異常"""
        logger.error(f"處理更新時發生異常: {context.error}", exc_info=context.error)
        
        # 如果是網路超時錯誤，記錄但不中斷程序
        if isinstance(context.error, (TimedOut, NetworkError)):
            logger.warning(f"網路超時或連接錯誤（已忽略）: {context.error}")
        else:
            # 對於其他錯誤，嘗試發送錯誤消息給用戶（如果可能）
            if update and update.effective_message:
                try:
                    await update.effective_message.reply_text(
                        "抱歉，處理您的請求時發生錯誤，請稍後再試。"
                    )
                except Exception:
                    # 如果連發送錯誤消息都失敗，就忽略
                    pass
    
    application.add_error_handler(error_handler)
    
    logger.info("Telegram Bot 啟動中...")
    await application.initialize()
    await application.start()
    await application.updater.start_polling(allowed_updates=Update.ALL_TYPES)
    logger.info("Telegram Bot 已啟動並開始輪詢")
    
    # 保持運行直到停止
    try:
        await asyncio.Event().wait()  # 永遠等待
    except asyncio.CancelledError:
        await application.updater.stop()
        await application.stop()
        await application.shutdown()


async def main():
    """主函數：運行 Bot"""
    # 檢查 Bot Token 是否已設置
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE" or not BOT_TOKEN:
        logger.error("⚠️  請先在代碼中設置 BOT_TOKEN！")
        print("\n" + "="*60)
        print("⚠️  錯誤：未設置 Bot Token")
        print("="*60)
        print("請編輯 config.py 檔案，將 BOT_TOKEN 設為你的 Telegram Bot Token")
        print("="*60 + "\n")
        return
    
    # 運行 Bot
    await run_bot_async()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Telegram Bot - 新版本互動方式")
    print("="*60)
    print("機器人已準備就緒，等待用戶指令...")
    print("="*60 + "\n")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("程式已停止")
