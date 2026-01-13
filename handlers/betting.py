"""
投注處理模組
處理所有投注相關功能
"""

import asyncio
import logging
import random
from telegram.ext import ContextTypes
from telegram.error import TimedOut, NetworkError

from messages import (
    get_bet_success_message,
    get_waiting_hash_message,
    get_hash_result_message,
    get_bet_timeout_message,
    get_auto_bet_timeout_message,
    get_auto_bet_start_message,
    get_auto_bet_stop_bet_message,
    get_win_caption_message
)
from state import (
    get_user_usdt_balance,
    deduct_user_balance,
    add_user_balance,
    get_user_bet_confirmation,
    clear_user_bet_confirmation,
    get_user_auto_bet_confirmation,
    clear_user_auto_bet_confirmation,
    set_user_auto_bet_count,
    get_user_auto_bet_continuous,
    set_user_auto_bet_continuous,
    get_user_state,
    set_user_state,
    get_user_betting_source,
    set_user_betting_source,
    set_user_auto_bet_amount,
    get_user_auto_bet_count,
    get_user_account
)
from handlers.constants import TEST_HASH_VALUE, TEST_HASH_URL
from keyboards import (
    get_hash_wheel_betting_keyboard,
    get_beginner_room_betting_keyboard
)
from telegram.error import TimedOut, NetworkError

logger = logging.getLogger(__name__)


async def execute_single_bet(context: ContextTypes.DEFAULT_TYPE, chat_id: int, user_id: int, bet_amount: str) -> bool:
    """
    執行單次下注的輔助函數
    :param context: Context 對象
    :param chat_id: 聊天ID
    :param user_id: 用戶ID
    :param bet_amount: 下注金額（字符串，如 "2", "5", "10"）
    :return: 是否成功執行（False表示失敗，應該停止自動下注）
    """
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
        from datetime import datetime
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
                    game_name = "哈希转盘"
                else:
                    game_name = "哈希转盘"  # 默认值
                
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
                    game_result = f"尾数 {last_digit}"
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


async def handle_bet_confirmation_timeout(
    context: ContextTypes.DEFAULT_TYPE,
    user_id: int,
    chat_id: int,
    message_id: int,
    bet_amount: str
) -> None:
    """
    處理投注確認超時（30秒後）
    會檢查所有舊的確認消息並讓它們也超時
    :param context: Context 對象
    :param user_id: 用戶ID
    :param chat_id: 聊天ID
    :param message_id: 確認消息的ID
    :param bet_amount: 投注金額
    """
    await asyncio.sleep(30)  # 等待30秒
    
    # 獲取所有確認狀態
    confirmations = get_user_bet_confirmation(user_id)
    import time
    current_time = time.time()
    
    # 檢查所有確認消息，讓所有超時的消息都失效
    from telegram import InlineKeyboardMarkup
    for conf in confirmations[:]:  # 使用切片複製列表，避免迭代時修改
        conf_timestamp = conf.get("timestamp", 0)
        conf_message_id = conf.get("message_id")
        conf_chat_id = conf.get("chat_id")
        conf_amount = conf.get("amount")
        
        # 如果超過30秒，讓它超時
        if current_time - conf_timestamp > 30:
            # 清除這個確認狀態
            clear_user_bet_confirmation(user_id, conf_message_id)
            
            # 編輯消息，移除按鈕並顯示超時訊息
            try:
                await context.bot.edit_message_text(
                    chat_id=conf_chat_id,
                    message_id=conf_message_id,
                    text=get_bet_timeout_message(),
                    reply_markup=InlineKeyboardMarkup([])  # 移除按鈕
                )
                logger.info(f"用戶 {user_id} 投注確認超時，金額: {conf_amount}元，消息ID: {conf_message_id}")
            except Exception as e:
                logger.error(f"編輯超時消息時發生錯誤: {e}")


