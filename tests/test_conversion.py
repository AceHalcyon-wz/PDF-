#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
格式转换测试模块
"""

import unittest
import os
import tempfile
from core.conversion import ConversionEngine
from unittest.mock import patch, MagicMock


class TestConversionEngine(unittest.TestCase):
    """格式转换引擎测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.conversion_engine = ConversionEngine()
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """测试后清理"""
        # 清理测试文件
        pass
        
    def test_pdf_to_text_with_invalid_input(self):
        """测试使用无效输入路径的PDF转文本功能"""
        # 创建测试输入文件路径和输出文件路径
        input_path = os.path.join(self.test_dir, "input.pdf")
        output_path = os.path.join(self.test_dir, "output.txt")
        
        # 由于没有真实PDF文件，预期会抛出特定异常
        with self.assertRaises(Exception):
            self.conversion_engine.pdf_to_text(input_path, output_path)
            
    @patch('core.conversion.os.path.exists')
    @patch('core.conversion.PdfReader')
    def test_pdf_to_text_with_mocked_filesystem(self, mock_pdf_reader, mock_exists):
        """使用模拟文件系统的PDF转文本功能测试"""
        # 设置模拟行为
        mock_exists.return_value = True
        mock_reader_instance = MagicMock()
        mock_pdf_reader.return_value = mock_reader_instance
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "test text"
        mock_reader_instance.pages = [mock_page]
        
        # 执行测试
        result = self.conversion_engine.pdf_to_text("input.pdf", "output.txt")
        
        # 验证结果
        self.assertTrue(result)

        
    def test_image_to_pdf_with_invalid_input(self):
        """测试使用无效输入路径的图像转PDF功能"""
        # 创建测试输入文件路径和输出文件路径
        input_paths = [
            os.path.join(self.test_dir, "image1.jpg"),
            os.path.join(self.test_dir, "image2.png")
        ]
        output_path = os.path.join(self.test_dir, "output.pdf")
        
        # 由于没有真实图像文件，预期会抛出特定异常
        with self.assertRaises(Exception):
            self.conversion_engine.image_to_pdf(input_paths, output_path)
            
    @patch('core.conversion.os.path.exists')
    @patch('core.conversion.Image')
    def test_image_to_pdf_with_mocked_filesystem(self, mock_image, mock_exists):
        """使用模拟文件系统的图像转PDF功能测试"""
        # 设置模拟行为
        mock_exists.return_value = True
        mock_image_instance = MagicMock()
        mock_image.open.return_value = mock_image_instance
        mock_image_instance.size = (100, 100)
        
        # 模拟canvas.Canvas以避免实际创建PDF文件
        with patch('core.conversion.canvas.Canvas') as mock_canvas:
            mock_canvas_instance = MagicMock()
            mock_canvas.return_value = mock_canvas_instance
            
            # 执行测试
            result = self.conversion_engine.image_to_pdf(["image1.jpg", "image2.png"], "output.pdf")
            
            # 验证结果
            self.assertTrue(result)
            mock_canvas_instance.drawImage.assert_called()
            mock_canvas_instance.showPage.assert_called()
            mock_canvas_instance.save.assert_called()


if __name__ == '__main__':
    unittest.main()