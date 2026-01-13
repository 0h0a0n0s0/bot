"""
訊息內容模組 - binding
"""


def get_bank_card_binding_message(current_card_number: str | None = None) -> str:
    """
    獲取銀行卡綁定提示訊息
    :param current_card_number: 當前已綁定的銀行卡號（格式化後的），如果沒有則為None
    """
    message = ""
    
    if current_card_number:
        message += f"当前银行卡：{current_card_number}\n"
        message += "\n"
    
    message += (
        "请依照下列格式输入银行卡资料，如无开户银行、开户城市，则于对应行填写\"无\"即可\n"
        "\n"
        "------------\n"
        "\n"
        "开户姓名\n"
        "银行卡号\n"
        "开户银行\n"
        "开户城市\n"
        "\n"
        "------------\n"
        "\n"
        "填写范例：\n"
        "\n"
        "王小明\n"
        "1234567890123456\n"
        "visa银行\n"
        "无"
    )
    
    return message

def get_bank_card_binding_success_message() -> str:
    """
    獲取銀行卡綁定成功訊息
    """
    return "绑定成功！"

def get_bank_card_binding_failure_message() -> str:
    """
    獲取銀行卡綁定失敗訊息
    """
    return "绑定失败，请依照指定格式送入资料"

def get_wallet_binding_message(current_address: str | None = None) -> str:
    """
    獲取錢包綁定提示訊息（USDT-TRC20/USDT-ERC20）
    :param current_address: 當前已綁定的錢包地址（格式化後的），如果沒有則為None
    """
    message = ""
    
    if current_address:
        message += f"当前钱包地址：{current_address}\n"
        message += "\n"
    
    message += (
        "请依照下列格式输入钱包地址\n"
        "\n"
        "------------\n"
        "\n"
        "钱包地址\n"
        "提款密码（需与首次绑定银行卡的密码一致）\n"
        "\n"
        "------------\n"
        "\n"
        "填写范例：\n"
        "\n"
        "TWuN26pEnPDe5Fg15wWtdcTXcetzxgJS4V\n"
        "1234"
    )
    
    return message

def get_wallet_binding_success_message() -> str:
    """
    獲取錢包綁定成功訊息
    """
    return "绑定成功！"

def get_wallet_binding_failure_message() -> str:
    """
    獲取錢包綁定失敗訊息
    """
    return "绑定失败，请依照指定格式送入资料"

def get_bank_card_required_message() -> str:
    """
    獲取需要先綁定銀行卡的提示訊息
    """
    return "请先绑定银行卡和设定提款密码"

def get_password_mismatch_message() -> str:
    """
    獲取密碼不一致的錯誤訊息
    """
    return "密码错误，提款密码必须与首次绑定银行卡的密码一致"


def get_withdrawal_password_setup_message(current_length: int = 0) -> str:
    """
    獲取提款密碼設置提示訊息
    :param current_length: 當前已輸入的密碼長度（0-4）
    """
    # 生成密碼顯示（用*表示已輸入，-表示未輸入）
    password_display = "*" * current_length + "-" * (4 - current_length)
    
    return (
        "请设置提现密码\n"
        "----------------------------------------\n"
        f"🔑:{password_display}"
    )


def get_withdrawal_password_confirm_message(current_length: int = 0) -> str:
    """
    獲取提款密碼確認提示訊息
    :param current_length: 當前已輸入的確認密碼長度（0-4）
    """
    # 生成密碼顯示（用*表示已輸入，-表示未輸入）
    password_display = "*" * current_length + "-" * (4 - current_length)
    
    return (
        "输入确认密码\n"
        "----------------------------------------\n"
        f"🔑:{password_display}"
    )


def get_withdrawal_password_success_message() -> str:
    """
    獲取提款密碼設置成功訊息
    """
    return "提款密码设置成功！"


def get_withdrawal_password_mismatch_message() -> str:
    """
    獲取提款密碼確認不一致的錯誤訊息
    """
    return "两次输入的密码不一致，请重新设置"