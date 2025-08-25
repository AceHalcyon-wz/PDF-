#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
统一接口模块
定义各模块之间的标准接口和通信方式

更新状态:
- pdf_engine: 已完全实现ModuleInterface
- editor: 已完全实现ModuleInterface
- conversion: 已完全实现ModuleInterface
- security: 已完全实现ModuleInterface
- ocr: 已完全实现ModuleInterface
- optimization: 已完全实现ModuleInterface
- forms: 已完全实现ModuleInterface
- comparison: 已完全实现ModuleInterface
- analytics: 已完全实现ModuleInterface
- interface: 核心接口定义
- exceptions: 异常处理
- cloud_integration: 新增模块，正在实现ModuleInterface
- ai_features: 新增模块，正在实现ModuleInterface
"""

from typing import Dict, Any, Callable, Optional
from core.exceptions import PDFProcessorError
from utils.logger import get_module_logger

logger = get_module_logger("interface")


class ModuleInterface:
    """模块接口基类"""
    
    def __init__(self, module_name: str):
        """
        初始化模块接口
        
        Args:
            module_name (str): 模块名称
        """
        self.module_name = module_name
        self.logger = get_module_logger(module_name)
        self.callbacks = {}
        
    def register_callback(self, event_name: str, callback: Callable) -> None:
        """
        注册回调函数
        
        Args:
            event_name (str): 事件名称
            callback (Callable): 回调函数
        """
        if event_name not in self.callbacks:
            self.callbacks[event_name] = []
        self.callbacks[event_name].append(callback)
        
    def trigger_event(self, event_name: str, data: Dict[str, Any] = None) -> None:
        """
        触发事件
        
        Args:
            event_name (str): 事件名称
            data (Dict[str, Any]): 事件数据
        """
        if event_name in self.callbacks:
            for callback in self.callbacks[event_name]:
                try:
                    callback(data or {})
                except Exception as e:
                    self.logger.error(f"执行回调函数时出错: {str(e)}")
                    
    def log_info(self, message: str) -> None:
        """
        记录信息日志
        
        Args:
            message (str): 日志消息
        """
        self.logger.info(f"[{self.module_name}] {message}")
        
    def log_error(self, message: str) -> None:
        """
        记录错误日志
        
        Args:
            message (str): 错误消息
        """
        self.logger.error(f"[{self.module_name}] {message}")
        
    def log_debug(self, message: str) -> None:
        """
        记录调试日志
        
        Args:
            message (str): 调试消息
        """
        self.logger.debug(f"[{self.module_name}] {message}")


class ProcessingContext:
    """处理上下文，用于在模块间传递处理信息"""
    
    def __init__(self):
        """初始化处理上下文"""
        self.data = {}
        self.metadata = {}
        self.errors = []
        
    def set_data(self, key: str, value: Any) -> None:
        """
        设置数据
        
        Args:
            key (str): 数据键
            value (Any): 数据值
        """
        self.data[key] = value
        
    def get_data(self, key: str, default: Any = None) -> Any:
        """
        获取数据
        
        Args:
            key (str): 数据键
            default (Any): 默认值
            
        Returns:
            Any: 数据值
        """
        return self.data.get(key, default)
        
    def set_metadata(self, key: str, value: Any) -> None:
        """
        设置元数据
        
        Args:
            key (str): 元数据键
            value (Any): 元数据值
        """
        self.metadata[key] = value
        
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        获取元数据
        
        Args:
            key (str): 元数据键
            default (Any): 默认值
            
        Returns:
            Any: 元数据值
        """
        return self.metadata.get(key, default)
        
    def add_error(self, error: str) -> None:
        """
        添加错误信息
        
        Args:
            error (str): 错误信息
        """
        self.errors.append(error)
        
    def has_errors(self) -> bool:
        """
        检查是否有错误
        
        Returns:
            bool: 是否有错误
        """
        return len(self.errors) > 0
        
    def get_errors(self) -> list:
        """
        获取错误列表
        
        Returns:
            list: 错误列表
        """
        return self.errors.copy()


def standard_progress_callback(progress: int, message: str = "") -> None:
    """
    标准进度回调函数
    
    Args:
        progress (int): 进度值(0-100)
        message (str): 进度消息
    """
    # 这是一个示例函数，实际使用时会被替换为具体的实现
    logger = get_module_logger("progress")
    logger.debug(f"进度: {progress}%, 消息: {message}")


def standard_result_handler(result: Dict[str, Any]) -> None:
    """
    标准结果处理函数
    
    Args:
        result (Dict[str, Any]): 处理结果
    """
    logger = get_module_logger("result")
    logger.debug(f"处理结果: {result}")


# 定义标准的模块接口
STANDARD_MODULE_INTERFACES = {
    "pdf_engine": ["split_pdf", "merge_pdfs", "compress_pdf", "rotate_pages"],
    "conversion": ["pdf_to_text", "pdf_to_image", "image_to_pdf", "pdf_to_word"],
    "editor": ["delete_pages", "insert_pages", "replace_pages", "reorder_pages"],
    "security": ["encrypt_pdf", "decrypt_pdf", "add_watermark", "digital_signature"],
    "ocr": ["ocr_pdf", "batch_ocr"],
    "optimization": ["optimize_pdf", "compress_images"],
    "comparison": ["compare_pdfs", "visual_diff"],
    "analytics": ["get_document_info", "generate_report"],
    "forms": ["fill_form", "extract_form_data", "validate_form"],
}