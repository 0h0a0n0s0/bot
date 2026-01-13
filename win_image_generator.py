"""
中獎圖片生成模組
使用 Pillow 在底圖上繪製動態文字
"""

import os
import logging
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from typing import Optional

logger = logging.getLogger(__name__)

# 排版參數配置（集中定義，方便微調）
LAYOUT_CONFIG = {
    "start_x": 50,  # 起始 x 座標
    "start_y": 200,  # 起始 y 座標
    "line_spacing": 50,  # 行距
    "max_width": 600,  # 單行最大寬度
    "base_font_size": 40,  # 基礎字體大小
    "min_font_size": 24,  # 最小字體大小（用於自動縮小）
}

# 文字顏色（淺金色/米黃色）
TEXT_COLOR = (255, 235, 180)  # RGB 淺金色
# 描邊顏色（深色，確保在紅色背景上清晰）
STROKE_COLOR = (100, 0, 0)  # RGB 深紅色
STROKE_WIDTH = 2  # 描邊寬度


def _find_font_path() -> Optional[str]:
    """
    尋找可用的中文字體路徑
    優先順序：系統字體 > 默認字體
    """
    # macOS 系統字體路徑
    mac_fonts = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
    ]
    
    # Linux 系統字體路徑
    linux_fonts = [
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
        "/usr/share/fonts/truetype/arphic/uming.ttc",
    ]
    
    # Windows 系統字體路徑
    windows_fonts = [
        "C:/Windows/Fonts/msyh.ttc",  # 微軟雅黑
        "C:/Windows/Fonts/simhei.ttf",  # 黑體
        "C:/Windows/Fonts/simsun.ttc",  # 宋體
    ]
    
    # 根據系統選擇字體列表
    import platform
    system = platform.system()
    if system == "Darwin":  # macOS
        font_paths = mac_fonts
    elif system == "Linux":
        font_paths = linux_fonts
    elif system == "Windows":
        font_paths = windows_fonts
    else:
        font_paths = mac_fonts + linux_fonts + windows_fonts
    
    # 尋找第一個存在的字體
    for font_path in font_paths:
        if os.path.exists(font_path):
            logger.info(f"找到字體: {font_path}")
            return font_path
    
    logger.warning("未找到系統中文字體，將使用默認字體（可能無法正確顯示中文）")
    return None


def _get_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """
    獲取指定大小的字體
    :param size: 字體大小
    :return: 字體對象
    """
    font_path = _find_font_path()
    try:
        if font_path:
            # 如果是 .ttc 文件，需要指定字體索引（通常 0 是常規字體）
            if font_path.endswith('.ttc'):
                return ImageFont.truetype(font_path, size, index=0)
            else:
                return ImageFont.truetype(font_path, size)
        else:
            # 使用默認字體（可能無法顯示中文）
            return ImageFont.load_default()
    except Exception as e:
        logger.warning(f"載入字體失敗: {e}，使用默認字體")
        return ImageFont.load_default()


def _truncate_text_middle(text: str, max_width: int, font: ImageFont.FreeTypeFont | ImageFont.ImageFont) -> str:
    """
    中間省略文字（用於交易哈希等長文字）
    :param text: 原始文字
    :param max_width: 最大寬度
    :param font: 字體對象
    :return: 處理後的文字
    """
    # 創建臨時 ImageDraw 來測量文字寬度
    temp_img = Image.new('RGB', (1000, 100))
    temp_draw = ImageDraw.Draw(temp_img)
    
    # 如果文字寬度不超過最大寬度，直接返回
    try:
        bbox = temp_draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
    except Exception:
        # 如果測量失敗，直接返回原文字
        return text
    
    if text_width <= max_width:
        return text
    
    # 需要省略，計算前後保留的長度
    # 使用二分法找到合適的長度
    left_len = len(text) // 2
    right_len = len(text) - left_len
    
    # 逐步縮短，直到符合寬度要求
    while left_len > 0 and right_len > 0:
        truncated = text[:left_len] + "..." + text[-right_len:]
        try:
            bbox = temp_draw.textbbox((0, 0), truncated, font=font)
            truncated_width = bbox[2] - bbox[0]
        except Exception:
            # 如果測量失敗，返回當前截斷的文字
            return truncated
        
        if truncated_width <= max_width:
            return truncated
        
        # 如果還是太長，縮短左右兩邊
        left_len -= 1
        right_len -= 1
    
    # 如果還是太長，返回前幾個字符 + "..."
    return text[:10] + "..."


def _truncate_text_end(text: str, max_width: int, font: ImageFont.FreeTypeFont | ImageFont.ImageFont) -> str:
    """
    尾部省略文字（用於一般文字）
    :param text: 原始文字
    :param max_width: 最大寬度
    :param font: 字體對象
    :return: 處理後的文字
    """
    # 創建臨時 ImageDraw 來測量文字寬度
    temp_img = Image.new('RGB', (1000, 100))
    temp_draw = ImageDraw.Draw(temp_img)
    
    # 如果文字寬度不超過最大寬度，直接返回
    try:
        bbox = temp_draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
    except Exception:
        # 如果測量失敗，直接返回原文字
        return text
    
    if text_width <= max_width:
        return text
    
    # 需要省略，從尾部開始縮短
    truncated = text
    while len(truncated) > 0:
        test_text = truncated + "..."
        try:
            bbox = temp_draw.textbbox((0, 0), test_text, font=font)
            test_width = bbox[2] - bbox[0]
        except Exception:
            # 如果測量失敗，返回當前測試文字
            return test_text
        
        if test_width <= max_width:
            return test_text
        
        truncated = truncated[:-1]
    
    return "..."


