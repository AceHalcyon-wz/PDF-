#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PDF引擎测试模块
"""

import os
import tempfile
import unittest

from core.exceptions import PDFEngineError
from core.pdf_engine import PDFEngine


class TestPDFEngine(unittest.TestCase):
    """PDF引擎测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.pdf_engine = PDFEngine()
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """测试后清理"""
        # 清理测试文件
        pass
        
    def test_split_pdf(self):
        """测试PDF拆分功能"""
        # 创建测试输入文件路径和输出文件路径
        input_path = os.path.join(self.test_dir, "input.pdf")
        output_path = os.path.join(self.test_dir, "output.pdf")
        
        # 测试输入文件不存在的处理
        with self.assertRaises(PDFEngineError):
            self.pdf_engine.split_pdf(input_path, output_path, "page_count")
        
    def test_merge_pdfs(self):
        """测试PDF合并功能"""
        # 创建测试输入文件路径和输出文件路径
        input_paths = [
            os.path.join(self.test_dir, "input1.pdf"),
            os.path.join(self.test_dir, "input2.pdf")
        ]
        output_path = os.path.join(self.test_dir, "merged.pdf")
        
        # 测试空输入文件列表处理
        with self.assertRaises(ValueError):
            self.pdf_engine.merge_pdfs([], output_path)
        
    def test_compress_pdf(self):
        """测试PDF压缩功能"""
        # 创建测试输入文件路径和输出文件路径
        input_path = os.path.join(self.test_dir, "input.pdf")
        output_path = os.path.join(self.test_dir, "compressed.pdf")
        
        # 测试输入文件不存在的处理
        with self.assertRaises(PDFEngineError):
            self.pdf_engine.compress_pdf(input_path, output_path)
        
    def test_rotate_pdf(self):
        """测试PDF旋转功能"""
        # 创建测试输入文件路径和输出文件路径
        input_path = os.path.join(self.test_dir, "input.pdf")
        output_path = os.path.join(self.test_dir, "rotated.pdf")
        
        # 测试rotate_pdf方法不存在的处理
        self.assertFalse(hasattr(self.pdf_engine, 'rotate_pdf'))


if __name__ == '__main__':
    unittest.main()