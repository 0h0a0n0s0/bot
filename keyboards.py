"""
鍵盤布局模組
存放所有鍵盤生成函數
"""

from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup


def get_home_keyboard() -> ReplyKeyboardMarkup:
    """
    獲取首頁底部常駐菜單
    """
    start_game_button = KeyboardButton(text="开始游戏")
    profile_button = KeyboardButton(text="个人中心")
    deposit_button = KeyboardButton(text="充值")
    withdraw_button = KeyboardButton(text="提款")
    
    return ReplyKeyboardMarkup(
        [
            [start_game_button, profile_button],  # 第一行
            [deposit_button, withdraw_button]  # 第二行
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )


def get_game_level1_keyboard() -> ReplyKeyboardMarkup:
    """
    獲取第一層遊戲菜單（哈希转盘那一层）
    """
    hash_wheel_button = KeyboardButton(text="哈希转盘")
    flat_cow_button = KeyboardButton(text="平倍牛牛")
    ten_cow_button = KeyboardButton(text="十倍牛牛")
    
    lucky_banker_button = KeyboardButton(text="幸运庄闲")
    more_games_button = KeyboardButton(text="更多游戏")
    back_home_button = KeyboardButton(text="返回主页")
    
    return ReplyKeyboardMarkup(
        [
            [hash_wheel_button, flat_cow_button, ten_cow_button],
            [lucky_banker_button, more_games_button, back_home_button]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )


def get_game_level2_keyboard() -> ReplyKeyboardMarkup:
    """
    獲取第二層遊戲菜單（更多游戏那一层）
    """
    lucky_hash_button = KeyboardButton(text="幸运哈希")
    hash_odd_even_button = KeyboardButton(text="哈希单双")
    hash_big_small_button = KeyboardButton(text="哈希大小")
    
    baccarat_button = KeyboardButton(text="百家乐")
    prev_page_button = KeyboardButton(text="上一页")
    
    return ReplyKeyboardMarkup(
        [
            [lucky_hash_button, hash_odd_even_button, hash_big_small_button],
            [baccarat_button, prev_page_button]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )


def get_profile_keyboard() -> ReplyKeyboardMarkup:
    """
    獲取個人中心底部菜單
    """
    report_center_button = KeyboardButton(text="报表中心")
    security_center_button = KeyboardButton(text="安全中心")
    back_home_button = KeyboardButton(text="返回主页")
    
    return ReplyKeyboardMarkup(
        [
            [report_center_button, security_center_button],  # 第一行
            [back_home_button]  # 第二行
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )


def get_security_center_keyboard() -> ReplyKeyboardMarkup:
    """
    獲取安全中心底部菜單
    """
    withdrawal_password_button = KeyboardButton(text="提款密码")
    usdt_trc20_button = KeyboardButton(text="USDT-TRC20绑定")
    usdt_erc20_button = KeyboardButton(text="USDT-ERC20绑定")
    back_prev_button = KeyboardButton(text="返回上页")
    
    return ReplyKeyboardMarkup(
        [
            [withdrawal_password_button, usdt_trc20_button],  # 第一行
            [usdt_erc20_button, back_prev_button]  # 第二行
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )


def get_password_input_keyboard() -> InlineKeyboardMarkup:
    """
    獲取提款密碼輸入數字鍵盤（Inline 按鈕）
    """
    from telegram import InlineKeyboardButton
    
    button_1 = InlineKeyboardButton(text="1", callback_data="pwd_1")
    button_2 = InlineKeyboardButton(text="2", callback_data="pwd_2")
    button_3 = InlineKeyboardButton(text="3", callback_data="pwd_3")
    button_4 = InlineKeyboardButton(text="4", callback_data="pwd_4")
    button_5 = InlineKeyboardButton(text="5", callback_data="pwd_5")
    button_6 = InlineKeyboardButton(text="6", callback_data="pwd_6")
    button_7 = InlineKeyboardButton(text="7", callback_data="pwd_7")
    button_8 = InlineKeyboardButton(text="8", callback_data="pwd_8")
    button_9 = InlineKeyboardButton(text="9", callback_data="pwd_9")
    button_cancel = InlineKeyboardButton(text="取消", callback_data="pwd_cancel")
    button_0 = InlineKeyboardButton(text="0", callback_data="pwd_0")
    button_delete = InlineKeyboardButton(text="删除", callback_data="pwd_delete")
    
    return InlineKeyboardMarkup(
        [
            [button_1, button_2, button_3],  # 第一行：1, 2, 3
            [button_4, button_5, button_6],  # 第二行：4, 5, 6
            [button_7, button_8, button_9],  # 第三行：7, 8, 9
            [button_cancel, button_0, button_delete]  # 第四行：取消, 0, 删除
        ]
    )




def get_beginner_room_betting_keyboard() -> ReplyKeyboardMarkup:
    """
    獲取初級房投注金額選擇底部菜單
    """
    bet_2_button = KeyboardButton(text="2元")
    bet_5_button = KeyboardButton(text="5元")
    bet_10_button = KeyboardButton(text="10元")
    bet_30_button = KeyboardButton(text="30元")
    bet_50_button = KeyboardButton(text="50元")
    auto_bet_button = KeyboardButton(text="自动下注")
    confirm_room_button = KeyboardButton(text="确认当前房型")
    back_room_selection_button = KeyboardButton(text="返回房型选单")
    
    return ReplyKeyboardMarkup(
        [
            [bet_2_button, bet_5_button, bet_10_button, bet_30_button],  # 第一行：2元 / 5元 / 10元 / 30元
            [bet_50_button, auto_bet_button, confirm_room_button, back_room_selection_button]  # 第二行：50元 / 自动下注 / 确认当前房型 / 返回房型选单
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )


def get_hash_wheel_betting_keyboard() -> ReplyKeyboardMarkup:
    """
    獲取哈希轉盤投注金額選擇底部菜單（移除確認當前房型，返回房型選單改為返回上頁）
    """
    bet_2_button = KeyboardButton(text="2元")
    bet_5_button = KeyboardButton(text="5元")
    bet_10_button = KeyboardButton(text="10元")
    bet_30_button = KeyboardButton(text="30元")
    bet_50_button = KeyboardButton(text="50元")
    bet_100_button = KeyboardButton(text="100元")
    bet_150_button = KeyboardButton(text="150元")
    bet_200_button = KeyboardButton(text="200元")
    bet_300_button = KeyboardButton(text="300元")
    bet_500_button = KeyboardButton(text="500元")
    auto_bet_button = KeyboardButton(text="自动下注")
    back_prev_button = KeyboardButton(text="返回上页")
    
    return ReplyKeyboardMarkup(
        [
            [bet_2_button, bet_5_button, bet_10_button, bet_30_button, bet_50_button],  # 第一行：2元 / 5元 / 10元 / 30元 / 50元
            [bet_100_button, bet_150_button, bet_200_button, bet_300_button, bet_500_button],  # 第二行：100元 / 150元 / 200元 / 300元 / 500元
            [auto_bet_button, back_prev_button]  # 第三行：自动下注 / 返回上页
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )


def get_personal_report_keyboard() -> ReplyKeyboardMarkup:
    """
    獲取個人報表底部菜單
    """
    daily_stats_button = KeyboardButton(text="日统计")
    monthly_stats_button = KeyboardButton(text="月统计")
    
    back_prev_button = KeyboardButton(text="返回上页")
    
    return ReplyKeyboardMarkup(
        [
            [daily_stats_button, monthly_stats_button],  # 第一行
            [back_prev_button]  # 第二行
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )


def get_auto_bet_amount_keyboard() -> ReplyKeyboardMarkup:
    """
    獲取自動下注金額選擇底部菜單
    """
    bet_2_button = KeyboardButton(text="2元")
    bet_5_button = KeyboardButton(text="5元")
    bet_10_button = KeyboardButton(text="10元")
    bet_30_button = KeyboardButton(text="30元")
    bet_50_button = KeyboardButton(text="50元")
    bet_100_button = KeyboardButton(text="100元")
    bet_150_button = KeyboardButton(text="150元")
    bet_200_button = KeyboardButton(text="200元")
    bet_300_button = KeyboardButton(text="300元")
    bet_500_button = KeyboardButton(text="500元")
    back_prev_button = KeyboardButton(text="返回上页")
    
    return ReplyKeyboardMarkup(
        [
            [bet_2_button, bet_5_button, bet_10_button, bet_30_button, bet_50_button],  # 第一行：2元 / 5元 / 10元 / 30元 / 50元
            [bet_100_button, bet_150_button, bet_200_button, bet_300_button, bet_500_button],  # 第二行：100元 / 150元 / 200元 / 300元 / 500元
            [back_prev_button]  # 第三行：返回上页
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )


def get_auto_bet_count_keyboard() -> ReplyKeyboardMarkup:
    """
    獲取自動下注次數選擇底部菜單
    """
    count_10_button = KeyboardButton(text="10次")
    count_20_button = KeyboardButton(text="20次")
    count_30_button = KeyboardButton(text="30次")
    count_50_button = KeyboardButton(text="50次")
    count_100_button = KeyboardButton(text="100次")
    count_150_button = KeyboardButton(text="150次")
    count_200_button = KeyboardButton(text="200次")
    count_300_button = KeyboardButton(text="300次")
    count_500_button = KeyboardButton(text="500次")
    count_1000_button = KeyboardButton(text="1000次")
    stop_on_click_button = KeyboardButton(text="下注到点击停止")
    back_prev_button = KeyboardButton(text="返回上页")
    
    return ReplyKeyboardMarkup(
        [
            [count_10_button, count_20_button, count_30_button, count_50_button, count_100_button],  # 第一行：10次 / 20次 / 30次 / 50次 / 100次
            [count_150_button, count_200_button, count_300_button, count_500_button, count_1000_button],  # 第二行：150次 / 200次 / 300次 / 500次 / 1000次
            [stop_on_click_button, back_prev_button]  # 第三行：下注到点击停止 / 返回上页
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )


def get_stop_betting_keyboard() -> ReplyKeyboardMarkup:
    """
    獲取停止下注底部菜單
    """
    stop_betting_button = KeyboardButton(text="停止下注")
    
    return ReplyKeyboardMarkup(
        [
            [stop_betting_button]  # 停止下注
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )



