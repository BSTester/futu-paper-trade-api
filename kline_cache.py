"""K线数据缓存模块

只缓存日K线及以上级别的数据（daily, weekly, monthly, quarterly, yearly）
分钟级数据不缓存，因为实时性要求高
"""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import threading
import time


class KlineCache:
    """K线数据缓存类
    
    缓存策略：
    - 只缓存日K线及以上级别的数据
    - 每只股票独立的24小时失效时间
    - 分钟级数据不缓存
    - 线程安全
    """
    
    def __init__(self, ttl_hours: int = 24):
        """
        初始化缓存
        
        Args:
            ttl_hours: 缓存有效期（小时），默认24小时
        """
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_time: Dict[str, float] = {}  # 存储缓存时间戳
        self._lock = threading.Lock()
        self._ttl_seconds = ttl_hours * 3600  # 转换为秒
        
        # 可缓存的时间间隔（日K及以上）
        self._cacheable_intervals = {
            2: "daily",      # kline_type=2
            3: "weekly",     # kline_type=3
            4: "monthly",    # kline_type=4
            5: "yearly",     # kline_type=5
            11: "quarterly"  # kline_type=11
        }
    
    def _generate_cache_key(self, stock_id: str, kline_type: int, market_type: str) -> str:
        """生成缓存键"""
        return f"{market_type}:{stock_id}:{kline_type}"
    
    def _is_cacheable(self, kline_type: int) -> bool:
        """判断是否可以缓存
        
        Args:
            kline_type: K线类型
                1: 分时（不缓存）
                2: 日K（缓存）
                3: 周K（缓存）
                4: 月K（缓存）
                5: 年K（缓存）
                11: 季K（缓存）
        
        Returns:
            是否可以缓存
        """
        return kline_type in self._cacheable_intervals
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """判断缓存是否有效
        
        缓存有效条件：
        1. 缓存存在
        2. 缓存时间未超过TTL（默认24小时）
        
        Args:
            cache_key: 缓存键
        
        Returns:
            缓存是否有效
        """
        if cache_key not in self._cache:
            return False
        
        if cache_key not in self._cache_time:
            return False
        
        # 检查缓存是否过期（超过TTL）
        cache_time = self._cache_time[cache_key]
        current_time = time.time()
        elapsed = current_time - cache_time
        
        return elapsed < self._ttl_seconds
    
    def get(
        self,
        stock_id: str,
        kline_type: int,
        market_type: str
    ) -> Optional[Dict[str, Any]]:
        """从缓存获取K线数据
        
        Args:
            stock_id: 股票ID
            kline_type: K线类型
            market_type: 市场类型
        
        Returns:
            缓存的K线数据，如果不存在或已过期则返回None
        """
        # 分钟级数据不缓存
        if not self._is_cacheable(kline_type):
            return None
        
        cache_key = self._generate_cache_key(stock_id, kline_type, market_type)
        
        with self._lock:
            if self._is_cache_valid(cache_key):
                return self._cache[cache_key]
            else:
                # 缓存无效，清理
                if cache_key in self._cache:
                    del self._cache[cache_key]
                if cache_key in self._cache_time:
                    del self._cache_time[cache_key]
                return None
    
    def set(
        self,
        stock_id: str,
        kline_type: int,
        market_type: str,
        data: Dict[str, Any]
    ) -> None:
        """设置K线数据缓存
        
        Args:
            stock_id: 股票ID
            kline_type: K线类型
            market_type: 市场类型
            data: K线数据
        """
        # 分钟级数据不缓存
        if not self._is_cacheable(kline_type):
            return
        
        cache_key = self._generate_cache_key(stock_id, kline_type, market_type)
        
        with self._lock:
            self._cache[cache_key] = data
            self._cache_time[cache_key] = time.time()  # 记录缓存时间戳
    
    def clear(self) -> None:
        """清空所有缓存"""
        with self._lock:
            self._cache.clear()
            self._cache_time.clear()
    
    def clear_expired(self) -> int:
        """清理过期的缓存（超过TTL的缓存）
        
        Returns:
            清理的缓存数量
        """
        current_time = time.time()
        expired_keys = []
        
        with self._lock:
            for cache_key, cache_time in self._cache_time.items():
                elapsed = current_time - cache_time
                if elapsed >= self._ttl_seconds:
                    expired_keys.append(cache_key)
            
            for cache_key in expired_keys:
                if cache_key in self._cache:
                    del self._cache[cache_key]
                if cache_key in self._cache_time:
                    del self._cache_time[cache_key]
        
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息
        
        Returns:
            缓存统计信息
        """
        current_time = time.time()
        
        with self._lock:
            valid_count = 0
            expired_count = 0
            oldest_cache_time = None
            newest_cache_time = None
            
            for cache_key, cache_time in self._cache_time.items():
                elapsed = current_time - cache_time
                
                if elapsed < self._ttl_seconds:
                    valid_count += 1
                else:
                    expired_count += 1
                
                # 记录最老和最新的缓存时间
                if oldest_cache_time is None or cache_time < oldest_cache_time:
                    oldest_cache_time = cache_time
                if newest_cache_time is None or cache_time > newest_cache_time:
                    newest_cache_time = cache_time
            
            stats = {
                "total_cached": len(self._cache),
                "valid_count": valid_count,
                "expired_count": expired_count,
                "ttl_hours": self._ttl_seconds / 3600,
                "current_time": datetime.fromtimestamp(current_time).isoformat()
            }
            
            # 添加最老和最新缓存的时间信息
            if oldest_cache_time is not None:
                stats["oldest_cache_time"] = datetime.fromtimestamp(oldest_cache_time).isoformat()
                stats["oldest_cache_age_hours"] = (current_time - oldest_cache_time) / 3600
            
            if newest_cache_time is not None:
                stats["newest_cache_time"] = datetime.fromtimestamp(newest_cache_time).isoformat()
                stats["newest_cache_age_hours"] = (current_time - newest_cache_time) / 3600
            
            return stats
    
    def get_cache_info(
        self,
        stock_id: str,
        kline_type: int,
        market_type: str
    ) -> Optional[Dict[str, Any]]:
        """获取指定缓存项的详细信息
        
        Args:
            stock_id: 股票ID
            kline_type: K线类型
            market_type: 市场类型
        
        Returns:
            缓存项信息，如果不存在则返回None
        """
        if not self._is_cacheable(kline_type):
            return {
                "cached": False,
                "reason": "分钟级数据不缓存"
            }
        
        cache_key = self._generate_cache_key(stock_id, kline_type, market_type)
        current_time = time.time()
        
        with self._lock:
            if cache_key not in self._cache:
                return {
                    "cached": False,
                    "reason": "缓存不存在"
                }
            
            cache_time = self._cache_time.get(cache_key)
            if cache_time is None:
                return {
                    "cached": False,
                    "reason": "缓存时间丢失"
                }
            
            elapsed = current_time - cache_time
            is_valid = elapsed < self._ttl_seconds
            remaining = self._ttl_seconds - elapsed
            
            return {
                "cached": True,
                "valid": is_valid,
                "cache_time": datetime.fromtimestamp(cache_time).isoformat(),
                "age_hours": elapsed / 3600,
                "remaining_hours": remaining / 3600 if remaining > 0 else 0,
                "ttl_hours": self._ttl_seconds / 3600,
                "expires_at": datetime.fromtimestamp(cache_time + self._ttl_seconds).isoformat()
            }


# 全局缓存实例
_kline_cache = KlineCache()


def get_kline_cache() -> KlineCache:
    """获取全局K线缓存实例"""
    return _kline_cache
