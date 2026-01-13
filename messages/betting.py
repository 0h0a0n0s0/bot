"""
訊息內容模組 - betting
"""
import re


def get_bet_success_message(bet_amount: str, balance_after_deduct: str) -> str:
    """
    獲取投注成功提示訊息
    :param bet_amount: 投注金額
    :param balance_after_deduct: 扣款後餘額
    """
    return f"投注 {bet_amount} 成功，投注后余额 {balance_after_deduct}"

def get_waiting_hash_message() -> str:
    """
    獲取等待哈希結果提示訊息
    """
    return "请稍等哈希结果！"

def get_hash_result_message(bonus: str, hash_value: str, hash_url: str, final_balance: str = "") -> str:
    """
    獲取哈希結果訊息
    :param bonus: 彩金金額
    :param hash_value: 哈希值（完整）
    :param hash_url: 哈希值超鏈接URL
    :param final_balance: 最終餘額（中獎後，如果為空則不顯示）
    """
    # 提取哈希值中的數字部分（654 和 32）並設置為粗體
    # 哈希值格式：...3c27e7b94**654**feb**32**
    # 需要將 **654** 和 **32** 轉換為 <b>654</b> 和 <b>32</b>
    import re
    # 將 **數字** 替換為 <b>數字</b>
    formatted_hash = re.sub(r'\*\*(\d+)\*\*', r'<b>\1</b>', hash_value)
    
    # 構建帶超鏈接的哈希值
    hash_link = f'<a href="{hash_url}">{formatted_hash}</a>'
    
    # 判斷是否中獎
    bonus_float = float(bonus)
    if bonus_float > 0:
        # 中獎時顯示：恭喜中奖、USDT餘額、哈希值
        message = f"恭喜中奖 {bonus} USDT！\n"
        if final_balance:
            message += f"\nUSDT馀额：{final_balance}\n"
        message += f"\n哈希值：{hash_link}"
        return message
    else:
        # 未中獎時只顯示哈希值
        return f"未中奖\n\n哈希值：{hash_link}"


def get_auto_bet_amount_prompt(usdt_balance: str = "0") -> str:
    """
    獲取自動下注金額選擇提示訊息
    :param usdt_balance: USDT餘額，默認為"0"
    """
    return (
        f"当前USDT余额：{usdt_balance}\n"
        "请先选择自动下注金额"
    )


def get_bet_confirmation_message(bet_amount: str) -> str:
    """
    獲取投注確認訊息
    :param bet_amount: 投注金額（如 "2"）
    """
    return f"请确认是否下注 {bet_amount} 元？"


def get_bet_timeout_message() -> str:
    """
    獲取投注超時訊息
    """
    return "投注超时，请重新选择投注金额。"


def get_auto_bet_confirmation_message(bet_amount: str, bet_count: int, total_amount: str) -> str:
    """
    獲取自動下注確認訊息
    :param bet_amount: 每次下注金額（如 "2"）
    :param bet_count: 下注次數（如 10）
    :param total_amount: 總金額（如 "20.00"）
    """
    return f"请确认是否下注 {bet_amount} 元，下注 {bet_count} 次，共 {total_amount} 元？"


def get_auto_bet_timeout_message() -> str:
    """
    獲取自動下注超時訊息
    """
    return "自动投注超时，请重新选择投注金额。"


def get_auto_bet_start_message(current_count: int, total_count: int, bet_amount: str) -> str:
    """
    獲取自動下注開始訊息
    :param current_count: 當前次數（從1開始）
    :param total_count: 總次數
    :param bet_amount: 每次投注金額
    """
    return f"已开始自动下注，当前次数为（{current_count} / {total_count}），每次下注金额 {bet_amount} USDT"


def get_auto_bet_stop_confirmation_message(bet_amount: str) -> str:
    """
    獲取下注到點擊停止的確認訊息
    :param bet_amount: 每次下注金額（如 "2"）
    """
    return f"请确认是否下注 {bet_amount} 元，下注到再次点击停止？"


def get_auto_bet_stop_bet_message(bet_count: int, bet_amount: str, balance_after_deduct: str) -> str:
    """
    獲取下注到點擊停止的投注成功訊息
    :param bet_count: 投注次數（從1開始）
    :param bet_amount: 投注金額
    :param balance_after_deduct: 扣款後餘額
    """
    return f"自动投注第 {bet_count} 次，投注 {bet_amount} 元成功，投注后馀额 {balance_after_deduct} 元"


def get_win_caption_message(
    game_name: str,
    bet_amount: str,
    win_amount: str,
    bet_time: str,
    final_balance: str = ""
) -> str:
    """
    获取中奖消息的 caption（用于 Telegram 图片说明）
    :param game_name: 游戏名称
    :param bet_amount: 投注金额
    :param win_amount: 中奖金额
    :param bet_time: 投注时间（格式化后的字符串）
    :param final_balance: 最终余额（可选）
    :return: caption 文字
    """
    message = f"🎉 恭喜中奖！\n\n"
    message += f"游戏：{game_name}\n"
    message += f"投注金额：{bet_amount} USDT\n"
    message += f"中奖金额：{win_amount} USDT\n"
    message += f"时间：{bet_time}\n"
    
    if final_balance:
        message += f"\n当前余额：{final_balance} USDT"
    
    return message