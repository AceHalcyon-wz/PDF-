#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PDF处理器统一异常处理模块
"""

class PDFProcessorError(Exception):
    """PDF处理器基础异常类"""
    pass


class PDFEngineError(PDFProcessorError):
    """PDF引擎相关异常"""
    pass


class PDFConversionError(PDFProcessorError):
    """PDF转换相关异常"""
    pass


class PDFSecurityError(PDFProcessorError):
    """PDF安全相关异常"""
    pass


class FileOperationError(PDFProcessorError):
    """文件操作相关异常"""
    pass


class PluginError(PDFProcessorError):
    """插件相关异常"""
    pass


class ValidationError(PDFProcessorError):
    """参数验证相关异常"""
    pass