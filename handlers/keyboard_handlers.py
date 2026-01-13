"""
鍵盤處理子模組
處理所有 Reply Keyboard 按鈕點擊的具體邏輯
"""
import logging
import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import TimedOut, NetworkError

from messages import (
    get_deposit_info_message,
    get_deposit_success_message,
    get_withdraw_success_message,
    get_withdraw_password_prompt,
    get_withdraw_password_error_message,
    get_password_mismatch_message,
    get_bank_card_binding_message,
    get_bank_card_binding_success_message,
    get_bank_card_binding_failure_message,
    get_wallet_binding_message,
    get_wallet_binding_success_message,
    get_wallet_binding_failure_message,
    get_bank_card_required_message,
    get_hash_wheel_info_message,
    get_beginner_room_bet_selection_message,
    get_current_room_message,
    get_auto_bet_amount_prompt,
    get_withdrawal_password_setup_message,
    get_withdrawal_password_confirm_message,
    get_withdrawal_password_success_message,
    get_withdrawal_password_mismatch_message
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
    get_auto_bet_count_keyboard,
    get_password_input_keyboard
)
from state import (
    get_user_state,
    set_user_state,
    reset_user_state,
    get_user_previous_state,
    get_user_bank_card_binding_state,
    set_user_bank_card_binding_state,
    get_user_wallet_binding_state,
    set_user_wallet_binding_state,
    get_user_deposit_withdraw_state,
    get_user_withdrawal_password_state,
    set_user_withdrawal_password_state,
    get_user_withdrawal_password_input,
    set_user_withdrawal_password_input,
    get_user_withdrawal_password_confirm,
    set_user_withdrawal_password_confirm,
    get_user_withdrawal_password_message_id,
    set_user_withdrawal_password_message_id,
    set_user_deposit_withdraw_state,
    get_user_withdraw_state,
    set_user_withdraw_state,
    set_user_withdraw_method,
    set_user_withdraw_amount,
    get_user_bank_card_number,
    set_user_bank_card_number,
    format_bank_card_number,
    get_user_bank_card_password,
    set_user_bank_card_password,
    get_user_wallet_address,
    set_user_wallet_address,
    format_wallet_address,
    get_user_usdt_balance,
    get_user_betting_source,
    set_user_betting_source,
    get_user_auto_bet_amount,
    set_user_auto_bet_amount,
    get_user_auto_bet_count,
    set_user_auto_bet_count,
    get_user_auto_bet_continuous,
    set_user_auto_bet_continuous,
    add_user_balance
)
from handlers.constants import ALL_MENU_BUTTONS, MESSAGE_FEATURE_DEVELOPING
from handlers.utils import send_photo_with_cache
from handlers.commands import (
    show_start_game_info,
    handle_profile,
    handle_deposit,
    handle_withdraw
)
from handlers.base import return_to_home
from handlers.reports import show_daily_report, show_monthly_report
from handlers.betting import execute_single_bet

