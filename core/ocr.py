#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OCR光学字符识别功能模块

接口状态: 已更新以符合统一接口标准ModuleInterface
更新内容:
1. 继承ModuleInterface基类
2. 使用标准日志记录方法
3. 实现标准接口方法
"""

import os
import cv2
import numpy as np
from core.interface import ModuleInterface

try:
    import pytesseract
    from PIL import Image
    import pdf2image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False


class OCREngine(ModuleInterface):
    """OCR引擎类"""

    def __init__(self):
        """初始化OCR引擎"""
        super().__init__("ocr")
        self.log_info("OCR引擎初始化完成")

    def process_pdf(self, input_path, output_path, languages=['eng']):
        """
        OCR识别PDF
        
        Args:
            input_path (str): 输入PDF文件路径
            output_path (str): 输出文本文件路径
            languages (list): OCR识别语言列表
        """
        try:
            if not OCR_AVAILABLE:
                raise Exception("缺少OCR依赖库，请安装 pytesseract, pillow 和 pdf2image")
                
            self.log_info(f"开始OCR识别: {input_path}")
            
            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            # 将PDF转换为图像
            images = pdf2image.convert_from_path(input_path)
            
            # 对每个图像执行OCR
            extracted_text = ""
            for i, image in enumerate(images):
                if self.should_cancel():
                    raise Exception("操作被用户取消")
                    
                # 将PIL图像转换为OpenCV格式
                open_cv_image = np.array(image)
                # 转换颜色空间 (RGB to BGR)
                open_cv_image = open_cv_image[:, :, ::-1].copy()
                
                # 预处理图像以提高OCR准确性
                processed_image = self._preprocess_image(open_cv_image)
                
                # 将OpenCV图像转换回PIL格式
                pil_image = Image.fromarray(processed_image)
                
                # 执行OCR
                lang = '+'.join(languages)
                page_text = pytesseract.image_to_string(pil_image, lang=lang)
                extracted_text += f"\n--- Page {i+1} ---\n{page_text}"
                
                self.log_debug(f"已完成第 {i+1} 页OCR")
            
            # 保存提取的文本
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(extracted_text)
                
            self.log_info(f"OCR识别完成: {output_path}")
        except Exception as e:
            self.log_error(f"OCR识别失败: {str(e)}")
            raise Exception(f"OCR识别失败: {str(e)}")

    def _preprocess_image(self, image):
        """
        预处理图像以提高OCR准确性
        
        Args:
            image: OpenCV图像对象
            
        Returns:
            处理后的图像
        """
        # 转换为灰度图
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 应用高斯模糊以减少噪声
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # 应用阈值以获得二值图像
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # 形态学操作以去除噪声
        kernel = np.ones((1, 1), np.uint8)
        processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        return processed

    def ocr_scan(self, input_path, output_path, languages=['eng']):
        """
        OCR扫描（兼容旧接口）
        
        Args:
            input_path (str): 输入PDF文件路径
            output_path (str): 输出文本文件路径
            languages (list): OCR识别语言列表
        """
        self.process_pdf(input_path, output_path, languages)

    def batch_ocr(self, input_paths, output_dir, languages=['eng']):
        """
        批量OCR识别
        
        Args:
            input_paths (list): 输入PDF文件路径列表
            output_dir (str): 输出目录路径
            languages (list): OCR识别语言列表
            
        Returns:
            list: 处理结果列表
        """
        try:
            self.log_info(f"开始批量OCR识别，共 {len(input_paths)} 个文件")
            
            # 确保输出目录存在
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            results = []
            for input_path in input_paths:
                try:
                    # 生成输出文件路径
                    name = os.path.splitext(os.path.basename(input_path))[0]
                    output_path = os.path.join(output_dir, f"{name}_ocr.txt")
                    
                    # 执行OCR
                    self.ocr_scan(input_path, output_path, languages)
                    results.append({
                        'input_path': input_path,
                        'output_path': output_path,
                        'success': True,
                        'error': None
                    })
                except Exception as e:
                    results.append({
                        'input_path': input_path,
                        'output_path': None,
                        'success': False,
                        'error': str(e)
                    })
            
            self.log_info(f"批量OCR识别完成，成功 {len([r for r in results if r['success']])} 个文件")
            return results
        except Exception as e:
            self.log_error(f"批量OCR处理失败: {str(e)}")
            raise Exception(f"批量OCR处理失败: {str(e)}")

    def optimize_ocr_quality(self, image, method="default"):
        """
        OCR质量优化
        
        Args:
            image (PIL.Image): 输入图像
            method (str): 优化方法 ("default", "denoise", "threshold", "sharpen")
            
        Returns:
            PIL.Image: 优化后的图像
        """
        try:
            # 转换为OpenCV格式
            cv_image = np.array(image)
            cv_image = cv_image[:, :, ::-1].copy()  # RGB to BGR
            
            # 转换为灰度图
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            if method == "denoise":
                # 去噪处理
                denoised = cv2.fastNlMeansDenoising(gray)
                processed = denoised
            elif method == "threshold":
                # 阈值处理
                _, processed = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            elif method == "sharpen":
                # 锐化处理
                kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
                sharpened = cv2.filter2D(gray, -1, kernel)
                processed = sharpened
            else:
                # 默认处理：高斯模糊和阈值
                blurred = cv2.GaussianBlur(gray, (5, 5), 0)
                _, processed = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # 转换回PIL图像
            optimized_image = Image.fromarray(processed)
            
            return optimized_image
        except Exception as e:
            # 如果优化失败，返回原始图像
            return image

    def is_ocr_available(self):
        """
        检查OCR功能是否可用
        
        Returns:
            bool: OCR功能是否可用
        """
        return OCR_AVAILABLE

    def multi_language_ocr(self, input_path, output_path, languages=['eng', 'chi_sim']):
        """
        多语言OCR识别
        
        Args:
            input_path (str): 输入PDF文件路径
            output_path (str): 输出文本文件路径
            languages (list): OCR识别语言列表
        """
        try:
            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            # 检查依赖是否可用
            if not OCR_AVAILABLE:
                raise Exception("OCR功能需要额外依赖库支持，请安装：\n"
                                "pip install pytesseract pdf2image pillow")
            
            # 将PDF转换为图像
            images = pdf2image.convert_from_path(input_path)
            
            # 对每个图像进行多语言OCR识别
            ocr_text = ""
            for i, image in enumerate(images):
                # 使用多种语言进行OCR识别
                combined_text = ""
                for lang in languages:
                    try:
                        text = pytesseract.image_to_string(image, lang=lang)
                        combined_text += f"[{lang}] {text}\n"
                    except Exception:
                        # 如果某种语言不可用，跳过
                        continue
                        
                ocr_text += f"--- Page {i+1} ---\n{combined_text}\n\n"
            
            # 保存OCR结果
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(ocr_text)
                
            return True
        except Exception as e:
            raise Exception(f"多语言OCR识别失败: {str(e)}")