async def handle_auto_bet_confirmation_timeout(
    context: ContextTypes.DEFAULT_TYPE,
    user_id: int,
    chat_id: int,
    message_id: int,
    bet_amount: str,
    bet_count: int
) -> None:
    """
    處理自動下注確認超時（30秒後）
    會檢查所有舊的確認消息並讓它們也超時
    :param context: Context 對象
    :param user_id: 用戶ID
    :param chat_id: 聊天ID
    :param message_id: 確認消息的ID
    :param bet_amount: 每次下注金額
    :param bet_count: 下注次數
    """
    await asyncio.sleep(30)  # 等待30秒
    
    # 獲取所有確認狀態
    confirmations = get_user_auto_bet_confirmation(user_id)
    import time
    current_time = time.time()
    
    # 檢查所有確認消息，讓所有超時的消息都失效
    from telegram import InlineKeyboardMarkup
    for conf in confirmations[:]:  # 使用切片複製列表，避免迭代時修改
        conf_timestamp = conf.get("timestamp", 0)
        conf_message_id = conf.get("message_id")
        conf_chat_id = conf.get("chat_id")
        conf_amount = conf.get("amount")
        conf_count = conf.get("count")
        
        # 如果超過30秒，讓它超時
        if current_time - conf_timestamp > 30:
            # 清除這個確認狀態
            clear_user_auto_bet_confirmation(user_id, conf_message_id)
            
            # 編輯消息，移除按鈕並顯示超時訊息
            try:
                await context.bot.edit_message_text(
                    chat_id=conf_chat_id,
                    message_id=conf_message_id,
                    text=get_auto_bet_timeout_message(),
                    reply_markup=InlineKeyboardMarkup([])  # 移除按鈕
                )
                logger.info(f"用戶 {user_id} 自動下注確認超時，金額: {conf_amount}元，次數: {conf_count}次，消息ID: {conf_message_id}")
            except Exception as e:
                logger.error(f"編輯自動下注超時消息時發生錯誤: {e}")


