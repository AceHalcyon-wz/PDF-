#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
插件接口定义模块
定义了所有插件需要实现的标准接口
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Any, Optional


class PluginLifeCycle(Enum):
    """插件生命周期阶段"""
    LOADED = "loaded"
    INITIALIZED = "initialized"
    ENABLED = "enabled"
    DISABLED = "disabled"
    UNLOADED = "unloaded"


class PluginInfo:
    """插件信息类"""
    def __init__(self, name: str, version: str, description: str, author: str = "",
                 website: str = "", license: str = ""):
        self.name = name
        self.version = version
        self.description = description
        self.author = author
        self.website = website
        self.license = license


class PluginInterface(ABC):
    """插件接口抽象基类"""

    def __init__(self):
        """初始化插件"""
        self._lifecycle_state = PluginLifeCycle.LOADED
        self._is_enabled = False

    @abstractmethod
    def get_info(self) -> PluginInfo:
        """
        获取插件信息
        
        Returns:
            PluginInfo: 插件信息对象
        """
        pass

    def on_load(self) -> None:
        """
        插件加载时调用
        在插件被加载后立即调用，用于执行一次性初始化操作
        """
        self._lifecycle_state = PluginLifeCycle.LOADED

    def on_initialize(self) -> None:
        """
        插件初始化时调用
        在插件被初始化时调用，用于执行初始化操作
        """
        self._lifecycle_state = PluginLifeCycle.INITIALIZED

    def on_enable(self) -> None:
        """
        插件启用时调用
        在插件被启用时调用
        """
        self._is_enabled = True
        self._lifecycle_state = PluginLifeCycle.ENABLED

    def on_disable(self) -> None:
        """
        插件禁用时调用
        在插件被禁用时调用
        """
        self._is_enabled = False
        self._lifecycle_state = PluginLifeCycle.DISABLED

    def on_unload(self) -> None:
        """
        插件卸载时调用
        在插件被卸载前调用，用于执行清理操作
        """
        self._lifecycle_state = PluginLifeCycle.UNLOADED

    def get_lifecycle_state(self) -> PluginLifeCycle:
        """
        获取插件生命周期状态
        
        Returns:
            PluginLifeCycle: 插件生命周期状态
        """
        return self._lifecycle_state

    def is_enabled(self) -> bool:
        """
        检查插件是否启用
        
        Returns:
            bool: 插件是否启用
        """
        return self._is_enabled

    def get_configuration_options(self) -> Dict[str, Any]:
        """
        获取插件配置选项
        
        Returns:
            Dict[str, Any]: 配置选项字典
        """
        return {}

    def set_configuration_option(self, key: str, value: Any) -> bool:
        """
        设置插件配置选项
        
        Args:
            key (str): 配置项键名
            value (Any): 配置项值
            
        Returns:
            bool: 是否设置成功
        """
        return False

    def get_menu_items(self) -> List[Dict[str, Any]]:
        """
        获取插件菜单项
        
        Returns:
            List[Dict[str, Any]]: 菜单项列表，每个项包含'label'和'callback'键
        """
        return []

    def get_toolbar_items(self) -> List[Dict[str, Any]]:
        """
        获取插件工具栏项
        
        Returns:
            List[Dict[str, Any]]: 工具栏项列表，每个项包含'icon'、'tooltip'和'callback'键
        """
        return []