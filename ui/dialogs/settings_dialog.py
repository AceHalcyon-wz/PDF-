#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
设置对话框模块
参考企划文档中的设置界面设计
"""

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, \
    QTabWidget, QWidget, QCheckBox, QGroupBox, QLabel, QComboBox, QSpinBox, QFormLayout, \
    QTableWidget, QTableWidgetItem, QHeaderView, QKeySequenceEdit, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence


class SettingsDialog(QDialog):
    """设置对话框类"""

    def __init__(self, parent=None):
        """初始化设置对话框"""
        super().__init__(parent)
        self.parent = parent
        self.init_ui()
        
    def init_ui(self):
        """初始化UI界面"""
        self.setWindowTitle('设置')
        self.resize(500, 400)
        
        layout = QVBoxLayout()
        
        # 创建标签页
        tab_widget = QTabWidget()
        tab_widget.addTab(self.create_general_tab(), "常规设置")
        tab_widget.addTab(self.create_performance_tab(), "性能设置")
        tab_widget.addTab(self.create_shortcut_tab(), "快捷键设置")
        
        layout.addWidget(tab_widget)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        ok_button = QPushButton('确定')
        cancel_button = QPushButton('取消')
        apply_button = QPushButton('应用')
        
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        apply_button.clicked.connect(self.apply_settings)
        
        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(apply_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
    def create_general_tab(self):
        """创建常规设置标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 常规设置组
        general_group = QGroupBox("常规设置")
        general_layout = QFormLayout()
        
        # 主题设置
        theme_combo = QComboBox()
        theme_combo.addItems(["浅色主题", "深色主题", "跟随系统"])
        general_layout.addRow(QLabel("主题:"), theme_combo)
        
        # 语言设置
        language_combo = QComboBox()
        language_combo.addItems(["简体中文", "English"])
        general_layout.addRow(QLabel("语言:"), language_combo)
        
        general_group.setLayout(general_layout)
        layout.addWidget(general_group)
        
        # 文件设置组
        file_group = QGroupBox("文件设置")
        file_layout = QFormLayout()
        
        # 默认保存路径
        default_path_checkbox = QCheckBox("使用上次保存路径作为默认路径")
        file_layout.addRow(default_path_checkbox)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        layout.addStretch()
        return widget
        
    def create_performance_tab(self):
        """创建性能设置标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 性能设置组
        performance_group = QGroupBox("性能设置")
        performance_layout = QFormLayout()
        
        # 线程数设置
        thread_spinbox = QSpinBox()
        thread_spinbox.setRange(1, 16)
        thread_spinbox.setValue(4)
        performance_layout.addRow(QLabel("处理线程数:"), thread_spinbox)
        
        # 内存限制设置
        memory_spinbox = QSpinBox()
        memory_spinbox.setRange(256, 8192)
        memory_spinbox.setValue(1024)
        memory_spinbox.setSuffix(" MB")
        performance_layout.addRow(QLabel("内存使用限制:"), memory_spinbox)
        
        performance_group.setLayout(performance_layout)
        layout.addWidget(performance_group)
        
        layout.addStretch()
        return widget
        
    def create_shortcut_tab(self):
        """创建快捷键设置标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 快捷键表格
        self.shortcut_table = QTableWidget(0, 2)
        self.shortcut_table.setHorizontalHeaderLabels(["功能", "快捷键"])
        self.shortcut_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.shortcut_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        # 添加快捷键数据
        shortcuts = [
            ("打开文件", "Ctrl+O"),
            ("保存文件", "Ctrl+S"),
            ("新建窗口", "Ctrl+N"),
            ("打印文档", "Ctrl+P"),
            ("撤销", "Ctrl+Z"),
            ("重做", "Ctrl+Y"),
            ("复制", "Ctrl+C"),
            ("粘贴", "Ctrl+V"),
            ("全选", "Ctrl+A"),
            ("查找", "Ctrl+F"),
            ("替换", "Ctrl+H"),
            ("帮助", "F1"),
            ("首选项", "Ctrl+,"),
            ("全屏", "F11"),
            ("放大", "Ctrl++"),
            ("缩小", "Ctrl+-"),
            ("关闭", "Ctrl+W")
        ]
        
        self.shortcut_table.setRowCount(len(shortcuts))
        for row, (action, key) in enumerate(shortcuts):
            action_item = QTableWidgetItem(action)
            key_item = QTableWidgetItem(key)
            action_item.setFlags(action_item.flags() & ~Qt.ItemIsEditable)
            # key_item.setFlags(key_item.flags() & ~Qt.ItemIsEditable)
            self.shortcut_table.setItem(row, 0, action_item)
            self.shortcut_table.setItem(row, 1, key_item)
        
        layout.addWidget(QLabel("双击快捷键列可修改快捷键:"))
        layout.addWidget(self.shortcut_table)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        reset_btn = QPushButton("重置为默认")
        reset_btn.clicked.connect(self.reset_shortcuts)
        button_layout.addStretch()
        button_layout.addWidget(reset_btn)
        layout.addLayout(button_layout)
        
        layout.addStretch()
        return widget
    
    def reset_shortcuts(self):
        """重置快捷键为默认值"""
        reply = QMessageBox.question(self, '确认', '确定要重置所有快捷键为默认值吗？',
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            # 重置快捷键表格中的数据
            shortcuts = [
                ("打开文件", "Ctrl+O"),
                ("保存文件", "Ctrl+S"),
                ("新建窗口", "Ctrl+N"),
                ("打印文档", "Ctrl+P"),
                ("撤销", "Ctrl+Z"),
                ("重做", "Ctrl+Y"),
                ("复制", "Ctrl+C"),
                ("粘贴", "Ctrl+V"),
                ("全选", "Ctrl+A"),
                ("查找", "Ctrl+F"),
                ("替换", "Ctrl+H"),
                ("帮助", "F1"),
                ("首选项", "Ctrl+,"),
                ("全屏", "F11"),
                ("放大", "Ctrl++"),
                ("缩小", "Ctrl+-"),
                ("关闭", "Ctrl+W")
            ]
            
            for row, (action, key) in enumerate(shortcuts):
                self.shortcut_table.item(row, 1).setText(key)
        
    def apply_settings(self):
        """应用设置"""
        # 在这里实现设置的应用逻辑
        # 获取快捷键设置
        shortcuts = {}
        for row in range(self.shortcut_table.rowCount()):
            action = self.shortcut_table.item(row, 0).text()
            key = self.shortcut_table.item(row, 1).text()
            shortcuts[action] = key
        
        # 如果父窗口存在，更新其快捷键设置
        if self.parent and hasattr(self.parent, 'update_shortcuts'):
            self.parent.update_shortcuts(shortcuts)