def _adjust_font_size(text: str, max_width: int, base_font_size: int, min_font_size: int) -> tuple[int, ImageFont.FreeTypeFont | ImageFont.ImageFont]:
    """
    自動調整字體大小以適應寬度
    :param text: 文字內容
    :param max_width: 最大寬度
    :param base_font_size: 基礎字體大小
    :param min_font_size: 最小字體大小
    :return: (字體大小, 字體對象)
    """
    font_size = base_font_size
    font = _get_font(font_size)
    
    # 創建臨時 ImageDraw 來測量文字寬度
    temp_img = Image.new('RGB', (1000, 100))
    temp_draw = ImageDraw.Draw(temp_img)
    
    # 測量文字寬度
    try:
        bbox = temp_draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
    except Exception:
        # 如果測量失敗，返回基礎字體大小
        return base_font_size, font
    
    # 如果寬度超過最大寬度，逐步縮小字體
    while text_width > max_width and font_size > min_font_size:
        font_size -= 2
        font = _get_font(font_size)
        try:
            bbox = temp_draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
        except Exception:
            # 如果測量失敗，返回當前字體大小
            break
    
    return font_size, font


def generate_win_image(
    game_name: str,
    transaction_hash: str,
    player_name: str,
    bet_amount: float,
    win_amount: float,
    game_result: str,
    bet_time: datetime
) -> str:
    """
    生成中獎圖片
    
    :param game_name: 遊戲名稱
    :param transaction_hash: 交易哈希
    :param player_name: 投注玩家
    :param bet_amount: 投注金額
    :param win_amount: 中獎金額
    :param game_result: 遊戲結果
    :param bet_time: 投注時間
    :return: 生成的圖片路徑
    """
    # 底圖路徑
    base_image_path = "./images/中奖底图.jpg"
    
    # 輸出目錄
    output_dir = "./images/win_pic"
    
    # 確保輸出目錄存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 檢查底圖是否存在
    if not os.path.exists(base_image_path):
        logger.error(f"底圖不存在: {base_image_path}")
        raise FileNotFoundError(f"底圖不存在: {base_image_path}")
    
    # 載入底圖
    try:
        img = Image.open(base_image_path)
        # 轉換為 RGB 模式（確保兼容性）
        if img.mode != 'RGB':
            img = img.convert('RGB')
    except Exception as e:
        logger.error(f"載入底圖失敗: {e}")
        raise
    
    # 創建繪圖對象
    draw = ImageDraw.Draw(img)
    
    # 準備要繪製的文字內容
    fields = [
        ("游戏名称", game_name),
        ("交易哈希", transaction_hash),
        ("投注玩家", player_name),
        ("投注金额", f"{bet_amount:.2f} USDT"),
        ("中奖金额", f"{win_amount:.2f} USDT"),
        ("游戏结果", game_result),
        ("投注时间", bet_time.strftime("%Y-%m-%d %H:%M:%S")),
    ]
    
    # 當前 y 座標
    current_y = LAYOUT_CONFIG["start_y"]
    
    # 繪製每一行
    for field_name, field_value in fields:
        # 組合文字（使用全角冒號）
        full_text = f"{field_name}：{field_value}"
        
        # 處理交易哈希（使用中間省略）
        if field_name == "交易哈希":
            # 清理哈希值格式（移除 ** 標記）
            clean_hash = field_value.replace("**", "")
            # 使用中間省略策略
            font = _get_font(LAYOUT_CONFIG["base_font_size"])
            truncated_hash = _truncate_text_middle(clean_hash, LAYOUT_CONFIG["max_width"], font)
            full_text = f"{field_name}：{truncated_hash}"
        else:
            # 其他字段：先嘗試自動縮小字體，如果還是超出則尾部省略
            font_size, font = _adjust_font_size(
                full_text,
                LAYOUT_CONFIG["max_width"],
                LAYOUT_CONFIG["base_font_size"],
                LAYOUT_CONFIG["min_font_size"]
            )
            
            # 如果字體已經縮到最小還是超出，則尾部省略
            if font_size <= LAYOUT_CONFIG["min_font_size"]:
                full_text = _truncate_text_end(full_text, LAYOUT_CONFIG["max_width"], font)
        
        # 獲取字體（如果不是交易哈希，使用調整後的字體）
        if field_name != "交易哈希":
            font = _get_font(font_size)
        
        # 繪製文字（帶描邊）
        # 先繪製描邊（在四個方向各繪製一次，形成描邊效果）
        for dx in [-STROKE_WIDTH, 0, STROKE_WIDTH]:
            for dy in [-STROKE_WIDTH, 0, STROKE_WIDTH]:
                if dx != 0 or dy != 0:
                    draw.text(
                        (LAYOUT_CONFIG["start_x"] + dx, current_y + dy),
                        full_text,
                        font=font,
                        fill=STROKE_COLOR
                    )
        
        # 再繪製主文字
        draw.text(
            (LAYOUT_CONFIG["start_x"], current_y),
            full_text,
            font=font,
            fill=TEXT_COLOR
        )
        
        # 更新 y 座標（移到下一行）
        # 獲取文字高度
        bbox = draw.textbbox((LAYOUT_CONFIG["start_x"], current_y), full_text, font=font)
        text_height = bbox[3] - bbox[1]
        current_y += text_height + LAYOUT_CONFIG["line_spacing"]
    
    # 生成輸出文件名（使用時間戳避免衝突）
    timestamp = bet_time.strftime("%Y%m%d_%H%M%S_%f")
    output_filename = f"win_{timestamp}.png"
    output_path = os.path.join(output_dir, output_filename)
    
    # 保存圖片（PNG 格式，保證文字清晰）
    try:
        img.save(output_path, "PNG")
        logger.info(f"中獎圖片已生成: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"保存圖片失敗: {e}")
        raise
