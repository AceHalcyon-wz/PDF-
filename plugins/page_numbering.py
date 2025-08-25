#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
页面编号插件模块
"""

import os
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
from plugins.plugin_interface import PluginInterface, PluginInfo


class PageNumberingPlugin(PluginInterface):
    """页面编号插件类"""

    def __init__(self):
        """初始化页面编号插件"""
        super().__init__()
        self.name = "PageNumberingPlugin"
        self.version = "1.0.0"
        self.description = "PDF页面编号添加插件"

    def add_page_numbers(self, input_path, output_path, position="bottom_right", start_number=1):
        """
        添加页面编号
        
        Args:
            input_path (str): 输入PDF文件路径
            output_path (str): 输出PDF文件路径
            position (str): 编号位置 ("top_left", "top_center", "top_right", 
                           "bottom_left", "bottom_center", "bottom_right")
            start_number (int): 起始编号
        """
        try:
            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            # 读取输入PDF
            reader = PdfReader(input_path)
            
            # 创建输出PDF写入器
            writer = PdfWriter()
            
            # 为每一页添加页面编号
            for i, page in enumerate(reader.pages):
                page_num = start_number + i
                
                # 创建页面编号PDF
                packet = io.BytesIO()
                can = canvas.Canvas(packet, pagesize=letter)
                width = letter[0]
                height = letter[1]
                
                # 根据位置设置坐标
                x, y = self._get_position_coordinates(position, width, height)
                
                # 绘制页面编号
                can.drawString(x, y, str(page_num))
                can.save()
                
                # 将页面编号移到页面上
                packet.seek(0)
                page_number_pdf = PdfReader(packet)
                page_number_page = page_number_pdf.pages[0]
                
                # 合并页面
                page.merge_page(page_number_page)
                
                # 添加到输出PDF
                writer.add_page(page)
            
            # 保存输出PDF
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
                
            return True
        except Exception as e:
            raise Exception(f"添加页面编号失败: {str(e)}")

    def _get_position_coordinates(self, position, width, height):
        """
        根据位置获取坐标
        
        Args:
            position (str): 位置字符串
            width (float): 页面宽度
            height (float): 页面高度
            
        Returns:
            tuple: (x, y) 坐标
        """
        margin = 50
        
        positions = {
            "top_left": (margin, height - margin),
            "top_center": (width / 2, height - margin),
            "top_right": (width - margin, height - margin),
            "bottom_left": (margin, margin),
            "bottom_center": (width / 2, margin),
            "bottom_right": (width - margin, margin)
        }
        
        return positions.get(position, positions["bottom_right"])

    def get_info(self):
        """
        获取插件信息
        
        Returns:
            dict: 插件信息
        """
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description
        }