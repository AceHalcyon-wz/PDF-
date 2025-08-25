#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
性能监控模块
提供性能监控和分析工具
"""

import time
import psutil
import os
from functools import wraps
from typing import Callable, Any, Dict
from utils.logger import get_module_logger

logger = get_module_logger("performance")


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        """初始化性能监控器"""
        self.metrics = {}
        self.start_times = {}
        
    def start_monitoring(self, operation_name: str) -> None:
        """
        开始监控操作
        
        Args:
            operation_name (str): 操作名称
        """
        self.start_times[operation_name] = {
            'time': time.time(),
            'memory': psutil.Process(os.getpid()).memory_info().rss
        }
        logger.debug(f"开始监控操作: {operation_name}")
        
    def stop_monitoring(self, operation_name: str) -> Dict[str, Any]:
        """
        停止监控操作并返回性能指标
        
        Args:
            operation_name (str): 操作名称
            
        Returns:
            Dict[str, Any]: 性能指标
        """
        if operation_name not in self.start_times:
            logger.warning(f"未找到操作 {operation_name} 的开始时间记录")
            return {}
            
        start_info = self.start_times[operation_name]
        end_time = time.time()
        end_memory = psutil.Process(os.getpid()).memory_info().rss
        
        metrics = {
            'duration': end_time - start_info['time'],
            'memory_used': end_memory - start_info['memory'],
            'operation_name': operation_name
        }
        
        self.metrics[operation_name] = metrics
        logger.debug(f"操作 {operation_name} 性能指标: {metrics}")
        return metrics
        
    def get_metrics(self, operation_name: str = None) -> Dict[str, Any]:
        """
        获取性能指标
        
        Args:
            operation_name (str, optional): 操作名称，如果为None则返回所有指标
            
        Returns:
            Dict[str, Any]: 性能指标
        """
        if operation_name:
            return self.metrics.get(operation_name, {})
        return self.metrics.copy()
        
    def reset_metrics(self, operation_name: str = None) -> None:
        """
        重置性能指标
        
        Args:
            operation_name (str, optional): 操作名称，如果为None则重置所有指标
        """
        if operation_name:
            self.metrics.pop(operation_name, None)
        else:
            self.metrics.clear()


# 全局性能监控器实例
performance_monitor = PerformanceMonitor()


def monitor_performance(operation_name: str = None):
    """
    性能监控装饰器
    
    Args:
        operation_name (str, optional): 操作名称
    """
    def decorator(func: Callable) -> Callable:
        nonlocal operation_name
        if operation_name is None:
            operation_name = func.__name__
            
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # 开始监控
            performance_monitor.start_monitoring(operation_name)
            
            try:
                # 执行函数
                result = func(*args, **kwargs)
                return result
            finally:
                # 停止监控
                performance_monitor.stop_monitoring(operation_name)
                
        return wrapper
    return decorator


class LRUCache:
    """简单LRU缓存实现"""
    
    def __init__(self, capacity: int):
        """
        初始化LRU缓存
        
        Args:
            capacity (int): 缓存容量
        """
        self.capacity = capacity
        self.cache = {}
        self.access_order = []  # 访问顺序列表
        
    def get(self, key: str) -> Any:
        """
        获取缓存值
        
        Args:
            key (str): 缓存键
            
        Returns:
            Any: 缓存值，如果不存在则返回None
        """
        if key in self.cache:
            # 更新访问顺序
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]
        return None
        
    def put(self, key: str, value: Any) -> None:
        """
        设置缓存值
        
        Args:
            key (str): 缓存键
            value (Any): 缓存值
        """
        if key in self.cache:
            # 更新值并调整访问顺序
            self.cache[key] = value
            self.access_order.remove(key)
            self.access_order.append(key)
        else:
            # 检查容量
            if len(self.cache) >= self.capacity:
                # 移除最久未使用的项
                oldest_key = self.access_order.pop(0)
                del self.cache[oldest_key]
                
            # 添加新项
            self.cache[key] = value
            self.access_order.append(key)
            
    def clear(self) -> None:
        """清空缓存"""
        self.cache.clear()
        self.access_order.clear()
        
    def size(self) -> int:
        """
        获取缓存大小
        
        Returns:
            int: 缓存大小
        """
        return len(self.cache)