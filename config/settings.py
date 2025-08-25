#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
设置管理器模块
"""

import json
import os
from utils.logger import get_module_logger

logger = get_module_logger("config")


class SettingsManager:
    """设置管理器"""

    # 默认配置
    DEFAULT_SETTINGS = {
        "appearance": {
            "theme": "高对比度主题",
            "language": "zh_CN",
            "window_width": 1200,
            "window_height": 800
        },
        "processing": {
            "default_output_dir": "./output",
            "auto_open_output": True,
            "max_recent_files": 10
        },
        "performance": {
            "thread_pool_max_workers": 4,
            "enable_cache": True,
            "cache_size_limit": 100  # MB
        }
    }

    def __init__(self, config_file="./config/settings.json"):
        """
        初始化设置管理器
        
        Args:
            config_file (str): 配置文件路径
        """
        self.config_file = config_file
        self.settings = {}
        self.load_settings()
        logger.info("设置管理器初始化完成")

    def load_settings(self):
        """加载设置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.settings = json.load(f)
                logger.info(f"配置已从 {self.config_file} 加载")
            else:
                # 如果配置文件不存在，使用默认设置
                self.settings = self.get_default_settings()
                self.save_settings()
                logger.info("使用默认配置并已保存")
        except Exception as e:
            logger.error(f"加载配置时出错: {e}")
            self.settings = self.get_default_settings()

    def save_settings(self):
        """保存设置"""
        try:
            # 确保配置目录存在
            config_dir = os.path.dirname(self.config_file)
            if not os.path.exists(config_dir):
                os.makedirs(config_dir)
                
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
            logger.info(f"配置已保存到 {self.config_file}")
        except Exception as e:
            logger.error(f"保存配置时出错: {e}")

    def get_default_settings(self):
        """
        获取默认设置
        
        Returns:
            dict: 默认设置
        """
        return self.DEFAULT_SETTINGS.copy()

    def get(self, key_path, default=None):
        """
        获取配置项的值
        
        Args:
            key_path (str): 配置项路径，如 "appearance.theme"
            default: 默认值
            
        Returns:
            配置项的值
        """
        keys = key_path.split('.')
        value = self.settings
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key_path, value):
        """
        设置配置项的值
        
        Args:
            key_path (str): 配置项路径，如 "appearance.theme"
            value: 配置项的值
        """
        keys = key_path.split('.')
        settings = self.settings
        
        # 导航到倒数第二层
        for key in keys[:-1]:
            if key not in settings:
                settings[key] = {}
            settings = settings[key]
        
        # 设置最后一层的值
        settings[keys[-1]] = value
        
        logger.debug(f"设置配置项 {key_path} = {value}")

    def reset_to_default(self):
        """
        重置为默认设置
        """
        self.settings = self.get_default_settings()
        self.save_settings()
        logger.info("配置已重置为默认值")


# 全局设置管理器实例
settings_manager = SettingsManager()