async def start_fixed_count_auto_bet(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    user_id: int,
    bet_amount: str,
    count: int
) -> None:
    """
    啟動固定次數自動下注循環
    :param context: Context 對象
    :param chat_id: 聊天ID
    :param user_id: 用戶ID
    :param bet_amount: 每次下注金額（字符串）
    :param count: 下注次數
    """
    saved_count = count
    saved_bet_amount = bet_amount
    saved_bet_amount_float = float(saved_bet_amount)
    completed_count = 0
    
    # 設置自動下注狀態
    set_user_auto_bet_count(user_id, count)
    set_user_auto_bet_continuous(user_id, False)
    
    # 設置狀態為停止下注模式（確保底部菜單顯示停止下注按鈕）
    set_user_state(user_id, "auto_bet_stopping")
    
    logger.info(f"用戶 {user_id} 開始自動下注 {saved_count} 次，金額: {saved_bet_amount}元")
    
    try:
        # 執行固定次數下注，但允許用戶隨時停止
        for i in range(saved_count):
            # 檢查是否應該停止（用戶點擊了停止下注）
            # 檢查 auto_bet_count 是否為 None（停止下注時會被清除）
            current_count = get_user_auto_bet_count(user_id)
            if current_count is None:
                # 用戶已點擊停止下注，清除狀態並退出循環
                logger.info(f"用戶 {user_id} 在自動下注過程中點擊停止，已完成 {i}/{saved_count} 次")
                try:
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=f"已停止自动下注，已完成 {i}/{saved_count} 次"
                    )
                except (TimedOut, NetworkError) as e:
                    logger.error(f"發送停止消息時發生網絡錯誤: {e}")
                break
            
            # 檢查狀態是否已改變（用戶可能點擊了停止下注）
            current_state = get_user_state(user_id)
            if current_state != "auto_bet_stopping":
                # 狀態已改變，說明用戶可能點擊了停止下注
                logger.info(f"用戶 {user_id} 在自動下注過程中狀態改變，已完成 {i}/{saved_count} 次")
                try:
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=f"已停止自动下注，已完成 {i}/{saved_count} 次"
                    )
                except (TimedOut, NetworkError) as e:
                    logger.error(f"發送停止消息時發生網絡錯誤: {e}")
                break
            
            current_bet_count = i + 1  # 從1開始
            
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
            
            # 再次檢查是否應該停止（在執行下注前檢查）
            current_count = get_user_auto_bet_count(user_id)
            current_state = get_user_state(user_id)
            if current_count is None or current_state != "auto_bet_stopping":
                # 用戶已點擊停止下注，停止當前下注
                logger.info(f"用戶 {user_id} 在自動下注執行前點擊停止，已完成 {i}/{saved_count} 次")
                try:
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=f"已停止自动下注，已完成 {i}/{saved_count} 次"
                    )
                except (TimedOut, NetworkError) as e:
                    logger.error(f"發送停止消息時發生網絡錯誤: {e}")
                break
            
            # 執行單次下注（自動下注模式）
            try:
                # 轉換投注金額為浮點數
                bet_amount_float = float(saved_bet_amount)
                
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
                    break
                
                # 扣除餘額
                deduct_user_balance(user_id, bet_amount_float)
                new_balance = get_user_usdt_balance(user_id)
                logger.info(f"用戶 {user_id} 扣除投注金額: {bet_amount_float:.2f} USDT，剩餘餘額: {new_balance:.2f} USDT")
                
                # 發送第一則報文：投注成功（帶金額和餘額）
                from keyboards import get_stop_betting_keyboard
                try:
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=get_bet_success_message(f"{bet_amount_float:.2f}", f"{new_balance:.2f}"),
                        reply_markup=get_stop_betting_keyboard()
                    )
                except (TimedOut, NetworkError) as e:
                    logger.error(f"發送投注成功消息時發生網絡錯誤: {e}，但繼續執行下注流程")
                
                # 立即發送計次消息（投注成功後立即顯示）
                try:
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=get_auto_bet_start_message(current_bet_count, saved_count, saved_bet_amount),
                        reply_markup=get_stop_betting_keyboard()
                    )
                except (TimedOut, NetworkError) as e:
                    logger.error(f"發送自動下注計次消息時發生網絡錯誤: {e}")
                
                # 發送第二則報文：請稍等哈希結果
                try:
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=get_waiting_hash_message(),
                        reply_markup=get_stop_betting_keyboard()
                    )
                except (TimedOut, NetworkError) as e:
                    logger.error(f"發送等待哈希結果消息時發生網絡錯誤: {e}，但繼續執行下注流程")
                
                logger.info(f"用戶 {user_id} 執行自動下注第 {current_bet_count} 次，金額: {bet_amount_float:.2f} USDT")
                
                # 等待3秒（已扣除餘額，必須完成當次開獎）
                # 注意：即使等待期間用戶點擊停止，也要完成當次下注的開獎
                await asyncio.sleep(3)
                
                # 中獎判定：50%機率中獎
                is_winner = random.random() < 0.5
                
                # 記錄投注時間
                from datetime import datetime
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
                            game_name = "哈希转盘"
                        else:
                            game_name = "哈希转盘"  # 默认值
                        
                        # 獲取交易哈希（清理格式）
                        transaction_hash = TEST_HASH_VALUE.replace("**", "")
                        
                        # 獲取投注玩家名稱
                        player_name = get_user_account(user_id) or f"用戶{user_id}"
                        
                        # 計算遊戲結果（從哈希值提取最後一位數字）
                        import re
                        hash_numbers = re.findall(r'\d+', TEST_HASH_VALUE)
                        if hash_numbers:
                            last_digit = hash_numbers[-1][-1] if hash_numbers[-1] else "0"
                            game_result = f"尾数 {last_digit}"
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
                        from keyboards import get_stop_betting_keyboard
                        try:
                            with open(image_path, 'rb') as photo_file:
                                await context.bot.send_photo(
                                    chat_id=chat_id,
                                    photo=photo_file,
                                    caption=caption,
                                    parse_mode="HTML",
                                    reply_markup=get_stop_betting_keyboard()
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
                                parse_mode="HTML",
                                reply_markup=get_stop_betting_keyboard()
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
                                parse_mode="HTML",
                                reply_markup=get_stop_betting_keyboard()
                            )
                    except Exception as e:
                        logger.error(f"生成中獎圖片時發生錯誤: {e}", exc_info=True)
                        # 如果圖片生成失敗，降級為只發送文字訊息
                        from keyboards import get_stop_betting_keyboard
                        try:
                            await context.bot.send_message(
                                chat_id=chat_id,
                                text=get_hash_result_message(
                                    f"{bonus_amount:.2f}",
                                    TEST_HASH_VALUE,
                                    TEST_HASH_URL,
                                    f"{final_balance:.2f}"
                                ),
                                parse_mode="HTML",
                                reply_markup=get_stop_betting_keyboard()
                            )
                        except (TimedOut, NetworkError) as send_error:
                            logger.error(f"發送中獎結果消息時發生網絡錯誤: {send_error}")
                else:
                    # 未中獎
                    logger.info(f"用戶 {user_id} 未中獎，當前餘額: {new_balance:.2f} USDT")
                    
                    # 發送第三則報文：哈希結果（未中獎）
                    from keyboards import get_stop_betting_keyboard
                    try:
                        await context.bot.send_message(
                            chat_id=chat_id,
                            text=get_hash_result_message("0.00", TEST_HASH_VALUE, TEST_HASH_URL),
                            parse_mode="HTML",
                            reply_markup=get_stop_betting_keyboard()
                        )
                    except (TimedOut, NetworkError) as e:
                        logger.error(f"發送未中獎結果消息時發生網絡錯誤: {e}")
                
                completed_count = current_bet_count
                
                # 當次下注完成後，檢查是否應該停止（用於中斷後續下注）
                current_count = get_user_auto_bet_count(user_id)
                current_state = get_user_state(user_id)
                if current_count is None or current_state != "auto_bet_stopping":
                    # 用戶已點擊停止下注，當次下注已完成，停止後續下注
                    logger.info(f"用戶 {user_id} 在當次下注完成後點擊停止，已完成 {current_bet_count}/{saved_count} 次")
                    try:
                        await context.bot.send_message(
                            chat_id=chat_id,
                            text=f"已停止自动下注，已完成 {current_bet_count}/{saved_count} 次"
                        )
                    except (TimedOut, NetworkError) as e:
                        logger.error(f"發送停止消息時發生網絡錯誤: {e}")
                    break
                
            except Exception as e:
                logger.error(f"執行自動下注第 {current_bet_count} 次時發生錯誤: {e}", exc_info=True)
                logger.warning(f"用戶 {user_id} 自動下注第 {current_bet_count} 次執行失敗，停止下注")
                break
        
        # 完成後發送完成消息並清理狀態
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"自动下注 {saved_count} 次已完成（实际完成 {completed_count} 次）"
            )
        except (TimedOut, NetworkError) as e:
            logger.error(f"發送完成消息時發生網絡錯誤: {e}")
        
        # 清理自動下注相關狀態並返回到哈希轉盤投注菜單
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text="请选择",
                reply_markup=get_hash_wheel_betting_keyboard()
            )
            # 設置狀態和來源標記
            set_user_state(user_id, "beginner_room_betting")
            set_user_betting_source(user_id, "hash_wheel")
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


