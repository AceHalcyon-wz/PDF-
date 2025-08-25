#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PDF文档比较功能模块

接口状态: 已更新以符合统一接口标准ModuleInterface
更新内容:
1. 继承ModuleInterface基类
2. 使用标准日志记录方法
3. 实现标准接口方法
"""

import os
from pypdf import PdfReader
import json
import cv2
import numpy as np
from PIL import Image
import pdf2image
from core.interface import ModuleInterface


class ComparisonEngine(ModuleInterface):
    """文档比较引擎类"""

    def __init__(self):
        """初始化文档比较引擎"""
        super().__init__("comparison")
        self.log_info("文档比较引擎初始化完成")

    def compare_documents(self, pdf1_path, pdf2_path):
        """
        比较两个PDF文档
        
        Args:
            pdf1_path (str): 第一个PDF文件路径
            pdf2_path (str): 第二个PDF文件路径
            
        Returns:
            dict: 比较结果
        """
        try:
            self.log_info(f"开始比较PDF文档: {pdf1_path} vs {pdf2_path}")
            
            # 读取两个PDF文件
            reader1 = PdfReader(pdf1_path)
            reader2 = PdfReader(pdf2_path)
            
            # 获取基本信息
            page_count1 = len(reader1.pages)
            page_count2 = len(reader2.pages)
            
            # 基本差异比较
            differences = {
                'page_count_different': page_count1 != page_count2,
                'page_count': {
                    'pdf1': page_count1,
                    'pdf2': page_count2
                },
                'metadata_different': reader1.metadata != reader2.metadata,
                'metadata': {
                    'pdf1': dict(reader1.metadata) if reader1.metadata else {},
                    'pdf2': dict(reader2.metadata) if reader2.metadata else {}
                }
            }
            
            # 逐页比较文本内容
            text_differences = []
            min_pages = min(page_count1, page_count2)
            
            for i in range(min_pages):
                page1_text = reader1.pages[i].extract_text()
                page2_text = reader2.pages[i].extract_text()
                
                if page1_text != page2_text:
                    text_differences.append({
                        'page_number': i + 1,
                        'pdf1_text': page1_text[:100] + '...' if len(page1_text) > 100 else page1_text,
                        'pdf2_text': page2_text[:100] + '...' if len(page2_text) > 100 else page2_text
                    })
            
            differences['text_differences'] = text_differences
            differences['extra_pages_in_pdf1'] = page_count1 > page_count2
            differences['extra_pages_in_pdf2'] = page_count2 > page_count1
            
            self.log_info(f"PDF文档比较完成")
            return differences
        except Exception as e:
            self.log_error(f"PDF文档比较失败: {str(e)}")
            raise Exception(f"PDF文档比较失败: {str(e)}")

    def save_report_as_text(self, result, output_path):
        """
        将比较结果保存为文本报告
        
        Args:
            result (dict): 比较结果
            output_path (str): 输出文件路径
        """
        try:
            self.log_info(f"开始保存比较报告为文本: {output_path}")
            
            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("PDF文档比较报告\n")
                f.write("=" * 50 + "\n\n")
                
                f.write(f"页面数量差异: {result['page_count_different']}\n")
                f.write(f"文档1页面数: {result['page_count']['pdf1']}\n")
                f.write(f"文档2页面数: {result['page_count']['pdf2']}\n\n")
                
                f.write(f"元数据差异: {result['metadata_different']}\n")
                f.write("文档1元数据:\n")
                for key, value in result['metadata']['pdf1'].items():
                    f.write(f"  {key}: {value}\n")
                f.write("文档2元数据:\n")
                for key, value in result['metadata']['pdf2'].items():
                    f.write(f"  {key}: {value}\n\n")
                
                f.write("文本内容差异:\n")
                for diff in result['text_differences']:
                    f.write(f"  第{diff['page_number']}页存在差异:\n")
                    f.write(f"    文档1内容: {diff['pdf1_text']}\n")
                    f.write(f"    文档2内容: {diff['pdf2_text']}\n\n")
                
                f.write(f"文档1中额外页面: {result['extra_pages_in_pdf1']}\n")
                f.write(f"文档2中额外页面: {result['extra_pages_in_pdf2']}\n")
            
            self.log_info(f"比较报告保存完成: {output_path}")
        except Exception as e:
            self.log_error(f"保存比较报告失败: {str(e)}")
            raise Exception(f"保存比较报告失败: {str(e)}")

    def save_report_as_pdf(self, result, output_path):
        """
        将比较结果保存为PDF报告
        
        Args:
            result (dict): 比较结果
            output_path (str): 输出文件路径
        """
        try:
            self.log_info(f"开始保存比较报告为PDF: {output_path}")
            
            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            # 创建一个简单的文本报告，然后转换为PDF
            # 这里简化处理，实际项目中可以使用reportlab等库创建更复杂的PDF报告
            
            from pypdf import PdfWriter
            from io import BytesIO
            
            # 创建一个内存中的PDF
            packet = BytesIO()
            
            # 由于缺少直接创建PDF的库，这里简化处理
            # 实际应用中应该使用reportlab等库来创建真正的PDF报告
            raise Exception("PDF报告生成功能需要额外库支持，请安装reportlab库")
            
            self.log_info(f"比较报告保存完成: {output_path}")
        except Exception as e:
            self.log_error(f"保存比较报告失败: {str(e)}")
            raise Exception(f"保存比较报告失败: {str(e)}")