logger = logging.getLogger(__name__)

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
        
        # 清除提款密碼設置狀態
        if get_user_withdrawal_password_state(user_id):
            set_user_withdrawal_password_state(user_id, None)
            logger.info(f"用戶 {user_id} 點擊菜單按鈕，清除提款密碼設置狀態")
    
    
    # 檢查用戶是否在輸入銀行卡資料（只有在不是菜單按鈕時才檢查）
    if message_text not in all_menu_buttons and get_user_bank_card_binding_state(user_id):
        # 用戶正在輸入銀行卡資料
        bank_card_data = message_text.strip()
        # 檢查是否符合格式（4行資料，已移除提款密碼）
        lines = [line.strip() for line in bank_card_data.split('\n') if line.strip()]
        if len(lines) == 4:
            # 符合格式
            # 保存銀行卡號（第二行是銀行卡號）
            card_number = lines[1]
            
            # 檢查是否已設置提款密碼
            existing_password = get_user_bank_card_password(user_id)
            if not existing_password:
                await update.message.reply_text("请先设置提款密码")
                set_user_bank_card_binding_state(user_id, False)
                logger.info(f"用戶 {user_id} 嘗試綁定銀行卡但未設置提款密碼")
                return
            
            # 保存資料
            set_user_bank_card_number(user_id, card_number)
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
            try:
                amount_float = float(amount)
            except ValueError:
                await update.message.reply_text("请输入有效的充值金额")
                return
            
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
            
            # 10秒後自動發送充值成功消息並更新餘額
            async def send_deposit_success():
                await asyncio.sleep(10)
                try:
                    # 增加餘額
                    add_user_balance(user_id, amount_float)
                    new_balance = get_user_usdt_balance(user_id)
                    
                    # 發送充值成功消息
                    await context.bot.send_message(
                        chat_id=update.message.chat_id,
                        text=get_deposit_success_message(amount, f"{new_balance:.2f}")
                    )
                    logger.info(f"用戶 {user_id} 充值成功，金額: {amount_float} USDT，新餘額: {new_balance:.2f} USDT")
                except Exception as e:
                    logger.error(f"發送充值成功消息時發生錯誤: {e}")
            
            # 啟動異步任務
            asyncio.create_task(send_deposit_success())
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
        security_buttons = {"提款密码", "USDT-TRC20绑定", "USDT-ERC20绑定", "返回上页"}
        
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
        
        # 處理「提款密码」按鈕
        if message_text == "提款密码":
            # 開始設置提款密碼
            set_user_withdrawal_password_state(user_id, "inputting")
            set_user_withdrawal_password_input(user_id, "")
            set_user_withdrawal_password_confirm(user_id, "")
            
            # 發送設置密碼消息和數字鍵盤（Inline 按鈕）
            sent_message = await update.message.reply_text(
                get_withdrawal_password_setup_message(0),
                reply_markup=get_password_input_keyboard()
            )
            set_user_withdrawal_password_message_id(user_id, sent_message.message_id)
            logger.info(f"用戶 {user_id} 開始設置提款密碼")
            return
        
        # 處理「USDT-TRC20绑定」按鈕
        if message_text == "USDT-TRC20绑定":
            # 檢查是否已設置提款密碼
            if not get_user_bank_card_password(user_id):
                await update.message.reply_text(get_bank_card_required_message())
                logger.info(f"用戶 {user_id} 點擊 USDT-TRC20 綁定按鈕，但未設置提款密碼")
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
            # 檢查是否已設置提款密碼
            if not get_user_bank_card_password(user_id):
                await update.message.reply_text(get_bank_card_required_message())
                logger.info(f"用戶 {user_id} 點擊 USDT-ERC20 綁定按鈕，但未設置提款密碼")
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
        personal_report_buttons = {"日统计", "月统计", "返回上页"}
        
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
        
        # 處理「月统计」
        if message_text == "月统计":
            await show_monthly_report(update, context)
            return
    
    # ==========================================
    # 處理日統計報表狀態下的按鈕
    # ==========================================
    elif current_state == "daily_report":
        # 允許在日統計狀態下切換到周統計或返回上頁
        personal_report_buttons = {"日统计", "月统计", "返回上页"}
        
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
        
        # 處理「月统计」
        if message_text == "月统计":
            await show_monthly_report(update, context)
            return
        
        # 處理「日统计」（重新顯示日統計）
        if message_text == "日统计":
            await show_daily_report(update, context)
            return
    
    # ==========================================
    # 處理周統計報表狀態下的按鈕
    # ==========================================
    elif current_state == "monthly_report":
        # 允許在月統計狀態下切換到日統計或返回上頁
        personal_report_buttons = {"日统计", "月统计", "返回上页"}
        
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
                logger.info(f"用戶 {user_id} 從月統計返回個人中心")
            else:
                # 默認返回首頁
                await update.message.reply_text(
                    "💡 使用底部按钮快速操作",
                    reply_markup=get_home_keyboard()
                )
                set_user_state(user_id, "home")
                logger.info(f"用戶 {user_id} 從月統計返回首頁（默認）")
            return
        
        # 處理「日统计」
        if message_text == "日统计":
            await show_daily_report(update, context)
            return
        
        # 處理「月统计」（重新顯示月統計）
        if message_text == "月统计":
            await show_monthly_report(update, context)
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
            try:
                await update.message.reply_text(
                    get_auto_bet_amount_prompt(f"{usdt_balance:.2f}"),
                    reply_markup=get_auto_bet_amount_keyboard()
                )
            except (TimedOut, NetworkError) as e:
                logger.error(f"發送自動下注提示消息時發生網絡錯誤: {e}")
                # 即使發送失敗，也更新狀態，避免用戶卡在當前狀態
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
            
            # 發送確認訊息和 Inline 按鈕
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            from messages import get_bet_confirmation_message
            from state import set_user_bet_confirmation
            import time
            
            confirmation_button = InlineKeyboardButton(
                text="确认下注",
                callback_data=f"confirm_bet_{bet_amount}"
            )
            inline_keyboard = InlineKeyboardMarkup([[confirmation_button]])
            
            sent_message = await update.message.reply_text(
                get_bet_confirmation_message(bet_amount),
                reply_markup=inline_keyboard
            )
            
            # 保存確認狀態（包含時間戳和聊天ID）
            set_user_bet_confirmation(user_id, bet_amount, sent_message.message_id, sent_message.chat.id, time.time())
            
            # 啟動30秒超時任務
            from handlers.betting import handle_bet_confirmation_timeout
            asyncio.create_task(
                handle_bet_confirmation_timeout(context, user_id, sent_message.chat.id, sent_message.message_id, bet_amount)
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
        count_buttons = {"10次", "20次", "30次", "50次", "100次", "150次", "200次", "300次", "500次", "1000次", "下注到点击停止", "返回上页"}
        
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
        if message_text == "下注到点击停止":
            # 持續下注模式（點擊停止才停止）- 先發送確認消息
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            from messages import get_auto_bet_stop_confirmation_message
            from state import set_user_auto_bet_confirmation
            import time
            
            confirmation_button = InlineKeyboardButton(
                text="确认下注",
                callback_data=f"confirm_auto_bet_stop_{bet_amount}"
            )
            inline_keyboard = InlineKeyboardMarkup([[confirmation_button]])
            
            try:
                sent_message = await update.message.reply_text(
                    get_auto_bet_stop_confirmation_message(bet_amount),
                    reply_markup=inline_keyboard
                )
            except (TimedOut, NetworkError) as e:
                logger.error(f"發送持續自動下注確認消息時發生網絡錯誤: {e}")
                return
            
            # 保存確認狀態（使用特殊的count值-1表示持續下注）
            set_user_auto_bet_confirmation(user_id, bet_amount, -1, sent_message.message_id, sent_message.chat.id, time.time())
            
            # 啟動30秒超時任務
            from handlers.betting import handle_auto_bet_confirmation_timeout
            asyncio.create_task(
                handle_auto_bet_confirmation_timeout(context, user_id, sent_message.chat.id, sent_message.message_id, bet_amount, -1)
            )
            
            logger.info(f"用戶 {user_id} 選擇下注到點擊停止，金額: {bet_amount}元，等待確認")
            return
        
        elif message_text in {"10次", "20次", "30次", "50次", "100次", "150次", "200次", "300次", "500次", "1000次"}:
            # 固定次數下注模式 - 先發送確認消息
            count = int(message_text.replace("次", ""))
            bet_amount_float = float(bet_amount)
            total_amount = bet_amount_float * count
            
            # 發送確認訊息和 Inline 按鈕
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            from messages import get_auto_bet_confirmation_message
            from state import set_user_auto_bet_confirmation
            import time
            
            confirmation_button = InlineKeyboardButton(
                text="确认下注",
                callback_data=f"confirm_auto_bet_{bet_amount}_{count}"
            )
            inline_keyboard = InlineKeyboardMarkup([[confirmation_button]])
            
            try:
                sent_message = await update.message.reply_text(
                    get_auto_bet_confirmation_message(bet_amount, count, f"{total_amount:.2f}"),
                    reply_markup=inline_keyboard
                )
            except (TimedOut, NetworkError) as e:
                logger.error(f"發送自動下注確認消息時發生網絡錯誤: {e}")
                return
            
            # 保存確認狀態（包含時間戳和聊天ID）
            set_user_auto_bet_confirmation(user_id, bet_amount, count, sent_message.message_id, sent_message.chat.id, time.time())
            
            # 啟動30秒超時任務
            from handlers.betting import handle_auto_bet_confirmation_timeout
            asyncio.create_task(
                handle_auto_bet_confirmation_timeout(context, user_id, sent_message.chat.id, sent_message.message_id, bet_amount, count)
            )
            
            logger.info(f"用戶 {user_id} 選擇自動下注 {count} 次，金額: {bet_amount}元，等待確認")
            return
    
    # ==========================================
    # 處理停止下注狀態下的按鈕
    # ==========================================
    elif current_state == "auto_bet_stopping":
        if message_text == "停止下注":
            # 停止自動下注（無論是持續下注還是固定次數下注）
            set_user_auto_bet_continuous(user_id, False)
            
            # 返回到哈希轉盤投注菜單
            try:
                await update.message.reply_text(
                    "已停止自动下注",
                    reply_markup=get_hash_wheel_betting_keyboard()
                )
            except (TimedOut, NetworkError) as e:
                logger.error(f"發送停止下注消息時發生網絡錯誤: {e}")
            
            # 設置狀態和來源標記
            set_user_state(user_id, "beginner_room_betting")
            set_user_betting_source(user_id, "hash_wheel")
            set_user_auto_bet_amount(user_id, None)
            set_user_auto_bet_count(user_id, None)
            logger.info(f"用戶 {user_id} 停止自動下注，返回到哈希轉盤投注菜單")
            return
    
    # 如果狀態未知，重置為首頁
    else:
        reset_user_state(user_id)
        await update.message.reply_text(
            "💡 使用底部按钮快速操作",
            reply_markup=get_home_keyboard()
        )