async def execute_continuous_bet(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    user_id: int,
    bet_amount: str,
    bet_count: int
) -> bool:
    """
    執行持續下注的單次投注（使用持續下注專用的消息格式）
    :param context: Context 對象
    :param chat_id: 聊天ID
    :param user_id: 用戶ID
    :param bet_amount: 下注金額（字符串，如 "2", "5", "10"）
    :param bet_count: 投注次數（從1開始）
    :return: 是否成功執行（False表示失敗，應該停止自動下注）
    """
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
        
        # 發送第一則報文：投注成功（使用持續下注專用格式）
        from keyboards import get_stop_betting_keyboard
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=get_auto_bet_stop_bet_message(
                    bet_count,
                    bet_amount,
                    f"{new_balance:.2f}"
                ),
                reply_markup=get_stop_betting_keyboard()
            )
        except (TimedOut, NetworkError) as e:
            logger.error(f"發送投注成功消息時發生網絡錯誤: {e}，但繼續執行下注流程")
        
        # 發送第二則報文：請稍等哈希結果
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=get_waiting_hash_message(),
                reply_markup=get_stop_betting_keyboard()
            )
        except (TimedOut, NetworkError) as e:
            logger.error(f"發送等待哈希結果消息時發生網絡錯誤: {e}，但繼續執行下注流程")
        
        logger.info(f"用戶 {user_id} 執行持續下注第 {bet_count} 次，金額: {bet_amount_float:.2f} USDT")
        
        # 等待3秒
        await asyncio.sleep(3)
        
        # 中獎判定：50%機率中獎
        is_winner = random.random() < 0.5
        
        # 記錄投注時間
        from datetime import datetime
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
                    game_name = "哈希转盘"
                else:
                    game_name = "哈希转盘"  # 默认值
                
                # 獲取交易哈希（清理格式）
                transaction_hash = TEST_HASH_VALUE.replace("**", "")
                
                # 獲取投注玩家名稱
                player_name = get_user_account(user_id) or f"用戶{user_id}"
                
                # 計算遊戲結果（從哈希值提取最後一位數字）
                import re
                hash_numbers = re.findall(r'\d+', TEST_HASH_VALUE)
                if hash_numbers:
                    last_digit = hash_numbers[-1][-1] if hash_numbers[-1] else "0"
                    game_result = f"尾数 {last_digit}"
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
                            parse_mode="HTML",
                            reply_markup=get_stop_betting_keyboard()
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
                        parse_mode="HTML",
                        reply_markup=get_stop_betting_keyboard()
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
                        parse_mode="HTML",
                        reply_markup=get_stop_betting_keyboard()
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
                        parse_mode="HTML",
                        reply_markup=get_stop_betting_keyboard()
                    )
                except (TimedOut, NetworkError) as send_error:
                    logger.error(f"發送中獎結果消息時發生網絡錯誤: {send_error}")
                # 即使發送失敗，下注流程也算完成
        else:
            # 未中獎
            logger.info(f"用戶 {user_id} 未中獎，當前餘額: {new_balance:.2f} USDT")
            
            # 發送第三則報文：哈希結果（未中獎）
            try:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=get_hash_result_message("0.00", TEST_HASH_VALUE, TEST_HASH_URL),
                    parse_mode="HTML",
                    reply_markup=get_stop_betting_keyboard()
                )
            except (TimedOut, NetworkError) as e:
                logger.error(f"發送未中獎結果消息時發生網絡錯誤: {e}")
                # 即使發送失敗，下注流程也算完成
        
        return True
        
    except Exception as e:
        logger.error(f"執行持續下注時發生未知錯誤: {e}", exc_info=True)
        # 發生未知錯誤時，返回False表示失敗，應該停止自動下注
        return False


