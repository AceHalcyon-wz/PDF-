#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
插件管理器模块
"""

import os
import importlib.util
from typing import Dict, List, Optional
from plugins.plugin_interface import PluginInterface, PluginInfo, PluginLifeCycle


class PluginLoader:
    """插件加载和管理器"""

    def __init__(self, plugin_dir="./plugins"):
        """
        初始化插件管理器
        
        Args:
            plugin_dir (str): 插件目录路径
        """
        self.plugin_dir = plugin_dir
        self.plugins: Dict[str, PluginInterface] = {}
        self.enabled_plugins = set()
        self.load_plugins()

    def load_plugins(self):
        """加载所有插件"""
        if not os.path.exists(self.plugin_dir):
            return
            
        for filename in os.listdir(self.plugin_dir):
            if filename.endswith(".py") and filename != "__init__.py":
                plugin_name = filename[:-3]  # 移除.py扩展名
                try:
                    self.load_plugin(plugin_name)
                except Exception as e:
                    print(f"加载插件 {plugin_name} 失败: {e}")

    def load_plugin(self, plugin_name: str) -> bool:
        """
        加载插件
        
        Args:
            plugin_name (str): 插件名称
            
        Returns:
            bool: 是否加载成功
        """
        plugin_path = os.path.join(self.plugin_dir, plugin_name + ".py")
        if not os.path.exists(plugin_path):
            print(f"插件文件 {plugin_path} 不存在")
            return False
            
        try:
            # 使用importlib加载插件
            spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 查找插件类（继承自PluginInterface的类）
            plugin_instance = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and issubclass(attr, PluginInterface) and attr != PluginInterface:
                    plugin_instance = attr()
                    break
                    
            if plugin_instance:
                # 调用加载回调
                plugin_instance.on_load()
                
                # 注册插件
                self.plugins[plugin_name] = plugin_instance
                print(f"成功加载插件: {plugin_name}")
                return True
            else:
                print(f"插件 {plugin_name} 中未找到继承自PluginInterface的插件类")
                return False
        except Exception as e:
            print(f"加载插件 {plugin_name} 时发生错误: {e}")
            return False

    def unload_plugin(self, plugin_name: str) -> bool:
        """
        卸载插件
        
        Args:
            plugin_name (str): 插件名称
            
        Returns:
            bool: 是否卸载成功
        """
        if plugin_name in self.plugins:
            plugin = self.plugins[plugin_name]
            try:
                # 调用卸载回调
                plugin.on_unload()
                
                # 从启用列表中移除
                if plugin_name in self.enabled_plugins:
                    self.enabled_plugins.discard(plugin_name)
                
                # 从插件列表中移除
                del self.plugins[plugin_name]
                print(f"成功卸载插件: {plugin_name}")
                return True
            except Exception as e:
                print(f"卸载插件 {plugin_name} 时发生错误: {e}")
                return False
        return False

    def get_plugin(self, plugin_name: str) -> Optional[PluginInterface]:
        """
        获取插件实例
        
        Args:
            plugin_name (str): 插件名称
            
        Returns:
            PluginInterface: 插件实例，如果不存在则返回None
        """
        return self.plugins.get(plugin_name)

    def list_plugins(self) -> List[Dict[str, any]]:
        """
        列出所有插件
        
        Returns:
            list: 插件信息列表
        """
        plugin_list = []
        for name, plugin in self.plugins.items():
            try:
                info = plugin.get_info()
                plugin_info = {
                    "name": info.name,
                    "version": info.version,
                    "description": info.description,
                    "author": info.author,
                    "state": plugin.get_lifecycle_state().value,
                    "enabled": plugin.is_enabled()
                }
            except Exception:
                plugin_info = {
                    "name": name,
                    "version": "未知",
                    "description": "无描述",
                    "author": "未知",
                    "state": "unknown",
                    "enabled": False
                }
            plugin_list.append(plugin_info)
        return plugin_list

    def is_plugin_enabled(self, plugin_name: str) -> bool:
        """
        检查插件是否启用
        
        Args:
            plugin_name (str): 插件名称
            
        Returns:
            bool: 插件是否启用
        """
        return plugin_name in self.enabled_plugins

    def enable_plugin(self, plugin_name: str) -> bool:
        """
        启用插件
        
        Args:
            plugin_name (str): 插件名称
            
        Returns:
            bool: 是否启用成功
        """
        if plugin_name in self.plugins:
            try:
                plugin = self.plugins[plugin_name]
                plugin.on_enable()
                self.enabled_plugins.add(plugin_name)
                return True
            except Exception as e:
                print(f"启用插件 {plugin_name} 时发生错误: {e}")
                return False
        return False

    def disable_plugin(self, plugin_name: str) -> bool:
        """
        禁用插件
        
        Args:
            plugin_name (str): 插件名称
            
        Returns:
            bool: 是否禁用成功
        """
        if plugin_name in self.enabled_plugins:
            try:
                plugin = self.plugins[plugin_name]
                plugin.on_disable()
                self.enabled_plugins.discard(plugin_name)
                return True
            except Exception as e:
                print(f"禁用插件 {plugin_name} 时发生错误: {e}")
                return False
        return False

    def get_enabled_plugins(self) -> List[PluginInterface]:
        """
        获取所有已启用的插件
        
        Returns:
            List[PluginInterface]: 已启用的插件列表
        """
        return [self.plugins[name] for name in self.enabled_plugins if name in self.plugins]

    def get_plugin_info(self, plugin_name: str) -> Optional[PluginInfo]:
        """
        获取插件详细信息
        
        Args:
            plugin_name (str): 插件名称
            
        Returns:
            PluginInfo: 插件信息，如果插件不存在则返回None
        """
        plugin = self.plugins.get(plugin_name)
        if plugin:
            try:
                return plugin.get_info()
            except Exception:
                pass
        return None