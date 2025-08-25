#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
基础PDF操作引擎（拆分/合并/加密）

这个模块提供了PDF处理的核心功能，包括：
- PDF拆分（按页数、按范围、首页与末页配对）
- PDF合并
- PDF页面操作

接口状态: 已完全符合统一接口标准ModuleInterface
"""

import os
import pypdf
from pypdf import PdfReader, PdfWriter
from core.exceptions import PDFEngineError
from utils.performance_monitor import monitor_performance, performance_monitor, LRUCache
from utils.logger import get_module_logger
from core.interface import ModuleInterface, ProcessingContext

logger = get_module_logger("pdf_engine")


class PDFEngine(ModuleInterface):
    """基础PDF操作引擎类"""

    def __init__(self):
        """初始化PDF引擎"""
        super().__init__("pdf_engine")
        self.cache = LRUCache(100)  # 使用LRU缓存替代简单字典
        self.log_info("PDF引擎初始化完成")

    @monitor_performance("get_page_count")
    def _get_page_count(self, input_path):
        """获取PDF页数（带缓存）"""
        cache_key = f"page_count:{input_path}"
        cached_result = self.cache.get(cache_key)
        if cached_result is not None:
            self.log_debug(f"从缓存获取页数: {input_path} = {cached_result}")
            return cached_result
        
        try:
            with open(input_path, 'rb') as file:
                reader = PdfReader(file)
                count = len(reader.pages)
                # 更新缓存
                self.cache.put(cache_key, count)
                self.log_debug(f"计算并缓存页数: {input_path} = {count}")
                return count
        except Exception as e:
            self.log_error(f"无法获取PDF页数: {str(e)}")
            raise PDFEngineError(f"无法获取PDF页数: {str(e)}")

    @monitor_performance("split_pdf")
    def split_pdf(self, input_path: str, output_dir: str, pages_per_file=10, **kwargs) -> list:
        """
        按页数拆分PDF文件
        
        Args:
            input_path (str): 输入PDF文件路径
            output_dir (str): 输出目录路径
            pages_per_file (int): 每个拆分文件的页数
            **kwargs: 其他参数
                - progress_callback (callable): 进度回调函数
                
        Returns:
            list: 拆分后的文件路径列表
        """
        try:
            self.log_info(f"开始拆分PDF: {input_path}")
            
            # 确保输出目录存在
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            with open(input_path, 'rb') as file:
                reader = PdfReader(file)
                total_pages = len(reader.pages)
                
                # 计算拆分份数
                num_files = (total_pages + pages_per_file - 1) // pages_per_file
                output_files = []
                
                progress_callback = kwargs.get("progress_callback")
                
                for i in range(num_files):
                    if self.should_cancel():
                        raise PDFEngineError("操作被用户取消")
                        
                    writer = PdfWriter()
                    start_page = i * pages_per_file
                    end_page = min((i + 1) * pages_per_file, total_pages)
                    
                    # 添加页面到新PDF
                    for page_num in range(start_page, end_page):
                        writer.add_page(reader.pages[page_num])
                    
                    # 生成输出文件名
                    base_name = os.path.splitext(os.path.basename(input_path))[0]
                    output_filename = f"{base_name}_part_{i+1:03d}.pdf"
                    output_path = os.path.join(output_dir, output_filename)
                    
                    # 写入文件
                    with open(output_path, 'wb') as output_file:
                        writer.write(output_file)
                    
                    output_files.append(output_path)
                    self.log_debug(f"已拆分: {output_path} ({start_page+1}-{end_page})")
                    
                    # 进度反馈
                    if progress_callback:
                        progress_callback(int((i + 1) / num_files * 100))
                    
            self.log_info(f"PDF拆分完成，共生成 {len(output_files)} 个文件")
            return output_files
        except Exception as e:
            self.log_error(f"PDF拆分失败: {str(e)}")
            raise PDFEngineError(f"PDF拆分失败: {str(e)}")

    def _parse_page_ranges(self, ranges_str: str) -> list:
        """解析页码范围字符串为列表"""
        ranges = []
        for range_part in ranges_str.split(','):
            range_part = range_part.strip()
            if '-' in range_part:
                start, end = map(int, range_part.split('-'))
                ranges.append((start, end))
            else:
                page = int(range_part)
                ranges.append((page, page))
        return ranges

    def _split_by_page_count(self, reader: PdfReader, output_dir: str, page_count: int, 
                           total_pages: int, input_path: str, progress_callback=None) -> list:
        """按页数拆分"""
        output_files = []
        file_index = 1
        total_splits = (total_pages + page_count - 1) // page_count
        
        for i, start_page in enumerate(range(0, total_pages, page_count)):
            end_page = min(start_page + page_count, total_pages)
            writer = PdfWriter()
            
            for page_num in range(start_page, end_page):
                writer.add_page(reader.pages[page_num])
            
            output_path = self._generate_output_path(input_path, output_dir, "part", file_index)
            self._write_pdf(writer, output_path)
            output_files.append(output_path)
            
            # 进度反馈
            if progress_callback:
                progress_callback(int((i + 1) / total_splits * 100))
                
        return output_files

    @monitor_performance("split_pdf_by_ranges")
    def split_pdf_by_ranges(self, input_path, output_dir, page_ranges, **kwargs):
        """
        按页面范围拆分PDF文件
        
        Args:
            input_path (str): 输入PDF文件路径
            output_dir (str): 输出目录路径
            page_ranges (list): 页面范围列表，每个元素为(start, end)元组
            **kwargs: 其他参数
                - progress_callback (callable): 进度回调函数
                
        Returns:
            list: 拆分后的文件路径列表
        """
        try:
            self.log_info(f"开始按范围拆分PDF: {input_path}")
            
            # 确保输出目录存在
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            with open(input_path, 'rb') as file:
                reader = PdfReader(file)
                total_pages = len(reader.pages)
                output_files = []
                
                progress_callback = kwargs.get("progress_callback")
                
                for i, (start_page, end_page) in enumerate(page_ranges):
                    if self.should_cancel():
                        raise PDFEngineError("操作被用户取消")
                        
                    # 验证页码范围
                    if start_page < 1 or end_page > total_pages or start_page > end_page:
                        raise PDFEngineError(f"无效的页码范围: {start_page}-{end_page}")
                    
                    writer = PdfWriter()
                    
                    # 添加页面到新PDF (注意: pypdf使用0索引)
                    for page_num in range(start_page-1, end_page):
                        writer.add_page(reader.pages[page_num])
                    
                    # 生成输出文件名
                    base_name = os.path.splitext(os.path.basename(input_path))[0]
                    output_filename = f"{base_name}_range_{start_page:03d}-{end_page:03d}.pdf"
                    output_path = os.path.join(output_dir, output_filename)
                    
                    # 写入文件
                    with open(output_path, 'wb') as output_file:
                        writer.write(output_file)
                    
                    output_files.append(output_path)
                    self.log_debug(f"已拆分: {output_path} ({start_page}-{end_page})")
                    
                    # 进度反馈
                    if progress_callback:
                        progress_callback(int((i + 1) / len(page_ranges) * 100))
                    
            self.log_info(f"PDF按范围拆分完成，共生成 {len(output_files)} 个文件")
            return output_files
        except Exception as e:
            self.log_error(f"PDF按范围拆分失败: {str(e)}")
            raise PDFEngineError(f"PDF按范围拆分失败: {str(e)}")

    @monitor_performance("split_pdf_pair_mode")
    def split_pdf_pair_mode(self, input_path, output_dir, **kwargs):
        """
        首页与末页配对拆分PDF文件
        
        Args:
            input_path (str): 输入PDF文件路径
            output_dir (str): 输出目录路径
            **kwargs: 其他参数
                - progress_callback (callable): 进度回调函数
                
        Returns:
            list: 拆分后的文件路径列表
        """
        try:
            self.log_info(f"开始配对拆分PDF: {input_path}")
            
            # 确保输出目录存在
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            with open(input_path, 'rb') as file:
                reader = PdfReader(file)
                total_pages = len(reader.pages)
                
                if total_pages % 2 != 0:
                    raise PDFEngineError("配对模式要求PDF页数为偶数")
                
                num_pairs = total_pages // 2
                output_files = []
                
                progress_callback = kwargs.get("progress_callback")
                
                for i in range(num_pairs):
                    if self.should_cancel():
                        raise PDFEngineError("操作被用户取消")
                        
                    writer = PdfWriter()
                    # 首页
                    writer.add_page(reader.pages[i])
                    # 末页
                    writer.add_page(reader.pages[total_pages - 1 - i])
                    
                    # 生成输出文件名
                    base_name = os.path.splitext(os.path.basename(input_path))[0]
                    output_filename = f"{base_name}_pair_{i+1:03d}.pdf"
                    output_path = os.path.join(output_dir, output_filename)
                    
                    # 写入文件
                    with open(output_path, 'wb') as output_file:
                        writer.write(output_file)
                    
                    output_files.append(output_path)
                    self.log_debug(f"已拆分: {output_path}")
                    
                    # 进度反馈
                    if progress_callback:
                        progress_callback(int((i + 1) / num_pairs * 100))
                    
            self.log_info(f"PDF配对拆分完成，共生成 {len(output_files)} 个文件")
            return output_files
        except Exception as e:
            self.log_error(f"PDF配对拆分失败: {str(e)}")
            raise PDFEngineError(f"PDF配对拆分失败: {str(e)}")

    def _generate_output_path(self, input_path: str, output_dir: str, suffix_type: str, index: int) -> str:
        """生成输出文件路径"""
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        return os.path.join(output_dir, f"{base_name}_{suffix_type}_{index}.pdf")

    def _write_pdf(self, writer: PdfWriter, output_path: str) -> None:
        """写入PDF文件"""
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)

    @monitor_performance("merge_pdfs")
    def merge_pdfs(self, input_paths, output_path, **kwargs):
        """
        合并多个PDF文件
        
        Args:
            input_paths (list): 要合并的PDF文件路径列表
            output_path (str): 输出PDF文件路径
            **kwargs: 其他参数
                - progress_callback (callable): 进度回调函数
                
        Returns:
            bool: 合并是否成功
        """
        try:
            self.log_info(f"开始合并PDF，共 {len(input_paths)} 个文件")
            
            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            writer = PdfWriter()
            
            total_files = len(input_paths)
            progress_callback = kwargs.get("progress_callback")
            
            for i, pdf_path in enumerate(input_paths):
                if self.should_cancel():
                    raise PDFEngineError("操作被用户取消")
                    
                if not os.path.exists(pdf_path):
                    raise PDFEngineError(f"文件不存在: {pdf_path}")
                
                with open(pdf_path, 'rb') as file:
                    reader = PdfReader(file)
                    for page in reader.pages:
                        writer.add_page(page)
                        
                self.log_debug(f"已添加文件: {pdf_path}")
                
                # 进度反馈
                if progress_callback:
                    progress_callback(int((i + 1) / total_files * 100))
            
            # 写入合并后的文件
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            self.log_info(f"PDF合并完成: {output_path}")
            return True
        except Exception as e:
            self.log_error(f"PDF合并失败: {str(e)}")
            raise PDFEngineError(f"PDF合并失败: {str(e)}")

    @monitor_performance("compress_pdf")
    def compress_pdf(self, input_path, output_path, compression_level="normal", progress_callback=None):
        """
        压缩PDF文件
        
        Args:
            input_path (str): 输入PDF文件路径
            output_path (str): 输出PDF文件路径
            compression_level (str): 压缩级别 ("low", "normal", "high")
            progress_callback (callable): 进度回调函数
        """
        self.log_info(f"开始压缩PDF: {input_path}")
        try:
            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            with open(input_path, 'rb') as input_file:
                reader = PdfReader(input_file)
                writer = PdfWriter()
                
                # 复制所有页面
                for i, page in enumerate(reader.pages):
                    writer.add_page(page)
                    
                    # 进度反馈
                    if progress_callback:
                        progress_callback(int((i + 1) / len(reader.pages) * 100))
                
                # 保存压缩后的PDF
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
                    
            self.log_info(f"PDF压缩完成: {output_path}")
            return True
        except Exception as e:
            self.log_error(f"PDF压缩失败: {str(e)}")
            raise PDFEngineError(f"PDF压缩失败: {str(e)}")