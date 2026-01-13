"""
消息去重模組
處理 Telegram 消息去重機制
"""

import logging

try:
    from cachetools import TTLCache
    HAS_CACHETOOLS = True
except ImportError:
    HAS_CACHETOOLS = False
    logging.warning("cachetools 未安裝，將使用簡單的 set 進行消息去重（建議安裝：pip install cachetools）")

logger = logging.getLogger(__name__)

# 消息去重機制：儲存已處理過的 message_id
# 使用 TTLCache 自動清理過期條目（保留 1 小時，最多 10000 條）
# 如果沒有安裝 cachetools，則使用簡單的 set（最多保留 1000 條）
if HAS_CACHETOOLS:
    # 使用 TTL Cache：1 小時過期，最多 10000 條
    processed_message_ids: TTLCache[int, bool] = TTLCache(maxsize=10000, ttl=3600)
else:
    # 簡單的 set，手動限制大小
    class ProcessedMessageIds:
        """簡單的消息ID去重容器，限制最大大小"""
        def __init__(self):
            self._set: set[int] = set()
            self._max_size = 1000
        
        def __contains__(self, message_id: int) -> bool:
            return message_id in self._set
        
        def add(self, message_id: int) -> None:
            """添加 message_id，如果超過最大大小則清理最舊的條目"""
            if len(self._set) >= self._max_size:
                # 移除最舊的 100 條（簡單策略：轉為列表後移除前 100 個）
                items_to_remove = list(self._set)[:100]
                for item in items_to_remove:
                    self._set.discard(item)
            self._set.add(message_id)
    
    processed_message_ids = ProcessedMessageIds()


def is_message_processed(message_id: int) -> bool:
    """檢查消息是否已處理"""
    if HAS_CACHETOOLS:
        return message_id in processed_message_ids
    else:
        return message_id in processed_message_ids


def mark_message_processed(message_id: int) -> None:
    """標記消息為已處理"""
    if HAS_CACHETOOLS:
        processed_message_ids[message_id] = True
    else:
        processed_message_ids.add(message_id)
