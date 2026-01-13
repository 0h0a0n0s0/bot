"""
回調處理模組
處理所有 Inline 按鈕點擊事件
"""

import asyncio
import logging
from telegram import Update
from telegram.ext import ContextTypes

from messages import get_withdraw_amount_prompt
from state import (
    get_user_bank_card_binding_state,
    set_user_bank_card_binding_state,
    get_user_wallet_binding_state,
    set_user_wallet_binding_state,
    get_user_deposit_withdraw_state,
    set_user_deposit_withdraw_state,
    get_user_withdraw_state,
    set_user_withdraw_state,
    set_user_withdraw_method,
    set_user_withdraw_amount,
    get_user_usdt_balance,
    get_user_withdrawal_password_state,
    set_user_withdrawal_password_state,
    get_user_withdrawal_password_input,
    set_user_withdrawal_password_input,
    get_user_withdrawal_password_confirm,
    set_user_withdrawal_password_confirm,
    get_user_withdrawal_password_message_id,
    set_user_withdrawal_password_message_id,
    get_user_bank_card_password,
    set_user_bank_card_password
)
from handlers.reports import handle_daily_report_buttons, handle_monthly_report_buttons
from handlers.betting import execute_single_bet, start_fixed_count_auto_bet, start_continuous_auto_bet
from handlers.constants import MESSAGE_FEATURE_DEVELOPING
from state import (
    get_user_bet_confirmation,
    get_user_bet_confirmation_by_message_id,
    clear_user_bet_confirmation,
    get_user_auto_bet_confirmation,
    get_user_auto_bet_confirmation_by_message_id,
    clear_user_auto_bet_confirmation
)
from messages import (
    get_withdrawal_password_setup_message,
    get_withdrawal_password_confirm_message,
    get_withdrawal_password_success_message,
    get_withdrawal_password_mismatch_message
)
from keyboards import get_password_input_keyboard, get_security_center_keyboard
from telegram import InlineKeyboardMarkup

