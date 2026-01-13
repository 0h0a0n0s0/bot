"""
訊息內容模組
包含所有機器人發送的訊息內容
"""

# 導出所有消息函數
from messages.profile import get_profile_message
from messages.game import (
    get_start_game_message,
    get_hash_wheel_info_message,
    get_beginner_room_info_message,
    get_current_room_message,
    get_beginner_room_bet_selection_message
)
from messages.report import (
    get_daily_report_message,
    get_monthly_report_message
)
from messages.account import (
    get_account_info_message,
    get_user_check_message
)
from messages.deposit_withdraw import (
    get_deposit_amount_prompt,
    get_withdraw_amount_prompt,
    get_withdraw_method_selection_message,
    get_withdraw_password_prompt,
    get_withdraw_password_error_message,
    get_withdraw_success_message,
    get_deposit_info_message,
    get_deposit_success_message
)
from messages.binding import (
    get_bank_card_binding_message,
    get_bank_card_binding_success_message,
    get_bank_card_binding_failure_message,
    get_wallet_binding_message,
    get_wallet_binding_success_message,
    get_wallet_binding_failure_message,
    get_bank_card_required_message,
    get_password_mismatch_message,
    get_withdrawal_password_setup_message,
    get_withdrawal_password_confirm_message,
    get_withdrawal_password_success_message,
    get_withdrawal_password_mismatch_message
)
from messages.betting import (
    get_bet_success_message,
    get_waiting_hash_message,
    get_hash_result_message,
    get_auto_bet_amount_prompt,
    get_bet_confirmation_message,
    get_bet_timeout_message,
    get_auto_bet_confirmation_message,
    get_auto_bet_timeout_message,
    get_auto_bet_start_message,
    get_auto_bet_stop_confirmation_message,
    get_auto_bet_stop_bet_message,
    get_win_caption_message
)

__all__ = [
    'get_profile_message',
    'get_start_game_message',
    'get_hash_wheel_info_message',
    'get_beginner_room_info_message',
    'get_current_room_message',
    'get_beginner_room_bet_selection_message',
    'get_daily_report_message',
    'get_monthly_report_message',
    'get_account_info_message',
    'get_user_check_message',
    'get_deposit_amount_prompt',
    'get_withdraw_amount_prompt',
    'get_withdraw_method_selection_message',
    'get_withdraw_password_prompt',
    'get_withdraw_password_error_message',
    'get_withdraw_success_message',
    'get_deposit_info_message',
    'get_deposit_success_message',
    'get_bank_card_binding_message',
    'get_bank_card_binding_success_message',
    'get_bank_card_binding_failure_message',
    'get_wallet_binding_message',
    'get_wallet_binding_success_message',
    'get_wallet_binding_failure_message',
    'get_bank_card_required_message',
    'get_password_mismatch_message',
    'get_withdrawal_password_setup_message',
    'get_withdrawal_password_confirm_message',
    'get_withdrawal_password_success_message',
    'get_withdrawal_password_mismatch_message',
    'get_bet_success_message',
    'get_waiting_hash_message',
    'get_hash_result_message',
    'get_auto_bet_amount_prompt',
    'get_bet_confirmation_message',
    'get_bet_timeout_message',
    'get_auto_bet_confirmation_message',
    'get_auto_bet_timeout_message',
    'get_auto_bet_start_message',
    'get_auto_bet_stop_confirmation_message',
    'get_auto_bet_stop_bet_message',
    'get_win_caption_message'
]
