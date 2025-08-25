#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PDF水印插件模块
"""

import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.colors import red, blue, yellow, black, white
from reportlab.lib.units import inch
from pypdf import PdfReader, PdfWriter
import io


class WatermarkPlugin:
    """PDF水印插件类"""

    def add_watermark(self, input_path, output_path, watermark_text, font_size=48, angle=45):
        """
        为PDF添加水印
        
        Args:
            input_path (str): 输入PDF文件路径
            output_path (str): 输出PDF文件路径
            watermark_text (str): 水印文本
            font_size (int): 字体大小
            angle (int): 水印旋转角度
        """
        try:
            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            # 创建水印PDF
            watermark_pdf = self._create_text_watermark(watermark_text, font_size, angle)
            
            # 读取原始PDF
            reader = PdfReader(input_path)
            writer = PdfWriter()
            
            # 为每一页添加水印
            for page in reader.pages:
                page.merge_page(watermark_pdf.pages[0])
                writer.add_page(page)
            
            # 保存添加水印后的PDF
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
                
            return True
        except Exception as e:
            raise Exception(f"添加水印失败: {str(e)}")

    def _create_text_watermark(self, text, font_size=48, angle=45):
        """
        创建文本水印PDF
        
        Args:
            text (str): 水印文本
            font_size (int): 字体大小
            angle (int): 旋转角度
            
        Returns:
            PdfWriter: 水印PDF对象
        """
        # 创建一个内存中的PDF文件
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=A4)
        
        # 设置字体和颜色
        can.setFont("Helvetica", font_size)
        can.setFillColorRGB(0.5, 0.5, 0.5, alpha=0.3)  # 半透明灰色
        
        # 计算页面中心
        width, height = A4
        center_x = width / 2
        center_y = height / 2
        
        # 保存当前状态
        can.saveState()
        
        # 移动到中心点并旋转
        can.translate(center_x, center_y)
        can.rotate(angle)
        
        # 绘制文本（在旋转后的坐标系中）
        text_width = can.stringWidth(text, "Helvetica", font_size)
        can.drawString(-text_width/2, -font_size/2, text)
        
        # 恢复状态
        can.restoreState()
        
        # 保存PDF
        can.save()
        
        # 将内存中的PDF转换为可读取的对象
        packet.seek(0)
        watermark_pdf = PdfReader(packet)
        
        return watermark_pdf

    def add_image_watermark(self, input_path, output_path, image_path, opacity=0.5):
        """
        为PDF添加图片水印
        
        Args:
            input_path (str): 输入PDF文件路径
            output_path (str): 输出PDF文件路径
            image_path (str): 水印图片路径
            opacity (float): 水印透明度 (0-1)
        """
        try:
            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            # 创建图片水印PDF
            watermark_pdf = self._create_image_watermark(image_path, opacity)
            
            # 读取原始PDF
            reader = PdfReader(input_path)
            writer = PdfWriter()
            
            # 为每一页添加水印
            for page in reader.pages:
                page.merge_page(watermark_pdf.pages[0])
                writer.add_page(page)
            
            # 保存添加水印后的PDF
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
                
            return True
        except Exception as e:
            raise Exception(f"添加图片水印失败: {str(e)}")

    def _create_image_watermark(self, image_path, opacity=0.5):
        """
        创建图片水印PDF
        
        Args:
            image_path (str): 水印图片路径
            opacity (float): 水印透明度
            
        Returns:
            PdfWriter: 水印PDF对象
        """
        # 创建一个内存中的PDF文件
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=A4)
        
        # 计算页面中心
        width, height = A4
        center_x = width / 2
        center_y = height / 2
        
        # 加载图片并计算尺寸
        try:
            from PIL import Image
            img = Image.open(image_path)
            img_width, img_height = img.size
            
            # 计算缩放比例，使图片适应页面
            scale = min(width / img_width, height / img_height) * 0.5  # 缩放到页面的50%
            draw_width = img_width * scale
            draw_height = img_height * scale
            
            # 设置透明度
            can.setFillAlpha(opacity)
            
            # 绘制图片
            can.drawImage(
                image_path, 
                center_x - draw_width/2, 
                center_y - draw_height/2, 
                width=draw_width, 
                height=draw_height
            )
            
            # 恢复透明度
            can.setFillAlpha(1)
        except Exception as e:
            raise Exception(f"加载水印图片失败: {str(e)}")
        
        # 保存PDF
        can.save()
        
        # 将内存中的PDF转换为可读取的对象
        packet.seek(0)
        watermark_pdf = PdfReader(packet)
        
        return watermark_pdf