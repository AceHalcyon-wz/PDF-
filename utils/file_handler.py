#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
文件操作工具模块
"""

import os
import shutil
from pathlib import Path


class FileHandler:
    """文件操作处理器"""

    @staticmethod
    def ensure_directory_exists(directory_path):
        """
        确保目录存在，如果不存在则创建
        
        Args:
            directory_path (str): 目录路径
        """
        Path(directory_path).mkdir(parents=True, exist_ok=True)

    @staticmethod
    def copy_file(src_path, dst_path):
        """
        复制文件
        
        Args:
            src_path (str): 源文件路径
            dst_path (str): 目标文件路径
        """
        shutil.copy2(src_path, dst_path)

    @staticmethod
    def move_file(src_path, dst_path):
        """
        移动文件
        
        Args:
            src_path (str): 源文件路径
            dst_path (str): 目标文件路径
        """
        shutil.move(src_path, dst_path)

    @staticmethod
    def delete_file(file_path):
        """
        删除文件
        
        Args:
            file_path (str): 文件路径
        """
        if os.path.exists(file_path):
            os.remove(file_path)

    @staticmethod
    def get_file_size(file_path):
        """
        获取文件大小
        
        Args:
            file_path (str): 文件路径
            
        Returns:
            int: 文件大小（字节）
        """
        return os.path.getsize(file_path) if os.path.exists(file_path) else 0

    @staticmethod
    def get_file_extension(file_path):
        """
        获取文件扩展名
        
        Args:
            file_path (str): 文件路径
            
        Returns:
            str: 文件扩展名
        """
        return os.path.splitext(file_path)[1].lower()

    @staticmethod
    def is_pdf_file(file_path):
        """
        判断是否为PDF文件
        
        Args:
            file_path (str): 文件路径
            
        Returns:
            bool: 是否为PDF文件
        """
        return FileHandler.get_file_extension(file_path) == '.pdf'