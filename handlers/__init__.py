"""
處理器模組
存放所有 Telegram Bot 的處理函數
"""

# 導出所有處理函數
from handlers.commands import (
    start_command,
    show_start_game_info,
    handle_profile,
    handle_deposit,
    handle_withdraw,
    handle_customer_service
)
from handlers.callbacks import handle_inline_buttons
from handlers.keyboard import handle_reply_keyboard
from handlers.reports import (
    show_daily_report,
    show_monthly_report
)
from handlers.betting import execute_single_bet
from handlers.base import return_to_home, handle_user_registration_and_login

__all__ = [
    'start_command',
    'show_start_game_info',
    'handle_profile',
    'handle_deposit',
    'handle_withdraw',
    'handle_customer_service',
    'handle_inline_buttons',
    'handle_reply_keyboard',
    'show_daily_report',
    'show_monthly_report',
    'execute_single_bet',
    'return_to_home',
    'handle_user_registration_and_login'
]
