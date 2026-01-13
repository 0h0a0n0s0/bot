"""
訊息內容模組 - account
"""


def get_account_info_message(telegram_id: int, username: str, show_password: bool = False, password: str = "", usdt_balance: str = "0") -> str:
    """
    獲取賬戶信息訊息
    :param telegram_id: 用戶的 Telegram ID
    :param username: 用戶名
    :param show_password: 是否顯示密碼
    :param password: 密碼（如果不顯示可以為空）
    :param usdt_balance: USDT餘額，默認為"0"
    """
    message = f"用户名：{username}\n"
    
    if show_password and password:
        message += f"密码：{password}\n"
    
    message += f"电报ID：{telegram_id}\n"
    message += f"USDT余额：{usdt_balance}"
    
    return message

def get_user_check_message(user_exists: bool, user_logged_in: bool = False) -> str:
    """
    獲取用戶檢查說明報文（純文案）
    :param user_exists: 用戶是否存在
    :param user_logged_in: 用戶是否已登入（僅在用戶存在時有效）
    :return: 說明報文
    """
    message = "【首先确认是否有这个TG ID用户】\n\n"
    
    if not user_exists:
        # 如果沒有這個TG ID用戶
        message += (
            "【如果没有这个TG ID 用户】\n"
            "于网投平台注册该TG用户\n"
            "帐号生成优先度：TG绑定手机号>TGusernam>平台会员ID\n"
            "密码生成方式：8码随机小写英文＋数字\n"
            "TG ID必须写入网投，后续只要机器人请求登入时带TG ID就给登入\n\n"
            "第二则讯息维持显示密码\n\n"
            "【如果有这个TG ID用户】\n"
            "若用户有登入，带入第二则讯息，但是无显示密码\n"
            "若用户无登入，帮用户登入，带入第二则讯息，但是无显示密码"
        )
    else:
        # 如果有這個TG ID用戶
        message += "【如果有这个TG ID用户】\n\n"
        
        if user_logged_in:
            message += "若用户有登入，带入第二则讯息，但是无显示密码"
        else:
            message += "若用户无登入，帮用户登入，带入第二则讯息，但是无显示密码"
    
    return message