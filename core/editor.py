#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PDF编辑功能模块

接口状态: 已更新以符合统一接口标准ModuleInterface
更新内容:
1. 继承ModuleInterface基类
2. 使用标准日志记录方法
3. 实现标准接口方法
"""

import os
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, ArrayObject
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.colors import red, blue, yellow, black, white
import io
from core.interface import ModuleInterface


class EditorEngine(ModuleInterface):
    """PDF编辑引擎类"""

    def __init__(self):
        """初始化编辑引擎"""
        super().__init__("editor")
        self.log_info("编辑引擎初始化完成")

    def delete_pages(self, input_path, output_path, page_numbers):
        """
        删除PDF页面
        
        Args:
            input_path (str): 输入PDF文件路径
            output_path (str): 输出PDF文件路径
            page_numbers (list): 要删除的页面号列表（从1开始）
        """
        try:
            self.log_info(f"开始删除PDF页面: {input_path}, 删除页面: {page_numbers}")
            
            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            reader = PdfReader(input_path)
            writer = PdfWriter()
            
            total_pages = len(reader.pages)
            
            # 验证页面号
            for page_num in page_numbers:
                if page_num < 1 or page_num > total_pages:
                    raise ValueError(f"无效的页面号: {page_num}")
            
            # 复制未删除的页面
            for i in range(total_pages):
                page_num = i + 1
                if page_num not in page_numbers:
                    writer.add_page(reader.pages[i])
            
            # 保存结果
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
                
            self.log_info(f"页面删除成功: {output_path}")
        except Exception as e:
            self.log_error(f"页面删除失败: {str(e)}")
            raise Exception(f"页面删除失败: {str(e)}")

    def insert_pages(self, target_path, insert_path, output_path, position):
        """
        在指定位置插入页面
        
        Args:
            target_path (str): 目标PDF文件路径
            insert_path (str): 要插入的PDF文件路径
            output_path (str): 输出PDF文件路径
            position (int): 插入位置（从1开始）
        """
        try:
            self.log_info(f"开始插入页面: {insert_path} 到 {target_path} 的第 {position} 页")
            
            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            # 读取目标PDF
            target_reader = PdfReader(target_path)
            target_pages = len(target_reader.pages)
            
            # 验证插入位置
            if position < 1 or position > target_pages + 1:
                raise ValueError(f"无效的插入位置: {position}")
            
            # 读取要插入的PDF
            insert_reader = PdfReader(insert_path)
            
            # 创建写入器
            writer = PdfWriter()
            
            # 添加插入位置之前的页面
            for i in range(position - 1):
                writer.add_page(target_reader.pages[i])
                
            # 添加要插入的页面
            for page in insert_reader.pages:
                writer.add_page(page)
                
            # 添加插入位置之后的页面
            for i in range(position - 1, target_pages):
                writer.add_page(target_reader.pages[i])
            
            # 保存结果
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
                
            self.log_info(f"页面插入成功: {output_path}")
        except Exception as e:
            self.log_error(f"页面插入失败: {str(e)}")
            raise Exception(f"页面插入失败: {str(e)}")

    def replace_pages(self, target_path, replacement_path, output_path, page_numbers):
        """
        替换指定页面
        
        Args:
            target_path (str): 目标PDF文件路径
            replacement_path (str): 替换用的PDF文件路径
            output_path (str): 输出PDF文件路径
            page_numbers (list): 要替换的页面号列表（从1开始）
        """
        try:
            self.log_info(f"开始替换页面: 使用 {replacement_path} 替换 {target_path} 的页面 {page_numbers}")
            
            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            # 读取目标PDF
            target_reader = PdfReader(target_path)
            target_pages = len(target_reader.pages)
            
            # 验证页面号
            for page_num in page_numbers:
                if page_num < 1 or page_num > target_pages:
                    raise ValueError(f"无效的页面号: {page_num}")
            
            # 读取替换用的PDF
            replacement_reader = PdfReader(replacement_path)
            replacement_pages = len(replacement_reader.pages)
            
            if replacement_pages != len(page_numbers):
                self.log_warning(f"替换页面数({replacement_pages})与目标页面数({len(page_numbers)})不匹配")
            
            # 创建写入器
            writer = PdfWriter()
            
            # 添加页面，替换指定页面
            replacement_index = 0
            for i in range(target_pages):
                page_num = i + 1
                if page_num in page_numbers and replacement_index < replacement_pages:
                    # 使用替换页面
                    writer.add_page(replacement_reader.pages[replacement_index])
                    replacement_index += 1
                    self.log_debug(f"已替换页面: {page_num}")
                else:
                    # 使用原页面
                    writer.add_page(target_reader.pages[i])
            
            # 保存结果
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
                
            self.log_info(f"页面替换成功: {output_path}")
        except Exception as e:
            self.log_error(f"页面替换失败: {str(e)}")
            raise Exception(f"页面替换失败: {str(e)}")

    def reorder_pages(self, input_path, output_path, new_order):
        """
        重新排序页面
        
        Args:
            input_path (str): 输入PDF文件路径
            output_path (str): 输出PDF文件路径
            new_order (list): 新的页面顺序列表（从1开始）
        """
        try:
            self.log_info(f"开始重排序页面: {input_path}")
            
            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            # 读取PDF
            reader = PdfReader(input_path)
            total_pages = len(reader.pages)
            
            # 验证新顺序
            if len(new_order) != total_pages:
                raise ValueError(f"新顺序页面数({len(new_order)})与原页面数({total_pages})不匹配")
            
            for page_num in new_order:
                if page_num < 1 or page_num > total_pages:
                    raise ValueError(f"无效的页面号: {page_num}")
            
            # 创建写入器
            writer = PdfWriter()
            
            # 按新顺序添加页面
            for page_num in new_order:
                writer.add_page(reader.pages[page_num - 1])  # 转换为0索引
                
            # 保存结果
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
                
            self.log_info(f"页面重排序成功: {output_path}")
        except Exception as e:
            self.log_error(f"页面重排序失败: {str(e)}")
            raise Exception(f"页面重排序失败: {str(e)}")

    def add_watermark(self, input_path, output_path, watermark_text, 
                      font_name="Helvetica", font_size=48, 
                      font_color=red, opacity=0.5):
        """
        添加水印
        
        Args:
            input_path (str): 输入PDF文件路径
            output_path (str): 输出PDF文件路径
            watermark_text (str): 水印文本
            font_name (str): 字体名称
            font_size (int): 字体大小
            font_color: 字体颜色
            opacity (float): 透明度 (0-1)
        """
        try:
            self.log_info(f"开始添加水印: {input_path}")
            
            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            # 创建水印PDF
            watermark_pdf = self._create_text_watermark(
                watermark_text, font_name, font_size, font_color, opacity)
            
            # 读取输入PDF
            reader = PdfReader(input_path)
            
            # 创建写入器
            writer = PdfWriter()
            
            # 为每一页添加水印
            for page in reader.pages:
                page.merge_page(watermark_pdf.pages[0])
                writer.add_page(page)
            
            # 保存结果
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
                
            self.log_info(f"水印添加成功: {output_path}")
        except Exception as e:
            self.log_error(f"水印添加失败: {str(e)}")
            raise Exception(f"水印添加失败: {str(e)}")

    def _create_text_watermark(self, text, font_name="Helvetica", font_size=48, 
                               font_color=red, opacity=0.5):
        """
        创建文本水印PDF
        
        Args:
            text (str): 水印文本
            font_name (str): 字体名称
            font_size (int): 字体大小
            font_color: 字体颜色
            opacity (float): 透明度 (0-1)
            
        Returns:
            PdfWriter: 包含水印的PDF写入器
        """
        # 创建一个内存中的PDF作为水印
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        can.setFont(font_name, font_size)
        can.setFillColor(font_color)
        can.setFillAlpha(opacity)
        
        # 在页面中心添加水印文本
        can.saveState()
        can.translate(letter[0]/2, letter[1]/2)
        can.rotate(45)  # 旋转45度
        can.drawCentredString(0, 0, text)
        can.restoreState()
        
        can.save()
        
        # 将内存中的PDF转换为pypdf对象
        packet.seek(0)
        watermark_pdf = PdfReader(packet)
        
        return watermark_pdf

    def crop_pages(self, input_path, output_path, margins, page_range=None):
        """
        裁剪页面
        
        Args:
            input_path (str): 输入PDF文件路径
            output_path (str): 输出PDF文件路径
            margins (dict): 边距设置 {'left': int, 'right': int, 'top': int, 'bottom': int}
            page_range (str): 页面范围 (例如: "1-3,5,7-10")
        """
        try:
            self.log_info(f"开始裁剪页面: {input_path}")
            
            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            # 读取输入PDF
            reader = PdfReader(input_path)
            writer = PdfWriter()
            
            # 解析页面范围
            pages_to_crop = self._parse_page_range(page_range, len(reader.pages)) if page_range else list(range(len(reader.pages)))
            
            # 处理每一页
            for i, page in enumerate(reader.pages):
                if i in pages_to_crop:
                    # 裁剪页面
                    self._crop_single_page(page, margins)
                writer.add_page(page)
            
            # 保存结果
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
                
            self.log_info(f"页面裁剪成功: {output_path}")
        except Exception as e:
            self.log_error(f"页面裁剪失败: {str(e)}")
            raise Exception(f"页面裁剪失败: {str(e)}")

    def _parse_page_range(self, page_range, total_pages):
        """
        解析页面范围字符串
        
        Args:
            page_range (str): 页面范围字符串 (例如: "1-3,5,7-10")
            total_pages (int): 总页数
            
        Returns:
            list: 页面索引列表
        """
        pages = []
        for part in page_range.split(','):
            part = part.strip()
            if '-' in part:
                start, end = part.split('-')
                start, end = int(start), int(end)
                pages.extend(range(start-1, min(end, total_pages)))  # 转换为0索引
            else:
                page = int(part)
                if page <= total_pages:
                    pages.append(page-1)  # 转换为0索引
        return pages

    def _crop_single_page(self, page, margins):
        """
        裁剪单个页面
        
        Args:
            page (PageObject): 页面对象
            margins (dict): 边距设置 {'left': int, 'right': int, 'top': int, 'bottom': int}
        """
        # 获取页面原始边界框
        original_artbox = page.artbox
        original_bleedbox = page.bleedbox
        original_cropbox = page.cropbox
        original_mediabox = page.mediabox
        original_trimbox = page.trimbox
        
        # 计算新的边界框
        left = original_mediabox.left + margins.get('left', 0)
        right = original_mediabox.right - margins.get('right', 0)
        top = original_mediabox.top - margins.get('top', 0)
        bottom = original_mediabox.bottom + margins.get('bottom', 0)
        
        # 创建新的边界框
        from pypdf.generic import RectangleObject
        new_mediabox = RectangleObject((left, bottom, right, top))
        
        # 应用新的边界框
        page.mediabox = new_mediabox
        page.cropbox = new_mediabox

    def extract_pages(self, input_path, output_path, page_range=""):
        """
        提取页面
        
        Args:
            input_path (str): 输入PDF文件路径
            output_path (str): 输出PDF文件路径
            page_range (str): 页面范围 (例如: "1-3,5,7-10")
        """
        try:
            self.log_info(f"开始提取页面: {input_path}")
            
            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            # 读取输入PDF
            reader = PdfReader(input_path)
            writer = PdfWriter()
            
            # 解析页面范围
            if page_range:
                pages_to_extract = self._parse_page_range(page_range, len(reader.pages))
            else:
                pages_to_extract = list(range(len(reader.pages)))
            
            # 提取指定页面
            for i in pages_to_extract:
                writer.add_page(reader.pages[i])
            
            # 保存结果
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
                
            self.log_info(f"页面提取成功: {output_path}")
        except Exception as e:
            self.log_error(f"页面提取失败: {str(e)}")
            raise Exception(f"页面提取失败: {str(e)}")

    def rotate_pages(self, input_path, output_path, angle, page_range=""):
        """
        旋转页面
        
        Args:
            input_path (str): 输入PDF文件路径
            output_path (str): 输出PDF文件路径
            angle (int): 旋转角度 (90, 180, 270)
            page_range (str): 页面范围 (例如: "1-3,5,7-10")
        """
        try:
            self.log_info(f"开始旋转页面: {input_path}, 角度: {angle}")
            
            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            # 读取输入PDF
            reader = PdfReader(input_path)
            writer = PdfWriter()
            
            # 解析页面范围
            if page_range:
                pages_to_rotate = self._parse_page_range(page_range, len(reader.pages))
            else:
                pages_to_rotate = list(range(len(reader.pages)))
            
            # 处理每一页
            for i, page in enumerate(reader.pages):
                if i in pages_to_rotate:
                    # 旋转页面
                    page.rotate(angle)
                writer.add_page(page)
            
            # 保存结果
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
                
            self.log_info(f"页面旋转成功: {output_path}")
        except Exception as e:
            self.log_error(f"页面旋转失败: {str(e)}")
            raise Exception(f"页面旋转失败: {str(e)}")