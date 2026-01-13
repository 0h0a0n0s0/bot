"""
訊息內容模組 - report
"""
from config import VERIFICATION_ADDRESS, VERIFICATION_AMOUNT


def get_daily_report_message(date: str, game: str = "总计") -> str:
    """
    獲取日統計報表訊息內容
    :param date: 日期字符串，格式：YYYY-MM-DD
    :param game: 遊戲類型，默認為「总计」
    """
    return (
        f"报表类型：{game}\n"
        f"时间：{date}\n"
        "活跃账号：0\n"
        "------------------------------------\n"
        "投注金额：0 USDT\n"
        "派奖金额：0 USDT\n"
        "投注盈亏：0 USDT\n"
        "充值总额：0 USDT\n"
        "提款总额：0 USDT\n"
        "充提输赢：0 USDT\n"
        "转账笔数：0\n"
    )

def get_monthly_report_message(month: str, game: str = "总计") -> str:
    """
    獲取月統計報表訊息內容
    :param month: 月份字符串，格式：YYYY-MM（例如："2026-01"）
    :param game: 遊戲類型，默認為「总计」
    """
    from datetime import datetime
    from calendar import monthrange
    
    # 解析月份
    year, month_num = map(int, month.split("-"))
    
    # 計算當月的第一天和最後一天
    start_date = datetime(year, month_num, 1)
    last_day = monthrange(year, month_num)[1]  # 獲取當月最後一天
    end_date = datetime(year, month_num, last_day)
    
    # 生成日期範圍字符串
    date_range = f"{start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}"
    
    return (
        f"报表类型：{game}\n"
        f"时间：{date_range}\n"
        "活跃帐号：0\n"
        "------------------------------------\n"
        "投注金额：0 USDT\n"
        "派奖金额：0 USDT\n"
        "投注盈亏：0 USDT\n"
        "充值总额：0 USDT\n"
        "提款总额：0 USDT\n"
        "充提输赢：0 USDT\n"
        "转账笔数：0\n"
    )