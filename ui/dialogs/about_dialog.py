#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
关于对话框模块
"""

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit
from PyQt5.QtCore import Qt


class AboutDialog(QDialog):
    """关于对话框类"""

    def __init__(self, parent=None):
        """初始化关于对话框"""
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle('关于 PDF处理器')
        self.setFixedSize(400, 300)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        layout = QVBoxLayout()
        
        # 应用名称和版本
        app_label = QLabel('PDF处理器 v1.0.0')
        app_label.setAlignment(Qt.AlignCenter)
        app_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 20px;")
        
        # 描述信息
        desc_label = QLabel('一个功能强大的PDF处理工具，支持多种PDF操作功能。')
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setStyleSheet("margin: 10px;")
        desc_label.setWordWrap(True)
        
        # 版权信息
        copyright_label = QLabel('Copyright © 2025 PDF处理器开发团队')
        copyright_label.setAlignment(Qt.AlignCenter)
        copyright_label.setStyleSheet("margin: 10px;")
        
        # 确定按钮
        ok_button = QPushButton('确定')
        ok_button.clicked.connect(self.accept)
        ok_button.setStyleSheet("margin: 20px;")
        
        # 添加控件到布局
        layout.addWidget(app_label)
        layout.addWidget(desc_label)
        layout.addWidget(copyright_label)
        layout.addWidget(ok_button)
        
        self.setLayout(layout)