logger = logging.getLogger(__name__)


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
    
    # 處理月統計報表的按鈕
    if callback_data.startswith("monthly_report_"):
        await handle_monthly_report_buttons(update, context, callback_data)
        return
    
    # 處理提款密碼輸入按鈕（優先處理，因為 pwd_ 可能與其他回調衝突）
    if callback_data.startswith("pwd_"):
        await handle_withdrawal_password_input(update, context, callback_data)
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
    
    # 處理確認下注按鈕
    if callback_data.startswith("confirm_bet_"):
        bet_amount = callback_data.replace("confirm_bet_", "")
        message_id = query.message.message_id
        
        # 根據消息ID獲取確認狀態
        confirmation = get_user_bet_confirmation_by_message_id(user_id, message_id)
        
        if not confirmation:
            # 確認狀態不存在，說明已超時或被清除
            from messages import get_bet_timeout_message
            # 防錯誤機制：更新消息為超時訊息
            try:
                await query.message.edit_text(
                    text=get_bet_timeout_message(),
                    reply_markup=InlineKeyboardMarkup([])
                )
            except Exception as e:
                logger.warning(f"更新超時消息時發生錯誤（可忽略）: {e}")
            await query.answer(get_bet_timeout_message(), show_alert=True)
            logger.info(f"用戶 {user_id} 嘗試確認已超時的投注，金額: {bet_amount}元")
            return
        
        # 檢查金額是否匹配
        if confirmation.get("amount") != bet_amount:
            from messages import get_bet_timeout_message
            await query.answer(get_bet_timeout_message(), show_alert=True)
            logger.info(f"用戶 {user_id} 嘗試確認金額不匹配的投注")
            return
        
        # 檢查是否超時（30秒）
        import time
        elapsed_time = time.time() - confirmation.get("timestamp", 0)
        if elapsed_time > 30:
            # 已超時，防錯誤機制：更新消息為超時訊息
            from messages import get_bet_timeout_message
            clear_user_bet_confirmation(user_id, message_id)
            try:
                await query.message.edit_text(
                    text=get_bet_timeout_message(),
                    reply_markup=InlineKeyboardMarkup([])
                )
            except Exception as e:
                logger.warning(f"更新超時消息時發生錯誤（可忽略）: {e}")
            await query.answer(get_bet_timeout_message(), show_alert=True)
            logger.info(f"用戶 {user_id} 確認投注時已超時，金額: {bet_amount}元")
            return
        
        # 確認有效，清除確認狀態
        clear_user_bet_confirmation(user_id, message_id)
        
        # 編輯消息，移除按鈕
        try:
            await query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup([]))
        except Exception as e:
            logger.warning(f"編輯確認消息時發生錯誤（可忽略）: {e}")
        
        # 執行投注
        await query.answer("正在處理投注...")
        logger.info(f"用戶 {user_id} 確認下注，金額: {bet_amount}元")
        asyncio.create_task(
            execute_single_bet(context, query.message.chat.id, user_id, bet_amount)
        )
        return
    
    # 處理確認下注到點擊停止按鈕（必須在 confirm_auto_bet_ 之前檢查，因為它是子字符串）
    if callback_data.startswith("confirm_auto_bet_stop_"):
        bet_amount = callback_data.replace("confirm_auto_bet_stop_", "")
        message_id = query.message.message_id
        
        # 根據消息ID獲取確認狀態（count為-1表示持續下注）
        confirmation = get_user_auto_bet_confirmation_by_message_id(user_id, message_id)
        
        if not confirmation:
            # 確認狀態不存在，說明已超時或被清除
            from messages import get_auto_bet_timeout_message
            # 防錯誤機制：更新消息為超時訊息
            try:
                await query.message.edit_text(
                    text=get_auto_bet_timeout_message(),
                    reply_markup=InlineKeyboardMarkup([])
                )
            except Exception as e:
                logger.warning(f"更新超時消息時發生錯誤（可忽略）: {e}")
            await query.answer(get_auto_bet_timeout_message(), show_alert=True)
            logger.info(f"用戶 {user_id} 嘗試確認已超時的下注到點擊停止，金額: {bet_amount}元")
            return
        
        # 檢查參數是否匹配（count應該為-1）
        if confirmation.get("amount") != bet_amount or confirmation.get("count") != -1:
            from messages import get_auto_bet_timeout_message
            await query.answer(get_auto_bet_timeout_message(), show_alert=True)
            logger.info(f"用戶 {user_id} 嘗試確認參數不匹配的下注到點擊停止")
            return
        
        # 檢查是否超時（30秒）
        import time
        elapsed_time = time.time() - confirmation.get("timestamp", 0)
        if elapsed_time > 30:
            # 已超時，防錯誤機制：更新消息為超時訊息
            from messages import get_auto_bet_timeout_message
            clear_user_auto_bet_confirmation(user_id, message_id)
            try:
                await query.message.edit_text(
                    text=get_auto_bet_timeout_message(),
                    reply_markup=InlineKeyboardMarkup([])
                )
            except Exception as e:
                logger.warning(f"更新超時消息時發生錯誤（可忽略）: {e}")
            await query.answer(get_auto_bet_timeout_message(), show_alert=True)
            logger.info(f"用戶 {user_id} 確認下注到點擊停止時已超時，金額: {bet_amount}元")
            return
        
        # 確認有效，清除確認狀態
        clear_user_auto_bet_confirmation(user_id, message_id)
        
        # 編輯消息，移除按鈕
        try:
            await query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup([]))
        except Exception as e:
            logger.warning(f"編輯確認消息時發生錯誤（可忽略）: {e}")
        
        # 執行持續自動下注
        await query.answer("正在開始自動下注...")
        logger.info(f"用戶 {user_id} 確認下注到點擊停止，金額: {bet_amount}元")
        asyncio.create_task(
            start_continuous_auto_bet(context, query.message.chat.id, user_id, bet_amount)
        )
        return
    
    # 處理確認自動下注按鈕（固定次數）
    if callback_data.startswith("confirm_auto_bet_"):
        # callback_data 格式: "confirm_auto_bet_{amount}_{count}"
        parts = callback_data.replace("confirm_auto_bet_", "").split("_")
        if len(parts) != 2:
            logger.warning(f"無效的自動下注確認回調數據: {callback_data}")
            return
        
        bet_amount = parts[0]
        bet_count = int(parts[1])
        message_id = query.message.message_id
        
        # 根據消息ID獲取確認狀態
        confirmation = get_user_auto_bet_confirmation_by_message_id(user_id, message_id)
        
        if not confirmation:
            # 確認狀態不存在，說明已超時或被清除
            from messages import get_auto_bet_timeout_message
            # 防錯誤機制：更新消息為超時訊息
            try:
                await query.message.edit_text(
                    text=get_auto_bet_timeout_message(),
                    reply_markup=InlineKeyboardMarkup([])
                )
            except Exception as e:
                logger.warning(f"更新超時消息時發生錯誤（可忽略）: {e}")
            await query.answer(get_auto_bet_timeout_message(), show_alert=True)
            logger.info(f"用戶 {user_id} 嘗試確認已超時的自動下注，金額: {bet_amount}元，次數: {bet_count}次")
            return
        
        # 檢查參數是否匹配
        if confirmation.get("amount") != bet_amount or confirmation.get("count") != bet_count:
            from messages import get_auto_bet_timeout_message
            await query.answer(get_auto_bet_timeout_message(), show_alert=True)
            logger.info(f"用戶 {user_id} 嘗試確認參數不匹配的自動下注，金額: {bet_amount}，次數: {bet_count}，確認狀態: {confirmation}")
            return
        
        # 檢查是否超時（30秒）
        import time
        elapsed_time = time.time() - confirmation.get("timestamp", 0)
        if elapsed_time > 30:
            # 已超時，防錯誤機制：更新消息為超時訊息
            from messages import get_auto_bet_timeout_message
            clear_user_auto_bet_confirmation(user_id, message_id)
            try:
                await query.message.edit_text(
                    text=get_auto_bet_timeout_message(),
                    reply_markup=InlineKeyboardMarkup([])
                )
            except Exception as e:
                logger.warning(f"更新超時消息時發生錯誤（可忽略）: {e}")
            await query.answer(get_auto_bet_timeout_message(), show_alert=True)
            logger.info(f"用戶 {user_id} 確認自動下注時已超時，金額: {bet_amount}元，次數: {bet_count}次")
            return
        
        # 確認有效，清除確認狀態
        clear_user_auto_bet_confirmation(user_id, message_id)
        
        # 編輯消息，移除按鈕
        try:
            await query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup([]))
        except Exception as e:
            logger.warning(f"編輯確認消息時發生錯誤（可忽略）: {e}")
        
        # 執行自動下注
        await query.answer("正在開始自動下注...")
        logger.info(f"用戶 {user_id} 確認自動下注，金額: {bet_amount}元，次數: {bet_count}次")
        
        # 設置狀態為停止下注模式，並發送停止下注鍵盤
        from state import set_user_state
        from keyboards import get_stop_betting_keyboard
        set_user_state(user_id, "auto_bet_stopping")
        
        try:
            await query.message.chat.send_message(
                "已开始自动下注，点击「停止下注」可停止下注",
                reply_markup=get_stop_betting_keyboard()
            )
        except Exception as e:
            logger.warning(f"發送停止下注鍵盤時發生錯誤（可忽略）: {e}")
        
        # 固定次數下注模式
        asyncio.create_task(
            start_fixed_count_auto_bet(context, query.message.chat.id, user_id, bet_amount, bet_count)
        )
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


