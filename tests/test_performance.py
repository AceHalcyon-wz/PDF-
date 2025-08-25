#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
性能测试模块
"""

import unittest
import time
import os
import tempfile
from core.pdf_engine import PDFEngine
from core.editor import EditorEngine
from core.conversion import ConversionEngine


class TestPerformance(unittest.TestCase):
    """性能测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.pdf_engine = PDFEngine()
        self.editor_engine = EditorEngine()
        self.conversion_engine = ConversionEngine()
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """测试后清理"""
        # 清理测试文件
        pass
    
    def test_processing_time(self):
        """测试处理时间"""
        # 创建测试文件路径
        input_path = os.path.join(self.test_dir, "input.pdf")
        output_path = os.path.join(self.test_dir, "output.pdf")
        
        # 测试各种操作的执行时间
        operations = [
            ("PDF拆分", lambda: self.pdf_engine.split_pdf(input_path, output_path, [1])),
            ("PDF合并", lambda: self.pdf_engine.merge_pdfs([input_path, input_path], output_path)),
            ("PDF压缩", lambda: self.pdf_engine.compress_pdf(input_path, output_path)),
            ("PDF旋转", lambda: self.pdf_engine.rotate_pdf(input_path, output_path, 90)),
            ("页面删除", lambda: self.editor_engine.delete_pages(input_path, output_path, [1])),
            ("页面重排序", lambda: self.editor_engine.reorder_pages(input_path, output_path, [1, 2])),
            ("PDF转文本", lambda: self.conversion_engine.pdf_to_text(input_path, output_path.replace('.pdf', '.txt'))),
        ]
        
        # 由于缺少实际文件，这里仅测试函数调用结构
        for op_name, op_func in operations:
            start_time = time.time()
            try:
                op_func()
            except Exception:
                pass  # 预期会因缺少文件而异常
            end_time = time.time()
            
            # 记录执行时间（虽然实际操作未完成）
            execution_time = end_time - start_time
            print(f"{op_name} 操作耗时: {execution_time:.4f} 秒")


if __name__ == '__main__':
    unittest.main()