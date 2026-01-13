"""
訊息內容模組 - deposit_withdraw
"""


def get_deposit_amount_prompt(usdt_balance: str = "0") -> str:
    """
    獲取充值金額提示訊息
    :param usdt_balance: USDT餘額，默認為"0"
    """
    return (
        f"当前USDT余额：{usdt_balance}\n"
        "请输入充值金额"
    )

def get_withdraw_amount_prompt(usdt_balance: str = "0") -> str:
    """
    獲取提款金額提示訊息
    :param usdt_balance: USDT餘額，默認為"0"
    """
    return (
        f"当前USDT余额：{usdt_balance}\n"
        "请输入提款金额"
    )

def get_withdraw_method_selection_message() -> str:
    """
    獲取選擇提款方式提示訊息
    """
    return "请选择提款方式"

def get_withdraw_password_prompt() -> str:
    """
    獲取提款密碼提示訊息
    """
    return "请输入提款密码"

def get_withdraw_password_error_message() -> str:
    """
    獲取提款密碼錯誤訊息
    """
    return "密码错误，请重新输入。"

def get_withdraw_success_message() -> str:
    """
    獲取提款申請成功訊息
    """
    return "提款申请已送出，将为您尽速处理！"

def get_deposit_info_message(amount: str) -> str:
    """
    獲取充值信息訊息
    :param amount: 用戶輸入的金額
    """
    return (
        f"请充值{amount}，到此充值地址，点击地址可直接复制\n"
        "\n"
        "<code>TQs4qwRey1fa8z4qwvP1fT28J8TSnS6b25</code>\n"
        "\n"
        "转帐成功后3分钟内上分"
    )


def get_deposit_success_message(amount: str, new_balance: str) -> str:
    """
    獲取充值成功訊息
    :param amount: 充值金額
    :param new_balance: 充值後的餘額
    """
    return (
        f"充值 {amount} USDT成功！\n"
        f"当前USDT余额：{new_balance}"
    )