async def handle_withdrawal_password_input(update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
    """
    處理提款密碼輸入的 Inline 按鈕點擊
    """
    query = update.callback_query
    user_id = update.effective_user.id
    
    # 回答回調查詢
    try:
        await query.answer()
    except Exception as e:
        logger.warning(f"回答回調查詢時發生錯誤（可忽略）: {e}")
    
    # 檢查用戶是否在設置提款密碼
    withdrawal_password_state = get_user_withdrawal_password_state(user_id)
    if withdrawal_password_state not in {"inputting", "confirming"}:
        logger.warning(f"用戶 {user_id} 點擊提款密碼按鈕但不在設置狀態")
        return
    
    # 處理「取消」按鈕
    if callback_data == "pwd_cancel":
        await query.message.edit_text(
            "已取消設置提款密碼",
            reply_markup=InlineKeyboardMarkup([])
        )
        set_user_withdrawal_password_state(user_id, None)
        logger.info(f"用戶 {user_id} 取消設置提款密碼")
        return
    
    # 處理「删除」按鈕
    if callback_data == "pwd_delete":
        current_password = ""
        if withdrawal_password_state == "inputting":
            current_password = get_user_withdrawal_password_input(user_id)
        else:  # confirming
            current_password = get_user_withdrawal_password_confirm(user_id)
        
        # 刪除最後一位
        if len(current_password) > 0:
            current_password = current_password[:-1]
            
            # 更新狀態
            if withdrawal_password_state == "inputting":
                set_user_withdrawal_password_input(user_id, current_password)
            else:  # confirming
                set_user_withdrawal_password_confirm(user_id, current_password)
            
            # 更新消息
            try:
                if withdrawal_password_state == "inputting":
                    new_message = get_withdrawal_password_setup_message(len(current_password))
                else:  # confirming
                    new_message = get_withdrawal_password_confirm_message(len(current_password))
                
                await query.message.edit_text(
                    text=new_message,
                    reply_markup=get_password_input_keyboard()
                )
            except Exception as e:
                logger.error(f"更新提款密碼消息時發生錯誤: {e}")
        return
    
    # 處理數字按鈕（pwd_0 到 pwd_9）
    if callback_data.startswith("pwd_") and len(callback_data) == 5:
        digit = callback_data[-1]  # 獲取最後一個字符（數字）
        
        if digit not in "0123456789":
            return
        
        # 獲取當前密碼
        current_password = ""
        if withdrawal_password_state == "inputting":
            current_password = get_user_withdrawal_password_input(user_id)
        else:  # confirming
            current_password = get_user_withdrawal_password_confirm(user_id)
        
        # 如果密碼長度未達4位，添加數字
        if len(current_password) < 4:
            current_password += digit
            
            # 更新狀態
            if withdrawal_password_state == "inputting":
                set_user_withdrawal_password_input(user_id, current_password)
            else:  # confirming
                set_user_withdrawal_password_confirm(user_id, current_password)
            
            # 更新消息
            try:
                if withdrawal_password_state == "inputting":
                    new_message = get_withdrawal_password_setup_message(len(current_password))
                else:  # confirming
                    new_message = get_withdrawal_password_confirm_message(len(current_password))
                
                await query.message.edit_text(
                    text=new_message,
                    reply_markup=get_password_input_keyboard()
                )
            except Exception as e:
                logger.error(f"更新提款密碼消息時發生錯誤: {e}")
            
            # 如果密碼長度達到4位，自動進入下一步
            if len(current_password) == 4:
                if withdrawal_password_state == "inputting":
                    # 切換到確認密碼階段
                    set_user_withdrawal_password_state(user_id, "confirming")
                    set_user_withdrawal_password_confirm(user_id, "")
                    
                    # 發送確認密碼消息
                    sent_message = await query.message.chat.send_message(
                        get_withdrawal_password_confirm_message(0),
                        reply_markup=get_password_input_keyboard()
                    )
                    set_user_withdrawal_password_message_id(user_id, sent_message.message_id)
                    logger.info(f"用戶 {user_id} 完成提款密碼輸入，進入確認階段")
                else:  # confirming
                    # 驗證兩次密碼是否一致
                    input_password = get_user_withdrawal_password_input(user_id)
                    confirm_password = get_user_withdrawal_password_confirm(user_id)
                    
                    if input_password == confirm_password:
                        # 密碼一致，保存提款密碼
                        set_user_bank_card_password(user_id, confirm_password)
                        await query.message.edit_text(
                            text=get_withdrawal_password_success_message(),
                            reply_markup=InlineKeyboardMarkup([])
                        )
                        set_user_withdrawal_password_state(user_id, None)
                        logger.info(f"用戶 {user_id} 提款密碼設置成功")
                    else:
                        # 密碼不一致，重新開始
                        await query.message.edit_text(
                            text=get_withdrawal_password_mismatch_message(),
                            reply_markup=InlineKeyboardMarkup([])
                        )
                        set_user_withdrawal_password_state(user_id, None)
                        logger.info(f"用戶 {user_id} 提款密碼確認不一致，設置失敗")