async def start_continuous_auto_bet(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    user_id: int,
    bet_amount: str
) -> None:
    """
    啟動持續自動下注循環（下注到點擊停止）
    :param context: Context 對象
    :param chat_id: 聊天ID
    :param user_id: 用戶ID
    :param bet_amount: 每次下注金額（字符串）
    """
    saved_bet_amount = bet_amount
    saved_bet_amount_float = float(saved_bet_amount)
    bet_count = 0  # 從0開始計數，但顯示時從1開始
    
    # 設置自動下注狀態
    set_user_auto_bet_count(user_id, None)  # None 表示持續下注
    set_user_auto_bet_continuous(user_id, True)
    
    # 設置狀態為停止下注模式
    set_user_state(user_id, "auto_bet_stopping")
    
    # 發送開始消息
    from keyboards import get_stop_betting_keyboard
    try:
        await context.bot.send_message(
            chat_id=chat_id,
            text="已开始持续自动下注，点击「停止下注」可停止下注",
            reply_markup=get_stop_betting_keyboard()
        )
    except (TimedOut, NetworkError) as e:
        logger.error(f"發送持續自動下注開始消息時發生網絡錯誤: {e}，但繼續執行下注流程")
    
    logger.info(f"用戶 {user_id} 開始持續自動下注，金額: {saved_bet_amount}元")
    
    try:
        while get_user_auto_bet_continuous(user_id):
            bet_count += 1  # 從1開始顯示
            
            # 檢查餘額是否足夠
            current_balance = get_user_usdt_balance(user_id)
            if current_balance < saved_bet_amount_float:
                try:
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=f"余额不足，自动下注已停止。当前余额：{current_balance:.2f} USDT"
                    )
                except (TimedOut, NetworkError) as e:
                    logger.error(f"發送餘額不足消息時發生網絡錯誤: {e}")
                break
            
            # 執行持續下注的單次投注（使用專用的消息格式）
            success = await execute_continuous_bet(context, chat_id, user_id, saved_bet_amount, bet_count)
            if not success:
                logger.warning(f"用戶 {user_id} 持續自動下注第 {bet_count} 次執行失敗，停止下注")
                break
        
        # 停止後清理狀態並返回到哈希轉盤投注菜單
        set_user_auto_bet_continuous(user_id, False)
        set_user_auto_bet_amount(user_id, None)
        set_user_auto_bet_count(user_id, None)
        
        # 返回到哈希轉盤投注菜單
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text="请选择",
                reply_markup=get_hash_wheel_betting_keyboard()
            )
            # 設置狀態和來源標記
            set_user_state(user_id, "beginner_room_betting")
            set_user_betting_source(user_id, "hash_wheel")
        except (TimedOut, NetworkError) as e:
            logger.error(f"發送返回菜單消息時發生網絡錯誤: {e}")
        
        logger.info(f"用戶 {user_id} 持續自動下注已停止，共完成 {bet_count} 次")
        
    except Exception as e:
        logger.error(f"持續自動下注循環發生錯誤: {e}", exc_info=True)
        set_user_auto_bet_continuous(user_id, False)
        set_user_auto_bet_amount(user_id, None)
        set_user_auto_bet_count(user_id, None)
        
        # 發生錯誤時也返回到哈希轉盤投注菜單
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text="请选择",
                reply_markup=get_hash_wheel_betting_keyboard()
            )
            set_user_state(user_id, "beginner_room_betting")
            set_user_betting_source(user_id, "hash_wheel")
        except (TimedOut, NetworkError) as send_error:
            logger.error(f"發送返回菜單消息時發生網絡錯誤: {send_error}")
