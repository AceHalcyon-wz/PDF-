#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
统一日志处理模块
"""

import logging
import os
from datetime import datetime
from concurrent_log_handler import ConcurrentRotatingFileHandler


class LoggerManager:
    """日志管理器"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LoggerManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._initialized = True
            self.loggers = {}
            self.log_dir = "./logs"
            
            # 确保日志目录存在
            if not os.path.exists(self.log_dir):
                os.makedirs(self.log_dir)
    
    def get_logger(self, name="pdf_processor", level=logging.INFO):
        """
        获取日志记录器
        
        Args:
            name (str): 日志记录器名称
            level (int): 日志级别
            
        Returns:
            logging.Logger: 日志记录器实例
        """
        if name in self.loggers:
            return self.loggers[name]
            
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        # 避免重复添加处理器
        if not logger.handlers:
            # 创建文件处理器
            log_file = os.path.join(self.log_dir, f"{name}.log")
            file_handler = ConcurrentRotatingFileHandler(
                log_file, 
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
            
            # 创建控制台处理器
            console_handler = logging.StreamHandler()
            
            # 设置格式
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            # 添加处理器
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
            
            # 防止日志传播到父记录器
            logger.propagate = False
            
        self.loggers[name] = logger
        return logger
    
    def get_logger_for_module(self, module_name):
        """
        为特定模块获取日志记录器
        
        Args:
            module_name (str): 模块名称
            
        Returns:
            logging.Logger: 日志记录器实例
        """
        return self.get_logger(f"pdf_processor.{module_name}")


# 全局日志管理器实例
logger_manager = LoggerManager()


def get_logger(name="pdf_processor"):
    """
    获取日志记录器的便捷函数
    
    Args:
        name (str): 日志记录器名称
        
    Returns:
        logging.Logger: 日志记录器实例
    """
    return logger_manager.get_logger(name)


def get_module_logger(module_name):
    """
    获取模块日志记录器的便捷函数
    
    Args:
        module_name (str): 模块名称
        
    Returns:
        logging.Logger: 日志记录器实例
    """
    return logger_manager.get_logger_for_module(module_name)