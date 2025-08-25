#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PDF处理器插件模块初始化文件
"""

# 插件模块导出
from .plugin_loader import PluginLoader
from .watermark import WatermarkPlugin
from .page_numbering import PageNumberingPlugin

__all__ = [
    'PluginLoader',
    'WatermarkPlugin',
    'PageNumberingPlugin'
]