#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
性能优化工具模块
"""

import threading
import time
import psutil
import os
from functools import wraps


class PerformanceOptimizer:
    """性能优化器类"""
    
    def __init__(self, max_threads=4):
        """
        初始化性能优化器
        
        Args:
            max_threads (int): 最大线程数
        """
        self.max_threads = max_threads
        self.active_threads = 0
        self.thread_lock = threading.Lock()
        self.cache = {}
        self.cache_lock = threading.Lock()

    def set_memory_limit(self, limit):
        """
        设置内存限制
        
        Args:
            limit (str): 内存限制，例如 "1GB", "512MB"
        """
        self.memory_limit = limit

    def set_max_threads(self, max_threads):
        """
        设置最大线程数
        
        Args:
            max_threads (int): 最大线程数
        """
        self.max_threads = max_threads

    def monitor_performance(self, func):
        """
        性能监控装饰器
        
        Args:
            func: 被装饰的函数
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 记录开始时间
            start_time = time.time()
            
            # 记录开始内存
            start_memory = self.check_memory_usage()
            
            try:
                # 执行函数
                result = func(*args, **kwargs)
                
                return result
            finally:
                # 记录结束时间
                end_time = time.time()
                
                # 记录结束内存
                end_memory = self.check_memory_usage()
                
                # 输出性能信息
                print(f"函数 {func.__name__} 执行时间: {end_time - start_time:.2f} 秒")
                print(f"内存使用增加: {end_memory['rss'] - start_memory['rss']} 字节")
        
        return wrapper

    def check_memory_usage(self):
        """
        检查内存使用情况
        
        Returns:
            dict: 内存使用信息
        """
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        
        return {
            'rss': memory_info.rss,      # 物理内存使用
            'vms': memory_info.vms,      # 虚拟内存使用
            'percent': process.memory_percent()  # 内存使用百分比
        }

    def threaded_execution(self, func, *args, **kwargs):
        """
        线程化执行函数
        
        Args:
            func: 要执行的函数
            *args: 函数参数
            **kwargs: 函数关键字参数
            
        Returns:
            线程对象
        """
        def target():
            with self.thread_lock:
                self.active_threads += 1
            
            try:
                func(*args, **kwargs)
            finally:
                with self.thread_lock:
                    self.active_threads -= 1
        
        # 检查是否超过最大线程数
        with self.thread_lock:
            if self.active_threads >= self.max_threads:
                raise Exception("超过最大线程数限制")
        
        thread = threading.Thread(target=target)
        thread.start()
        return thread

    def chunked_processing(self, data, chunk_size=100):
        """
        分块处理数据
        
        Args:
            data: 要处理的数据列表
            chunk_size (int): 每块大小
            
        Yields:
            数据块
        """
        for i in range(0, len(data), chunk_size):
            yield data[i:i + chunk_size]

    def optimize_large_pdf_processing(self, pdf_path):
        """
        优化大PDF文件处理
        
        Args:
            pdf_path (str): PDF文件路径
            
        Returns:
            dict: 优化建议
        """
        file_size = os.path.getsize(pdf_path)
        
        recommendations = {
            'file_size': file_size,
            'use_streaming': file_size > 50 * 1024 * 1024,  # 大于50MB使用流式处理
            'chunk_pages': file_size > 100 * 1024 * 1024,   # 大于100MB分块处理页面
            'memory_warning': file_size > 200 * 1024 * 1024  # 大于200MB给出内存警告
        }
        
        return recommendations

    def monitor_performance_data(self):
        """
        获取性能监控数据
        
        Returns:
            dict: 性能监控数据
        """
        return {
            'timestamp': time(),
            'memory_usage': self.check_memory_usage(),
            'active_threads': self.active_threads
        }