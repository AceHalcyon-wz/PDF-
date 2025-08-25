#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PDF优化和压缩功能模块

接口状态: 已更新以符合统一接口标准ModuleInterface
更新内容:
1. 继承ModuleInterface基类
2. 使用标准日志记录方法
3. 实现标准接口方法
"""

import os
import zlib
from pypdf import PdfReader, PdfWriter
from pypdf.generic import DecodedStreamObject, EncodedStreamObject
from PIL import Image
import io
from core.interface import ModuleInterface

# 尝试导入PDF/A转换相关库
try:
    # 注意：PyPDF2不直接支持PDF/A，需要其他库如ghostscript
    import ghostscript
    PDFA_AVAILABLE = True
except ImportError:
    PDFA_AVAILABLE = False


class OptimizationEngine(ModuleInterface):
    """优化引擎类"""

    def __init__(self):
        """初始化优化引擎"""
        super().__init__("optimization")
        self.log_info("优化引擎初始化完成")

    def compress_pdf(self, input_path, output_path, compression_level="medium"):
        """
        PDF文件压缩
        
        Args:
            input_path (str): 输入PDF文件路径
            output_path (str): 输出PDF文件路径
            compression_level (str): 压缩级别 ("low", "medium", "high")
        """
        try:
            self.log_info(f"开始压缩PDF: {input_path}")
            
            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            reader = PdfReader(input_path)
            writer = PdfWriter()
            
            # 根据压缩级别设置参数
            if compression_level == "high":
                # 高压缩级别 - 降低图像质量
                writer.compress_identical_objects()
            
            # 复制所有页面（pypdf会自动进行一定程度的压缩）
            for page in reader.pages:
                writer.add_page(page)
                
            # 保存压缩后的PDF
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
                
            self.log_info(f"PDF压缩完成: {output_path}")
        except Exception as e:
            self.log_error(f"PDF文件压缩失败: {str(e)}")
            raise Exception(f"PDF文件压缩失败: {str(e)}")

    def optimize_images(self, input_path, output_path, quality=85):
        """
        图像优化
        
        Args:
            input_path (str): 输入PDF文件路径
            output_path (str): 输出PDF文件路径
            quality (int): 图像质量（1-100）
        """
        try:
            self.log_info(f"开始优化PDF中的图像: {input_path}")
            
            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            reader = PdfReader(input_path)
            writer = PdfWriter()
            
            # 处理每一页
            for page in reader.pages:
                writer.add_page(page)
                
            # 优化图像对象
            for page in writer.pages:
                for image in page.images:
                    # 获取原始图像
                    image_data = image.data
                    image_obj = Image.open(io.BytesIO(image_data))
                    
                    # 压缩图像
                    output = io.BytesIO()
                    image_obj.save(output, format=image_obj.format, quality=quality, optimize=True)
                    image.replace(output.getvalue())
            
            # 保存优化后的PDF
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
                
            self.log_info(f"PDF图像优化完成: {output_path}")
        except Exception as e:
            self.log_error(f"PDF图像优化失败: {str(e)}")
            raise Exception(f"PDF图像优化失败: {str(e)}")

    def mrc_compress(self, input_path, output_path):
        """
        MRC压缩（混合光栅化内容压缩，适合扫描文档）
        
        Args:
            input_path (str): 输入PDF文件路径
            output_path (str): 输出PDF文件路径
        """
        try:
            self.log_info(f"开始MRC压缩: {input_path}")
            
            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            # 注意：PyPDF2不直接支持MRC压缩
            # 这里提供一个占位实现，实际项目中需要专业库支持
            raise Exception("MRC压缩功能需要专业库支持，建议使用专业PDF处理工具。\n"
                            "可考虑使用以下方案：\n"
                            "1. 使用Ghostscript命令行工具\n"
                            "2. 使用Adobe PDF Library等商业库")
                            
            self.log_info(f"MRC压缩完成: {output_path}")
        except Exception as e:
            self.log_error(f"MRC压缩失败: {str(e)}")
            raise Exception(f"MRC压缩失败: {str(e)}")

    def jbig2_compress(self, input_path, output_path):
        """
        JBIG2压缩（黑白图像的高效压缩）
        
        Args:
            input_path (str): 输入PDF文件路径
            output_path (str): 输出PDF文件路径
        """
        try:
            self.log_info(f"开始JBIG2压缩: {input_path}")
            
            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            # 注意：PyPDF2不直接支持JBIG2压缩
            # 这里提供一个占位实现，实际项目中需要专业库支持
            raise Exception("JBIG2压缩功能需要专业库支持，建议使用专业PDF处理工具。\n"
                            "可考虑使用以下方案：\n"
                            "1. 使用Ghostscript命令行工具\n"
                            "2. 使用Adobe PDF Library等商业库\n"
                            "3. 使用MuPDF等开源库")
                            
            self.log_info(f"JBIG2压缩完成: {output_path}")
        except Exception as e:
            self.log_error(f"JBIG2压缩失败: {str(e)}")
            raise Exception(f"JBIG2压缩失败: {str(e)}")

    def jpeg2000_compress(self, input_path, output_path, quality=85):
        """
        JPEG2000压缩（适合彩色图像）
        
        Args:
            input_path (str): 输入PDF文件路径
            output_path (str): 输出PDF文件路径
            quality (int): 图像质量（1-100）
        """
        try:
            self.log_info(f"开始JPEG2000压缩: {input_path}")
            
            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            reader = PdfReader(input_path)
            writer = PdfWriter()
            
            # 处理每一页
            for page in reader.pages:
                writer.add_page(page)
                
            # JPEG2000压缩图像对象
            for page in writer.pages:
                for image in page.images:
                    # 获取原始图像
                    image_data = image.data
                    image_obj = Image.open(io.BytesIO(image_data))
                    
                    # 转换为JPEG2000格式
                    output = io.BytesIO()
                    image_obj.save(output, format='JPEG2000', quality_layers=[quality])
                    image.replace(output.getvalue())
            
            # 保存压缩后的PDF
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
                
            self.log_info(f"JPEG2000压缩完成: {output_path}")
        except Exception as e:
            self.log_error(f"JPEG2000压缩失败: {str(e)}")
            raise Exception(f"JPEG2000压缩失败: {str(e)}")

    def convert_to_pdfa(self, input_path, output_path, pdfa_level="PDF/A-1b"):
        """
        PDF/A转换
        
        Args:
            input_path (str): 输入PDF文件路径
            output_path (str): 输出PDF/A文件路径
            pdfa_level (str): PDF/A标准级别 ("PDF/A-1b", "PDF/A-2b", "PDF/A-2u")
        """
        try:
            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            # 检查依赖是否可用
            if not PDFA_AVAILABLE:
                raise Exception("缺少PDF/A转换依赖库，请安装ghostscript")
            
            # 设置PDF/A级别
            if pdfa_level not in ["PDF/A-1b", "PDF/A-2b", "PDF/A-2u"]:
                raise ValueError("无效的PDF/A级别。有效值: PDF/A-1b, PDF/A-2b, PDF/A-2u")
                
            # 使用Ghostscript进行PDF/A转换
            # 注意：这需要系统中安装了Ghostscript
            gs_cmd = [
                "gs",
                "-dPDFA=1" if pdfa_level == "PDF/A-1b" else "-dPDFA=2",
                "-dBATCH",
                "-dNOPAUSE",
                "-sProcessColorModel=DeviceRGB",
                "-sDEVICE=pdfwrite",
                f"-sPDFACompatibilityPolicy=1",
                f"-sOutputFile={output_path}",
                input_path
            ]
            
            # 执行命令
            import subprocess
            result = subprocess.run(gs_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"PDF/A转换失败: {result.stderr}")
                
            return True
        except Exception as e:
            raise Exception(f"PDF/A转换失败: {str(e)}")

    def linearize_pdf(self, input_path, output_path):
        """
        线性化PDF（Web优化）
        
        Args:
            input_path (str): 输入PDF文件路径
            output_path (str): 输出线性化PDF文件路径
        """
        try:
            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            reader = PdfReader(input_path)
            writer = PdfWriter()
            
            # 复制所有页面
            for page in reader.pages:
                writer.add_page(page)
                
            # 线性化PDF（快速网络传输优化）
            # pypdf的线性化支持
            writer.linearize = True
            
            # 保存线性化后的PDF
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
                
            return True
        except Exception as e:
            raise Exception(f"PDF线性化失败: {str(e)}")

    def is_pdfa_available(self):
        """
        检查PDF/A转换功能是否可用
        
        Returns:
            bool: PDF/A转换功能是否可用
        """
        return PDFA_AVAILABLE