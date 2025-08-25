#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PDF处理器初始化文件
"""

# 版本信息
__version__ = '1.0.0'

# 核心模块导出
from .core.pdf_engine import PDFEngine
from .core.conversion import ConversionEngine
from .core.editor import EditorEngine
from .core.forms import FormEngine
from .core.security import SecurityEngine
from .core.ocr import OCREngine
from .core.optimization import OptimizationEngine
from .core.comparison import ComparisonEngine
from .core.analytics import AnalyticsEngine
from .core.batch_processor import BatchProcessor

# 工具模块导出
from .utils.cache import CacheManager
from .utils.logger import LoggerManager
from .utils.file_handler import FileHandler
from .utils.validators import Validator
from .utils.performance_monitor import PerformanceMonitor

# 配置模块导出
from .config.settings import SettingsManager

# UI模块导出
from .ui.main_window import MainWindow

__all__ = [
    'PDFEngine',
    'ConversionEngine', 
    'EditorEngine',
    'FormEngine',
    'SecurityEngine',
    'OCREngine',
    'OptimizationEngine',
    'ComparisonEngine',
    'AnalyticsEngine',
    'BatchProcessor',
    'CacheManager',
    'LoggerManager',
    'FileHandler',
    'Validator',
    'PerformanceMonitor',
    'SettingsManager',
    'MainWindow'
]