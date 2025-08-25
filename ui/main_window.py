#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
主窗口模块
参考企划文档中的UI设计规范实现底部导航栏设计
"""

from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QToolBar, QStatusBar, QFileDialog, \
    QVBoxLayout, QWidget, QPushButton, QLabel, QStackedWidget, QComboBox, QSpinBox, \
    QHBoxLayout, QTextEdit, QApplication, QListWidget, QGroupBox, QGridLayout, \
    QTabWidget, QTableWidget, QHeaderView, QDialog, QButtonGroup, QRadioButton, \
    QLineEdit, QProgressBar, QTreeWidgetItem, QTreeWidget, QTableWidgetItem, QMessageBox, \
    QInputDialog, QShortcut
from PyQt5.QtGui import QIcon, QDragEnterEvent, QDropEvent, QKeySequence
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QThread, QObject, QRunnable, QThreadPool
import os

# 修改导入语句，使用正确的路径
from config.settings import SettingsManager
from ui.shortcuts import ShortcutManager




class WorkerSignals(QObject):
    """工作线程信号类"""
    progress_updated = pyqtSignal(int)
    finished = pyqtSignal(bool, str)
    error = pyqtSignal(str)


class Worker(QRunnable):
    """工作线程类"""
    def __init__(self, operation, *args, **kwargs):
        super().__init__()
        self.operation = operation
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        
        # 如果操作支持进度回调，则添加我们的进度更新方法
        if 'progress_callback' in self.kwargs:
            self.kwargs['progress_callback'] = self.signals.progress_updated.emit
        
    def run(self):
        try:
            # 执行操作
            result = self.operation(*self.args, **self.kwargs)
            self.signals.finished.emit(True, "操作成功完成")
        except Exception as e:
            self.signals.error.emit(str(e))
            self.signals.finished.emit(False, str(e))


class MainWindow(QMainWindow):
    """主窗口类，按照企划文档要求实现底部导航栏设计"""

    def __init__(self):
        """初始化主窗口"""
        super().__init__()
        self.thread_pool = QThreadPool()  # 使用线程池替代单一工作线程
        self.is_dark_theme = False  # 添加主题状态跟踪
        self.is_high_contrast_theme = True  # 设置默认为高对比度主题
        self.recent_files = []  # 最近处理的文件列表
        self.shortcut_manager = ShortcutManager(self)  # 初始化快捷键管理器
        self.init_ui()
        self.setAcceptDrops(True) # 启用拖放支持

    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle('PDF处理器')
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建中心部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建堆叠窗口用于切换不同页面
        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)
        
        # 创建各个功能页面
        self.create_home_page()
        self.create_tools_page()
        self.create_batch_page()
        self.create_history_page()
        self.create_settings_page()
        self.create_about_page() # 添加关于页面
        
        # 创建底部导航栏
        self.create_bottom_navigation()
        
        # 创建状态栏
        self.create_status_bar()
        
        # 设置样式
        self.set_modern_theme()
        # 应用默认高对比度主题
        self.change_theme("高对比度主题")

    def create_bottom_navigation(self):
        """创建底部导航栏，按照企划文档要求设计"""
        # 创建底部导航栏容器
        nav_container = QWidget()
        nav_container.setObjectName("bottomNav")
        nav_layout = QHBoxLayout(nav_container)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(0)
        
        # 创建导航按钮
        self.home_btn = QPushButton("首页")
        self.home_btn.setObjectName("navButton")
        self.home_btn.setCheckable(True)
        self.home_btn.setChecked(True)
        self.home_btn.clicked.connect(lambda: self.switch_page(0))
        
        self.tools_btn = QPushButton("工具")
        self.tools_btn.setObjectName("navButton")
        self.tools_btn.setCheckable(True)
        self.tools_btn.clicked.connect(lambda: self.switch_page(1))
        
        self.batch_btn = QPushButton("批量处理")
        self.batch_btn.setObjectName("navButton")
        self.batch_btn.setCheckable(True)
        self.batch_btn.clicked.connect(lambda: self.switch_page(2))
        
        self.history_btn = QPushButton("历史记录")
        self.history_btn.setObjectName("navButton")
        self.history_btn.setCheckable(True)
        self.history_btn.clicked.connect(lambda: self.switch_page(3))
        
        self.settings_btn = QPushButton("设置")
        self.settings_btn.setObjectName("navButton")
        self.settings_btn.setCheckable(True)
        self.settings_btn.clicked.connect(lambda: self.switch_page(4))
        
        self.about_btn = QPushButton("关于")
        self.about_btn.setObjectName("navButton")
        self.about_btn.setCheckable(True)
        self.about_btn.clicked.connect(lambda: self.switch_page(5))
        
        # 添加按钮到布局
        nav_layout.addWidget(self.home_btn)
        nav_layout.addWidget(self.tools_btn)
        nav_layout.addWidget(self.batch_btn)
        nav_layout.addWidget(self.history_btn)
        nav_layout.addWidget(self.settings_btn)
        nav_layout.addWidget(self.about_btn)
        
        # 将导航栏添加到主布局底部
        self.main_layout.addWidget(nav_container)

    def switch_page(self, index):
        """切换页面"""
        self.stacked_widget.setCurrentIndex(index)
        # 更新按钮状态
        for i, btn in enumerate([self.home_btn, self.tools_btn, self.batch_btn, self.history_btn, self.settings_btn, self.about_btn]):
            btn.setChecked(i == index)

    def create_home_page(self):
        """创建首页，按照企划文档的卡片式布局设计"""
        home_widget = QWidget()
        home_layout = QVBoxLayout(home_widget)
        home_layout.setSpacing(20)
        home_layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title_label = QLabel("欢迎使用PDF处理器")
        title_label.setObjectName("pageTitle")
        title_label.setAlignment(Qt.AlignCenter)
        home_layout.addWidget(title_label)
        
        # 常用功能快捷入口 - 卡片式布局
        functions_group = QGroupBox("常用功能")
        functions_layout = QGridLayout()
        functions_layout.setSpacing(15)
        
        # 第一行功能按钮
        split_btn = QPushButton("拆分PDF")
        split_btn.setObjectName("functionCard")
        split_btn.clicked.connect(self.split_pdf)
        functions_layout.addWidget(split_btn, 0, 0)
        
        merge_btn = QPushButton("合并PDF")
        merge_btn.setObjectName("functionCard")
        merge_btn.clicked.connect(self.merge_pdfs)
        functions_layout.addWidget(merge_btn, 0, 1)
        
        convert_btn = QPushButton("格式转换")
        convert_btn.setObjectName("functionCard")
        convert_btn.clicked.connect(self.convert_pdf)
        functions_layout.addWidget(convert_btn, 0, 2)
        
        # 第二行功能按钮
        edit_btn = QPushButton("编辑PDF")
        edit_btn.setObjectName("functionCard")
        edit_btn.clicked.connect(self.edit_pdf)
        functions_layout.addWidget(edit_btn, 1, 0)
        
        security_btn = QPushButton("安全处理")
        security_btn.setObjectName("functionCard")
        security_btn.clicked.connect(self.secure_pdf)
        functions_layout.addWidget(security_btn, 1, 1)
        
        ocr_btn = QPushButton("OCR识别")
        ocr_btn.setObjectName("functionCard")
        ocr_btn.clicked.connect(self.ocr_pdf)
        functions_layout.addWidget(ocr_btn, 1, 2)
        
        # 第三行新增功能按钮
        watermark_btn = QPushButton("添加水印")
        watermark_btn.setObjectName("functionCard")
        watermark_btn.clicked.connect(self.add_watermark)
        functions_layout.addWidget(watermark_btn, 2, 0)
        
        compress_btn = QPushButton("压缩PDF")
        compress_btn.setObjectName("functionCard")
        compress_btn.clicked.connect(self.compress_pdf)
        functions_layout.addWidget(compress_btn, 2, 1)
        
        extract_btn = QPushButton("提取页面")
        extract_btn.setObjectName("functionCard")
        extract_btn.clicked.connect(self.extract_pages)
        functions_layout.addWidget(extract_btn, 2, 2)
        
        functions_group.setLayout(functions_layout)
        home_layout.addWidget(functions_group)
        
        # 拖拽上传区域
        drop_group = QGroupBox("拖拽上传")
        drop_layout = QVBoxLayout()
        drop_label = QLabel("将PDF文件拖放到这里进行处理\n支持多文件拖放")
        drop_label.setAlignment(Qt.AlignCenter)
        drop_label.setObjectName("dropLabel")
        drop_layout.addWidget(drop_label)
        drop_group.setLayout(drop_layout)
        home_layout.addWidget(drop_group)
        
        # 最近处理的文件列表
        recent_group = QGroupBox("最近处理的文件")
        recent_layout = QVBoxLayout()
        self.recent_list = QListWidget()
        recent_layout.addWidget(self.recent_list)
        recent_group.setLayout(recent_layout)
        home_layout.addWidget(recent_group)
        
        # 处理统计信息
        stats_group = QGroupBox("处理统计")
        stats_layout = QHBoxLayout()
        today_label = QLabel("今日处理: 0 个文件")
        total_label = QLabel("总共处理: 0 个文件")
        stats_layout.addWidget(today_label)
        stats_layout.addWidget(total_label)
        stats_group.setLayout(stats_layout)
        home_layout.addWidget(stats_group)
        
        home_layout.addStretch()
        self.stacked_widget.addWidget(home_widget)

    def create_tools_page(self):
        """创建工具页面，按照企划文档的分类展示方式设计"""
        tools_widget = QWidget()
        tools_layout = QHBoxLayout(tools_widget)
        tools_layout.setSpacing(10)
        tools_layout.setContentsMargins(10, 10, 10, 10)
        
        # 工具分类树
        tools_tree = QTreeWidget()
        tools_tree.setHeaderLabels(["工具分类"])
        tools_tree.setMinimumWidth(200)
        
        # 添加工具分类
        basic_ops = QTreeWidgetItem(tools_tree, ["基础操作"])
        QTreeWidgetItem(basic_ops, ["拆分PDF"])
        QTreeWidgetItem(basic_ops, ["合并PDF"])
        QTreeWidgetItem(basic_ops, ["旋转页面"])
        QTreeWidgetItem(basic_ops, ["压缩PDF"])
        QTreeWidgetItem(basic_ops, ["提取页面"])
        
        convert_ops = QTreeWidgetItem(tools_tree, ["转换工具"])
        QTreeWidgetItem(convert_ops, ["PDF转文本"])
        QTreeWidgetItem(convert_ops, ["PDF转图像"])
        QTreeWidgetItem(convert_ops, ["图像转PDF"])
        QTreeWidgetItem(convert_ops, ["PDF转Word"])
        QTreeWidgetItem(convert_ops, ["Word转PDF"])
        QTreeWidgetItem(convert_ops, ["PDF转Excel"])
        QTreeWidgetItem(convert_ops, ["Excel转PDF"])
        QTreeWidgetItem(convert_ops, ["PDF转PPT"])
        QTreeWidgetItem(convert_ops, ["PPT转PDF"])
        QTreeWidgetItem(convert_ops, ["PDF转HTML"])
        QTreeWidgetItem(convert_ops, ["PDF转CSV"])
        QTreeWidgetItem(convert_ops, ["PDF转Markdown"])
        QTreeWidgetItem(convert_ops, ["文本转PDF"])
        
        edit_ops = QTreeWidgetItem(tools_tree, ["编辑工具"])
        QTreeWidgetItem(edit_ops, ["删除页面"])
        QTreeWidgetItem(edit_ops, ["插入页面"])
        QTreeWidgetItem(edit_ops, ["替换页面"])
        QTreeWidgetItem(edit_ops, ["重排序页面"])
        QTreeWidgetItem(edit_ops, ["添加水印"])
        QTreeWidgetItem(edit_ops, ["裁剪页面"])
        
        security_ops = QTreeWidgetItem(tools_tree, ["安全工具"])
        QTreeWidgetItem(security_ops, ["加密PDF"])
        QTreeWidgetItem(security_ops, ["解密PDF"])
        QTreeWidgetItem(security_ops, ["数字签名"])
        QTreeWidgetItem(security_ops, ["移除密码"])
        
        advanced_ops = QTreeWidgetItem(tools_tree, ["高级工具"])
        QTreeWidgetItem(advanced_ops, ["OCR识别"])
        QTreeWidgetItem(advanced_ops, ["比较文档"])
        QTreeWidgetItem(advanced_ops, ["优化压缩"])
        QTreeWidgetItem(advanced_ops, ["批量处理"])
        
        tools_tree.expandAll()
        tools_tree.itemClicked.connect(self.on_tool_selected)
        
        # 工具详情区域
        self.tool_details = QTextEdit()
        self.tool_details.setReadOnly(True)
        self.tool_details.setHtml(
            "<h2>PDF工具箱</h2>"
            "<p>请选择左侧的工具分类和具体功能查看详细信息</p>"
            "<p>每个工具都提供了详细的使用说明和参数设置</p>"
            "<p><b>点击工具名称可直接执行相应功能</b></p>"
            "<h3>使用说明</h3>"
            "<ol>"
            "<li>在左侧树形控件中选择需要的PDF处理功能</li>"
            "<li>点击功能名称可直接执行该功能</li>"
            "<li>部分功能会弹出参数设置对话框，请根据需要进行设置</li>"
            "<li>处理过程中可在状态栏查看进度信息</li>"
            "<li>处理完成后会显示成功或失败信息</li>"
            "</ol>"
            "<h3>注意事项</h3>"
            "<ul>"
            "<li>处理大文件时可能需要较长时间，请耐心等待</li>"
            "<li>部分高级功能可能需要安装额外依赖库</li>"
            "<li>处理过程中请勿关闭程序</li>"
            "<li>输出文件路径请勿包含特殊字符</li>"
            "</ul>"
        )
        
        tools_layout.addWidget(tools_tree, 1)
        tools_layout.addWidget(self.tool_details, 3)
        self.stacked_widget.addWidget(tools_widget)

    def show_tool_details(self, tool_name):
        """显示工具详情"""
        self.tool_details.setHtml(
            f"<h2>{tool_name}</h2>"
            "<p>详细说明</p>"
            "<p>参数设置</p>"
        )

    def create_batch_page(self):
        """创建批量处理页面"""
        batch_widget = QWidget()
        batch_layout = QVBoxLayout(batch_widget)
        
        # 标题
        title_label = QLabel("批量处理")
        title_label.setObjectName("pageTitle")
        title_label.setAlignment(Qt.AlignCenter)
        batch_layout.addWidget(title_label)
        
        # 批量处理功能说明
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setHtml(
            "<h2>批量处理功能</h2>"
            "<p>批量处理允许您一次性处理多个PDF文件，大大提高工作效率。</p>"
            "<p><b>功能特点：</b></p>"
            "<ul>"
            "<li>支持多种批量操作：拆分、合并、转换等</li>"
            "<li>可自定义处理模板</li>"
            "<li>支持定时任务</li>"
            "<li>处理进度实时显示</li>"
            "</ul>"
        )
        batch_layout.addWidget(info_text)
        
        # 批量任务列表
        task_group = QGroupBox("批量任务列表")
        task_layout = QVBoxLayout()
        self.task_table = QTableWidget(0, 4)
        self.task_table.setHorizontalHeaderLabels(["任务名称", "状态", "进度", "操作"])
        self.task_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        task_layout.addWidget(self.task_table)
        task_group.setLayout(task_layout)
        batch_layout.addWidget(task_group)
        
        # 批量操作按钮
        button_layout = QHBoxLayout()
        add_task_btn = QPushButton("添加任务")
        add_task_btn.clicked.connect(self.add_batch_task)
        remove_task_btn = QPushButton("移除任务")
        remove_task_btn.clicked.connect(self.remove_batch_task)
        start_process_btn = QPushButton("开始处理")
        start_process_btn.clicked.connect(self.start_batch_process)
        button_layout.addWidget(add_task_btn)
        button_layout.addWidget(remove_task_btn)
        button_layout.addWidget(start_process_btn)
        batch_layout.addLayout(button_layout)
        
        batch_layout.addStretch()
        self.stacked_widget.addWidget(batch_widget)

    def create_history_page(self):
        """创建历史记录页面"""
        history_widget = QWidget()
        history_layout = QVBoxLayout(history_widget)
        
        # 标题
        title_label = QLabel("处理历史")
        title_label.setObjectName("pageTitle")
        title_label.setAlignment(Qt.AlignCenter)
        history_layout.addWidget(title_label)
        
        # 历史记录表格
        history_group = QGroupBox("历史记录")
        history_layout_group = QVBoxLayout()
        self.history_table = QTableWidget(0, 5)
        self.history_table.setHorizontalHeaderLabels(["文件名", "操作类型", "处理时间", "状态", "详情"])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        history_layout_group.addWidget(self.history_table)
        history_group.setLayout(history_layout_group)
        history_layout.addWidget(history_group)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        refresh_btn = QPushButton("刷新")
        refresh_btn.clicked.connect(self.refresh_history)
        clear_btn = QPushButton("清空记录")
        clear_btn.clicked.connect(self.clear_history)
        reprocess_btn = QPushButton("重新处理")
        reprocess_btn.clicked.connect(self.reprocess_selected)
        button_layout.addWidget(refresh_btn)
        button_layout.addWidget(clear_btn)
        button_layout.addWidget(reprocess_btn)
        history_layout.addLayout(button_layout)
        
        history_layout.addStretch()
        self.stacked_widget.addWidget(history_widget)

    def create_settings_page(self):
        """创建设置页面"""
        settings_widget = QWidget()
        settings_layout = QVBoxLayout(settings_widget)
        
        # 标题
        title_label = QLabel("设置")
        title_label.setObjectName("pageTitle")
        title_label.setAlignment(Qt.AlignCenter)
        settings_layout.addWidget(title_label)
        
        # 创建标签页
        tab_widget = QTabWidget()
        
        # 常规设置标签
        general_tab = QWidget()
        general_layout = QVBoxLayout(general_tab)
        
        # 主题设置
        theme_group = QGroupBox("主题设置")
        theme_layout = QVBoxLayout()
        theme_combo = QComboBox()
        theme_combo.addItems(["浅色主题", "深色主题", "高对比度主题"])
        theme_combo.setCurrentText("高对比度主题")
        theme_combo.currentTextChanged.connect(self.change_theme)
        theme_layout.addWidget(theme_combo)
        theme_group.setLayout(theme_layout)
        general_layout.addWidget(theme_group)
        
        # 输出目录设置
        output_group = QGroupBox("输出设置")
        output_layout = QHBoxLayout()
        output_label = QLabel("默认输出目录:")
        self.output_edit = QLineEdit()
        output_button = QPushButton("浏览")
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_edit)
        output_layout.addWidget(output_button)
        output_group.setLayout(output_layout)
        general_layout.addWidget(output_group)
        
        general_layout.addStretch()
        tab_widget.addTab(general_tab, "常规设置")
        
        # 性能设置标签
        performance_tab = QWidget()
        performance_layout = QVBoxLayout(performance_tab)
        
        # 内存使用设置
        memory_group = QGroupBox("内存使用设置")
        memory_layout = QVBoxLayout()
        memory_label = QLabel("内存使用上限 (MB):")
        self.memory_spin = QSpinBox()
        self.memory_spin.setRange(128, 8192)
        self.memory_spin.setValue(1024)
        memory_layout.addWidget(memory_label)
        memory_layout.addWidget(self.memory_spin)
        memory_group.setLayout(memory_layout)
        performance_layout.addWidget(memory_group)
        
        # 并发处理设置
        concurrency_group = QGroupBox("并发处理设置")
        concurrency_layout = QVBoxLayout()
        concurrency_label = QLabel("同时处理的文件数量:")
        self.concurrency_spin = QSpinBox()
        self.concurrency_spin.setRange(1, 16)
        self.concurrency_spin.setValue(4)
        concurrency_layout.addWidget(concurrency_label)
        concurrency_layout.addWidget(self.concurrency_spin)
        concurrency_group.setLayout(concurrency_layout)
        performance_layout.addWidget(concurrency_group)
        
        # 缓存设置
        cache_group = QGroupBox("缓存设置")
        cache_layout = QVBoxLayout()
        cache_label = QLabel("文件缓存大小 (MB):")
        self.cache_spin = QSpinBox()
        self.cache_spin.setRange(32, 2048)
        self.cache_spin.setValue(256)
        cache_layout.addWidget(cache_label)
        cache_layout.addWidget(self.cache_spin)
        cache_group.setLayout(cache_layout)
        performance_layout.addWidget(cache_group)
        
        performance_layout.addStretch()
        tab_widget.addTab(performance_tab, "性能设置")
        
        # 快捷键设置标签
        shortcut_tab = QWidget()
        shortcut_layout = QVBoxLayout(shortcut_tab)
        
        # 快捷键表格
        shortcut_table = QTableWidget(0, 2)
        shortcut_table.setHorizontalHeaderLabels(["功能", "快捷键"])
        shortcut_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # 添加快捷键数据
        shortcuts = [
            ("打开文件", "Ctrl+O"),
            ("保存文件", "Ctrl+S"),
            ("新建窗口", "Ctrl+N"),
            ("打印文档", "Ctrl+P"),
            ("撤销", "Ctrl+Z"),
            ("重做", "Ctrl+Y"),
            ("复制", "Ctrl+C"),
            ("粘贴", "Ctrl+V")
        ]
        
        shortcut_table.setRowCount(len(shortcuts))
        for row, (action, key) in enumerate(shortcuts):
            action_item = QTableWidgetItem(action)
            key_item = QTableWidgetItem(key)
            action_item.setFlags(action_item.flags() & ~Qt.ItemIsEditable)
            key_item.setFlags(key_item.flags() & ~Qt.ItemIsEditable)
            shortcut_table.setItem(row, 0, action_item)
            shortcut_table.setItem(row, 1, key_item)
        
        shortcut_layout.addWidget(QLabel("快捷键列表:"))
        shortcut_layout.addWidget(shortcut_table)
        
        # 自定义快捷键按钮
        customize_btn = QPushButton("自定义快捷键")
        customize_btn.clicked.connect(self.customize_shortcuts)
        shortcut_layout.addWidget(customize_btn)
        
        shortcut_layout.addStretch()
        tab_widget.addTab(shortcut_tab, "快捷键设置")
        
        settings_layout.addWidget(tab_widget)
        self.stacked_widget.addWidget(settings_widget)
        
    def customize_shortcuts(self):
        """自定义快捷键"""
        from ui.dialogs.settings_dialog import SettingsDialog
        dialog = SettingsDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.status_label.setText("快捷键设置已更新")

    def update_shortcuts(self, shortcuts):
        """更新快捷键设置"""
        # 更新快捷键管理器中的快捷键
        self.shortcut_manager.update_shortcuts(shortcuts)
        self.status_label.setText("快捷键已更新")

    def change_theme(self, theme_name):
        """切换主题"""
        if theme_name == "浅色主题":
            self.setProperty("theme", "light")
            self.is_dark_theme = False
            self.is_high_contrast_theme = False
        elif theme_name == "深色主题":
            self.setProperty("theme", "dark")
            self.is_dark_theme = True
            self.is_high_contrast_theme = False
        elif theme_name == "高对比度主题":
            self.setProperty("theme", "high_contrast")
            self.is_dark_theme = False
            self.is_high_contrast_theme = True
            
        self.apply_theme()

    def apply_theme(self):
        """应用主题"""
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def set_modern_theme(self):
        """设置现代主题样式"""
        # 读取样式文件
        try:
            with open(os.path.join(os.path.dirname(__file__), 'modern_style.css'), 'r', encoding='utf-8') as f:
                style_sheet = f.read()
                self.setStyleSheet(style_sheet)
        except Exception as e:
            print(f"加载样式文件失败: {e}")

    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel("就绪")
        self.status_bar.addWidget(self.status_label)

    def create_tools_page(self):
        """创建工具页面，按照企划文档的分类展示方式设计"""
        tools_widget = QWidget()
        tools_layout = QHBoxLayout(tools_widget)
        tools_layout.setSpacing(10)
        tools_layout.setContentsMargins(10, 10, 10, 10)
        
        # 工具分类树
        tools_tree = QTreeWidget()
        tools_tree.setHeaderLabels(["工具分类"])
        tools_tree.setMinimumWidth(200)
        
        # 添加工具分类
        basic_ops = QTreeWidgetItem(tools_tree, ["基础操作"])
        QTreeWidgetItem(basic_ops, ["拆分PDF"])
        QTreeWidgetItem(basic_ops, ["合并PDF"])
        QTreeWidgetItem(basic_ops, ["旋转页面"])
        QTreeWidgetItem(basic_ops, ["压缩PDF"])
        QTreeWidgetItem(basic_ops, ["提取页面"])
        
        convert_ops = QTreeWidgetItem(tools_tree, ["转换工具"])
        QTreeWidgetItem(convert_ops, ["PDF转文本"])
        QTreeWidgetItem(convert_ops, ["PDF转图像"])
        QTreeWidgetItem(convert_ops, ["图像转PDF"])
        QTreeWidgetItem(convert_ops, ["PDF转Word"])
        QTreeWidgetItem(convert_ops, ["Word转PDF"])
        QTreeWidgetItem(convert_ops, ["PDF转Excel"])
        QTreeWidgetItem(convert_ops, ["Excel转PDF"])
        QTreeWidgetItem(convert_ops, ["PDF转PPT"])
        QTreeWidgetItem(convert_ops, ["PPT转PDF"])
        QTreeWidgetItem(convert_ops, ["PDF转HTML"])
        QTreeWidgetItem(convert_ops, ["PDF转CSV"])
        QTreeWidgetItem(convert_ops, ["PDF转Markdown"])
        QTreeWidgetItem(convert_ops, ["文本转PDF"])
        
        edit_ops = QTreeWidgetItem(tools_tree, ["编辑工具"])
        QTreeWidgetItem(edit_ops, ["删除页面"])
        QTreeWidgetItem(edit_ops, ["插入页面"])
        QTreeWidgetItem(edit_ops, ["替换页面"])
        QTreeWidgetItem(edit_ops, ["重排序页面"])
        QTreeWidgetItem(edit_ops, ["添加水印"])
        QTreeWidgetItem(edit_ops, ["裁剪页面"])
        
        security_ops = QTreeWidgetItem(tools_tree, ["安全工具"])
        QTreeWidgetItem(security_ops, ["加密PDF"])
        QTreeWidgetItem(security_ops, ["解密PDF"])
        QTreeWidgetItem(security_ops, ["数字签名"])
        QTreeWidgetItem(security_ops, ["移除密码"])
        
        advanced_ops = QTreeWidgetItem(tools_tree, ["高级工具"])
        QTreeWidgetItem(advanced_ops, ["OCR识别"])
        QTreeWidgetItem(advanced_ops, ["比较文档"])
        QTreeWidgetItem(advanced_ops, ["优化压缩"])
        QTreeWidgetItem(advanced_ops, ["批量处理"])
        
        tools_tree.expandAll()
        tools_tree.itemClicked.connect(self.on_tool_selected)
        
        # 工具详情区域
        self.tool_details = QTextEdit()
        self.tool_details.setReadOnly(True)
        self.tool_details.setHtml(
            "<h2>PDF工具箱</h2>"
            "<p>请选择左侧的工具分类和具体功能查看详细信息</p>"
            "<p>每个工具都提供了详细的使用说明和参数设置</p>"
            "<p><b>点击工具名称可直接执行相应功能</b></p>"
            "<h3>使用说明</h3>"
            "<ol>"
            "<li>在左侧树形控件中选择需要的PDF处理功能</li>"
            "<li>点击功能名称可直接执行该功能</li>"
            "<li>部分功能会弹出参数设置对话框，请根据需要进行设置</li>"
            "<li>处理过程中可在状态栏查看进度信息</li>"
            "<li>处理完成后会显示成功或失败信息</li>"
            "</ol>"
            "<h3>注意事项</h3>"
            "<ul>"
            "<li>处理大文件时可能需要较长时间，请耐心等待</li>"
            "<li>部分高级功能可能需要安装额外依赖库</li>"
            "<li>处理过程中请勿关闭程序</li>"
            "<li>输出文件路径请勿包含特殊字符</li>"
            "</ul>"
        )
        
        tools_layout.addWidget(tools_tree, 1)
        tools_layout.addWidget(self.tool_details, 3)
        self.stacked_widget.addWidget(tools_widget)

    def on_tool_selected(self, item, column):
        """工具被选中"""
        tool_name = item.text(0)
        
        # 根据工具名称执行相应功能
        if tool_name == "拆分PDF":
            self.split_pdf()
        elif tool_name == "合并PDF":
            self.merge_pdfs()
        elif tool_name == "旋转页面":
            self.rotate_pages()
        elif tool_name == "压缩PDF":
            self.compress_pdf()
        elif tool_name == "提取页面":
            self.extract_pages()
        elif tool_name == "PDF转文本":
            self.pdf_to_text()
        elif tool_name == "PDF转图像":
            self.pdf_to_images()
        elif tool_name == "图像转PDF":
            self.images_to_pdf()
        elif tool_name == "PDF转Word":
            self.pdf_to_word()
        elif tool_name == "Word转PDF":
            self.word_to_pdf()
        elif tool_name == "PDF转Excel":
            self.pdf_to_excel()
        elif tool_name == "Excel转PDF":
            self.excel_to_pdf()
        elif tool_name == "PDF转PPT":
            self.pdf_to_ppt()
        elif tool_name == "PPT转PDF":
            self.ppt_to_pdf()
        elif tool_name == "PDF转HTML":
            self.pdf_to_html()
        elif tool_name == "PDF转CSV":
            self.pdf_to_csv()
        elif tool_name == "PDF转Markdown":
            self.pdf_to_markdown()
        elif tool_name == "文本转PDF":
            self.text_to_pdf()
        elif tool_name == "删除页面":
            self.delete_pages()
        elif tool_name == "插入页面":
            self.insert_pages()
        elif tool_name == "替换页面":
            self.replace_pages()
        elif tool_name == "重排序页面":
            self.reorder_pages()
        elif tool_name == "添加水印":
            self.add_watermark()
        elif tool_name == "裁剪页面":
            self.crop_pages()
        elif tool_name == "加密PDF":
            self.encrypt_pdf()
        elif tool_name == "解密PDF":
            self.decrypt_pdf()
        elif tool_name == "数字签名":
            self.digital_signature()
        elif tool_name == "移除密码":
            self.remove_password()
        elif tool_name == "OCR识别":
            self.ocr_pdf()
        elif tool_name == "比较文档":
            self.compare_documents()
        elif tool_name == "优化压缩":
            self.optimize_compression()
        elif tool_name == "批量处理":
            self.switch_page(2)  # 切换到批量处理页面
        else:
            # 显示工具说明
            self.tool_details.setHtml(
                f"<h3>{tool_name}</h3>"
                f"<p>这是 {tool_name} 功能的详细说明。</p>"
                f"<p>在这里可以设置相关参数并执行操作。</p>"
                f"<p><b>点击左侧工具名称可直接执行该功能</b></p>"
            )

    def show_tool_details(self, tool_name):
        """显示工具详情"""
        tool_info = {
            "拆分PDF": {
                "description": "将一个PDF文件按指定规则拆分成多个文件",
                "features": [
                    "按固定页数拆分",
                    "按自定义页码范围拆分",
                    "首页与末页配对拆分"
                ],
                "parameters": [
                    "输入文件: 待拆分的PDF文件",
                    "拆分方式: 按页数/按范围/配对模式",
                    "页数或范围: 具体的页数或页码范围",
                    "输出目录: 拆分后文件的保存位置"
                ],
                "notes": [
                    "拆分后的文件会保存在指定输出目录中",
                    "文件名会自动添加页码范围后缀"
                ]
            },
            "合并PDF": {
                "description": "将多个PDF文件按顺序合并成一个文件",
                "features": [
                    "支持拖拽排序",
                    "可自定义页面范围",
                    "保留书签和元数据"
                ],
                "parameters": [
                    "文件列表: 待合并的PDF文件列表",
                    "合并顺序: 文件的排列顺序", 
                    "输出文件: 合并后文件的保存路径"
                ],
                "notes": [
                    "可通过拖拽调整文件顺序",
                    "支持选择每个文件的特定页面范围"
                ]
            },
            "旋转页面": {
                "description": "对PDF文件中的页面进行旋转操作",
                "features": [
                    "支持90度倍数旋转",
                    "可指定页面范围",
                    "支持顺时针和逆时针旋转"
                ],
                "parameters": [
                    "输入文件: 待处理的PDF文件",
                    "旋转角度: 90、180或270度",
                    "页面范围: 需要旋转的页面"
                ],
                "notes": [
                    "旋转角度以顺时针方向计算",
                    "页面范围支持格式如: 1-3,5,7-10"
                ]
            },
            "压缩PDF": {
                "description": "减小PDF文件大小，便于存储和传输",
                "features": [
                    "多种压缩级别可选",
                    "图像质量可调",
                    "保持文本清晰度"
                ],
                "parameters": [
                    "输入文件: 待压缩的PDF文件",
                    "压缩级别: 低、中、高三档",
                    "输出文件: 压缩后文件保存路径"
                ],
                "notes": [
                    "高压缩级别可能会降低图像质量",
                    "文本内容质量不受影响"
                ]
            },
            "提取页面": {
                "description": "从PDF文件中提取指定页面生成新文件",
                "features": [
                    "支持单页或多页提取",
                    "可指定页面范围",
                    "保持原始质量"
                ],
                "parameters": [
                    "输入文件: 源PDF文件",
                    "页面范围: 要提取的页面",
                    "输出文件: 提取后文件保存路径"
                ],
                "notes": [
                    "页面范围支持格式如: 1-3,5,7-10",
                    "提取的页面将保持原始质量"
                ]
            },
            "PDF转文本": {
                "description": "将PDF文件中的文字内容提取为纯文本格式",
                "features": [
                    "保持文本结构",
                    "支持多种编码格式",
                    "可选择提取范围"
                ],
                "parameters": [
                    "输入文件: 源PDF文件",
                    "页面范围: 可选的页面范围",
                    "输出文件: 文本文件保存路径"
                ],
                "notes": [
                    "仅提取可识别的文本内容",
                    "扫描版PDF需要先进行OCR处理"
                ]
            },
            "PDF转图像": {
                "description": "将PDF文件中的页面转换为图像格式",
                "features": [
                    "支持多种图像格式",
                    "可自定义分辨率",
                    "批量转换所有页面"
                ],
                "parameters": [
                    "输入文件: 源PDF文件",
                    "输出格式: JPG、PNG等格式",
                    "分辨率: 图像分辨率设置",
                    "输出目录: 图像文件保存目录"
                ],
                "notes": [
                    "高分辨率图像文件较大",
                    "支持每页保存为单独图像文件"
                ]
            },
            "图像转PDF": {
                "description": "将图像文件转换为PDF格式",
                "features": [
                    "支持多种图像格式",
                    "可调整页面布局",
                    "批量转换多张图像"
                ],
                "parameters": [
                    "输入文件: 图像文件列表",
                    "页面尺寸: PDF页面大小",
                    "输出文件: PDF文件保存路径"
                ],
                "notes": [
                    "支持JPG、PNG、BMP等常见格式",
                    "可调整图像在页面中的位置和大小"
                ]
            },
            "PDF转Word": {
                "description": "将PDF文件转换为可编辑的Word文档",
                "features": [
                    "保持原文本格式",
                    "保留图像和表格",
                    "支持复杂布局"
                ],
                "parameters": [
                    "输入文件: 源PDF文件",
                    "页面范围: 可选的页面范围",
                    "输出文件: Word文件保存路径"
                ],
                "notes": [
                    "转换效果取决于PDF文件的质量",
                    "扫描版PDF需要先进行OCR处理"
                ]
            },
            "Word转PDF": {
                "description": "将Word文档转换为PDF格式",
                "features": [
                    "保持原始格式",
                    "支持字体嵌入",
                    "高质量输出"
                ],
                "parameters": [
                    "输入文件: Word文档文件",
                    "页面设置: 页面大小和边距",
                    "输出文件: PDF文件保存路径"
                ],
                "notes": [
                    "转换后文件便于分发和打印",
                    "保持原始文档的格式和布局"
                ]
            },
            "添加水印": {
                "description": "为PDF文件添加文本或图像水印",
                "features": [
                    "支持文本和图像水印",
                    "可调整透明度和位置",
                    "批量处理所有页面"
                ],
                "parameters": [
                    "输入文件: 源PDF文件",
                    "水印类型: 文本或图像水印",
                    "水印参数: 文本内容、图像文件等",
                    "输出文件: 添加水印后文件保存路径"
                ],
                "notes": [
                    "文本水印可自定义字体和大小",
                    "图像水印支持常见图片格式"
                ]
            },
            "OCR识别": {
                "description": "对扫描版PDF进行光学字符识别",
                "features": [
                    "支持多语言识别",
                    "多种输出格式",
                    "高精度识别算法"
                ],
                "parameters": [
                    "输入文件: 扫描版PDF文件",
                    "识别语言: 中文、英文等",
                    "输出格式: PDF、文本、Word等",
                    "输出文件: 识别结果保存路径"
                ],
                "notes": [
                    "识别效果取决于图像质量",
                    "支持中文和英文等多种语言"
                ]
            },
            "加密PDF": {
                "description": "为PDF文件添加密码保护",
                "features": [
                    "设置打开密码",
                    "设置权限密码",
                    "多种加密算法"
                ],
                "parameters": [
                    "输入文件: 源PDF文件",
                    "打开密码: 打开文件所需密码",
                    "权限设置: 打印、编辑等权限控制",
                    "输出文件: 加密后文件保存路径"
                ],
                "notes": [
                    "请妥善保管设置的密码",
                    "加密后文件安全性更高"
                ]
            },
            "解密PDF": {
                "description": "移除PDF文件的密码保护",
                "features": [
                    "移除打开密码",
                    "移除权限限制",
                    "保持文件内容"
                ],
                "parameters": [
                    "输入文件: 加密的PDF文件",
                    "密码: 文件的打开密码",
                    "输出文件: 解密后文件保存路径"
                ],
                "notes": [
                    "需要提供正确的密码才能解密",
                    "解密后文件可自由编辑和复制"
                ]
            }
        }

        # 获取工具信息
        tool_info = tool_descriptions.get(tool_name, {
            "description": "暂无详细说明",
            "features": ["暂无特性信息"],
            "parameters": ["暂无参数信息"],
            "notes": ["暂无注意事项"]
        })

        # 构造HTML内容
        html_content = f"<h2>{tool_name}</h2>"
        html_content += f"<p><b>功能描述:</b> {tool_info['description']}</p>"
        
        html_content += "<h3>主要特性</h3><ul>"
        for feature in tool_info['features']:
            html_content += f"<li>{feature}</li>"
        html_content += "</ul>"
        
        html_content += "<h3>参数说明</h3><ul>"
        for param in tool_info['parameters']:
            html_content += f"<li>{param}</li>"
        html_content += "</ul>"
        
        html_content += "<h3>注意事项</h3><ul>"
        for note in tool_info['notes']:
            html_content += f"<li>{note}</li>"
        html_content += "</ul>"
        
        html_content += "<p><b>点击左侧功能名称可直接执行此功能</b></p>"
        
        self.tool_details.setHtml(html_content)
        
    # 文件操作方法
    def open_file(self):
        """打开文件"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, 
            '选择PDF文件', 
            '', 
            'PDF文件 (*.pdf)'
        )
        if file_paths:
            for file_path in file_paths:
                self.add_to_recent_files(file_path)
            self.status_label.setText(f'已打开 {len(file_paths)} 个文件')

    def add_to_recent_files(self, file_path):
        """添加文件到最近处理列表"""
        if file_path not in self.recent_files:
            self.recent_files.insert(0, file_path)
            if len(self.recent_files) > 10:  # 限制最多10个最近文件
                self.recent_files.pop()
            # 更新UI中的最近文件列表
            self.update_recent_list()

    def update_recent_list(self):
        """更新最近处理文件列表"""
        self.recent_list.clear()
        for file_path in self.recent_files:
            self.recent_list.addItem(os.path.basename(file_path))

    def dragEnterEvent(self, event: QDragEnterEvent):
        """拖放进入事件"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        """拖放事件"""
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        pdf_files = [f for f in files if f.lower().endswith('.pdf')]
        for file in pdf_files:
            self.add_to_recent_files(file)
        self.status_label.setText(f'通过拖放添加了 {len(pdf_files)} 个PDF文件')

    # 主要功能方法
    def split_pdf(self):
        """拆分PDF"""
        # 选择要拆分的PDF文件
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            '选择要拆分的PDF文件', 
            '', 
            'PDF文件 (*.pdf)'
        )
        
        if not file_path:
            return
            
        self.status_label.setText('准备拆分PDF...')
        self.log("准备拆分PDF...")
        
        # 创建拆分选项对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("PDF拆分选项")
        dialog.setGeometry(200, 200, 400, 250)
        
        layout = QVBoxLayout()
        
        # 拆分类型选择
        type_label = QLabel("选择拆分类型:")
        type_combo = QComboBox()
        type_combo.addItems([
            "按固定页数拆分", 
            "按页码范围拆分", 
            "首页与末页配对拆分"
        ])
        
        # 按固定页数拆分设置
        pages_layout = QHBoxLayout()
        pages_layout.addWidget(QLabel("每份页数:"))
        pages_spin = QSpinBox()
        pages_spin.setMinimum(1)
        pages_spin.setMaximum(1000)
        pages_spin.setValue(10)
        pages_layout.addWidget(pages_spin)
        
        # 按页码范围拆分设置
        ranges_layout = QHBoxLayout()
        ranges_layout.addWidget(QLabel("页码范围:"))
        ranges_edit = QLineEdit()
        ranges_edit.setPlaceholderText("例如: 1-5,7-10,12")
        ranges_layout.addWidget(ranges_edit)
        ranges_layout.addWidget(QLabel("(用逗号分隔多个范围)"))
        
        # 输出路径选择
        output_layout = QHBoxLayout()
        output_label = QLabel("输出目录:")
        output_edit = QLineEdit()
        output_button = QPushButton("浏览")
        
        # 设置默认输出目录
        from config.settings import SettingsManager
        settings = SettingsManager()
        default_output_dir = settings.get("processing.default_output_dir", "./output")
        output_edit.setText(default_output_dir)
        
        def select_output_dir():
            directory = QFileDialog.getExistingDirectory(self, "选择输出目录", default_output_dir)
            if directory:
                output_edit.setText(directory)
                
        output_button.clicked.connect(select_output_dir)
        output_layout.addWidget(output_label)
        output_layout.addWidget(output_edit)
        output_layout.addWidget(output_button)
        
        # 确定和取消按钮
        buttons_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        cancel_button = QPushButton("取消")
        buttons_layout.addWidget(ok_button)
        buttons_layout.addWidget(cancel_button)
        
        # 组装对话框
        layout.addWidget(type_label)
        layout.addWidget(type_combo)
        layout.addLayout(pages_layout)
        layout.addLayout(ranges_layout)
        layout.addLayout(output_layout)
        layout.addLayout(buttons_layout)
        
        dialog.setLayout(layout)
        
        # 隐藏/显示相关控件
        def on_type_changed(index):
            pages_layout.parentWidget().setVisible(index == 0)
            ranges_layout.parentWidget().setVisible(index == 1)
            
        type_combo.currentIndexChanged.connect(on_type_changed)
        on_type_changed(0)  # 初始化状态
        
        # 连接按钮
        cancel_button.clicked.connect(dialog.reject)
        
        def do_split():
            split_type = type_combo.currentText()
            output_path = output_edit.text()
            
            # 确保输出目录存在
            if not os.path.exists(output_path):
                try:
                    os.makedirs(output_path)
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"无法创建输出目录: {str(e)}")
                    return
                    
            try:
                # 导入核心模块
                from core.pdf_engine import PDFEngine
                
                # 调用核心功能
                engine = PDFEngine()
                
                if split_type == "按固定页数拆分":
                    pages_per_split = pages_spin.value()
                    files = engine.split_pdf(file_path, output_path, pages_per_split)
                    self.status_label.setText(f'PDF拆分完成，共创建 {len(files)} 个文件')
                    self.log(f"PDF拆分完成，共创建 {len(files)} 个文件")
                elif split_type == "按页码范围拆分":
                    ranges_input = ranges_edit.text()
                    files = engine.split_by_ranges(file_path, ranges_input, output_path)
                    self.status_label.setText(f'PDF拆分完成，共创建 {len(files)} 个文件')
                    self.log(f"PDF拆分完成，共创建 {len(files)} 个文件")
                elif split_type == "首页与末页配对拆分":
                    files = engine.split_pair_mode(file_path, output_path)
                    self.status_label.setText(f'PDF拆分完成，共创建 {len(files)} 个文件')
                    self.log(f"PDF拆分完成，共创建 {len(files)} 个文件")

                    self.log(f"PDF拆分完成，共创建 {len(files)} 个文件")
                
                dialog.accept()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"PDF拆分失败: {str(e)}")
                self.status_label.setText('PDF拆分失败')
                self.log(f"PDF拆分失败: {str(e)}")
                
        ok_button.clicked.connect(do_split)
        
        dialog.exec_()

    def merge_pdfs(self):
        """合并PDF"""
        # 选择要合并的PDF文件
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, 
            '选择要合并的PDF文件', 
            '', 
            'PDF文件 (*.pdf)'
        )
        
        if not file_paths or len(file_paths) < 2:
            self.status_label.setText('至少需要选择两个PDF文件进行合并')
            self.log("至少需要选择两个PDF文件进行合并")
            return
            
        # 选择输出文件路径
        output_path, _ = QFileDialog.getSaveFileName(
            self, 
            '保存合并后的PDF文件', 
            '合并.pdf', 
            'PDF文件 (*.pdf)'
        )
        
        if not output_path:
            return
            
        self.status_label.setText('正在合并PDF...')
        self.log("正在合并PDF...")
        
        try:
            # 导入核心模块
            from core.pdf_engine import PDFEngine
            
            # 调用核心功能
            engine = PDFEngine()
            engine.merge_pdfs(file_paths, output_path)
            
            self.status_label.setText('PDF合并完成')
            self.log("PDF合并完成")
        except Exception as e:
            self.status_label.setText('PDF合并失败')
            self.log(f"PDF合并失败: {str(e)}")

    def text_to_pdf(self):
        """文本转PDF"""
        # 选择要转换的文本文件
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            '选择要转换为PDF的文本文件', 
            '', 
            '文本文件 (*.txt)'
        )
        
        if not file_path:
            return
            
        # 选择输出文件路径
        output_path, _ = QFileDialog.getSaveFileName(
            self, 
            '保存PDF文件', 
            'output.pdf', 
            'PDF文件 (*.pdf)'
        )
        
        if not output_path:
            return
            
        self.status_label.setText('正在转换文本为PDF...')
        self.log("正在转换文本为PDF...")
        
        try:
            # 导入核心模块
            from core.conversion import ConversionEngine
            
            # 调用核心功能
            converter = ConversionEngine()
            converter.text_to_pdf(file_path, output_path)
            
            self.status_label.setText('文本转PDF完成')
            self.log("文本转PDF完成")
        except Exception as e:
            self.status_label.setText('文本转PDF失败')
            self.log(f"文本转PDF失败: {str(e)}")

    def convert_pdf(self):
        """转换PDF"""
        self.log("执行PDF转换功能")
        # 实现PDF转换逻辑

    def compress_pdf(self):
        """压缩PDF"""
        self.log("执行PDF压缩功能")
        # 实现PDF压缩逻辑

    def extract_pages(self):
        """提取页面"""
        self.log("执行提取页面功能")
        # 实现提取页面逻辑

    def rotate_pages(self):
        """旋转页面"""
        self.log("执行旋转页面功能")
        # 实现旋转页面逻辑

    def pdf_to_text(self):
        """PDF转文本"""
        # 选择要转换的PDF文件
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            '选择要转换的PDF文件', 
            '', 
            'PDF文件 (*.pdf)'
        )
        
        if not file_path:
            return
            
        self.status_label.setText('准备转换PDF...')
        self.log("准备PDF转文本...")
        
        # 选择输出文件路径
        output_path, _ = QFileDialog.getSaveFileName(
            self, 
            '保存文本文件', 
            'output.txt', 
            '文本文件 (*.txt)'
        )
        
        if not output_path:
            return
            
        self.status_label.setText('正在转换PDF...')
        self.log("正在转换PDF...")
        
        try:
            # 导入核心模块
            from core.conversion import ConversionEngine
            
            # 调用核心功能
            converter = ConversionEngine()
            converter.pdf_to_text(file_path, output_path)
            
            self.status_label.setText('PDF转文本完成')
            self.log("PDF转文本完成")
        except Exception as e:
            self.status_label.setText('PDF转文本失败')
            self.log(f"PDF转文本失败: {str(e)}")
        
    def pdf_to_csv(self):
        """PDF转CSV"""
        # 选择要转换的PDF文件
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            '选择要转换的PDF文件', 
            '', 
            'PDF文件 (*.pdf)'
        )
        
        if not file_path:
            return
            
        self.status_label.setText('准备转换PDF...')
        self.log("准备PDF转CSV...")
        
        # 选择输出文件路径
        output_path, _ = QFileDialog.getSaveFileName(
            self, 
            '保存CSV文件', 
            'output.csv', 
            'CSV文件 (*.csv)'
        )
        
        if not output_path:
            return
            
        self.status_label.setText('正在转换PDF...')
        self.log("正在转换PDF...")
        
        try:
            # 导入核心模块
            from core.conversion import ConversionEngine
            
            # 调用核心功能
            converter = ConversionEngine()
            converter.pdf_to_csv(file_path, output_path)
            
            self.status_label.setText('PDF转CSV完成')
            self.log("PDF转CSV完成")
        except Exception as e:
            self.status_label.setText('PDF转CSV失败')
            self.log(f"PDF转CSV失败: {str(e)}")

    def edit_pdf(self):
        """编辑PDF"""
        self.status_label.setText('PDF编辑功能')
        self.log("执行PDF编辑功能")

    def secure_pdf(self):
        """安全处理PDF"""
        # 选择要处理的PDF文件
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            '选择要安全处理的PDF文件', 
            '', 
            'PDF文件 (*.pdf)'
        )
        
        if not file_path:
            return
            
        self.status_label.setText('准备安全处理PDF...')
        self.log("准备安全处理PDF...")
        
        # 创建安全处理选项对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("PDF安全处理选项")
        dialog.setGeometry(200, 200, 300, 200)
        
        layout = QVBoxLayout()
        
        # 处理类型选择
        type_label = QLabel("选择处理类型:")
        type_combo = QComboBox()
        type_combo.addItems(["加密PDF", "解密PDF", "添加水印"])
        
        # 密码输入（用于加密）
        password_label = QLabel("输入密码:")
        password_edit = QLineEdit()
        password_edit.setEchoMode(QLineEdit.Password)
        
        # 输出路径选择
        output_layout = QHBoxLayout()
        output_label = QLabel("输出路径:")
        output_edit = QLineEdit()
        output_button = QPushButton("浏览")
        
        def select_output():
            path, _ = QFileDialog.getSaveFileName(dialog, "保存处理后的PDF文件", "", "PDF文件 (*.pdf)")
            output_edit.setText(path)
            
        output_button.clicked.connect(select_output)
        
        output_layout.addWidget(output_label)
        output_layout.addWidget(output_edit)
        output_layout.addWidget(output_button)
        
        # 确定和取消按钮
        button_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        cancel_button = QPushButton("取消")
        
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        
        # 添加控件到布局
        layout.addWidget(type_label)
        layout.addWidget(type_combo)
        layout.addWidget(password_label)
        layout.addWidget(password_edit)
        layout.addLayout(output_layout)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        
        # 连接按钮事件
        ok_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)
        
        # 显示对话框
        if dialog.exec_() != QDialog.Accepted:
            return
            
        output_path = output_edit.text()
        password = password_edit.text()
        if not output_path:
            self.status_label.setText('未指定输出路径')
            self.log("未指定输出路径")
            return
            
        self.status_label.setText('正在安全处理PDF...')
        self.log("正在安全处理PDF...")
        
        try:
            # 根据处理类型导入相应的核心模块
            if type_combo.currentText() == "加密PDF":
                from core.security import SecurityEngine
                security = SecurityEngine()
                security.encrypt_pdf(file_path, output_path, password)
            elif type_combo.currentText() == "解密PDF":
                from core.security import SecurityEngine
                security = SecurityEngine()
                security.decrypt_pdf(file_path, output_path, password)
            elif type_combo.currentText() == "添加水印":
                from plugins.watermark import WatermarkPlugin
                watermark = WatermarkPlugin()
                watermark_text, ok = QInputDialog.getText(self, '水印文本', '请输入水印文本:')
                if ok and watermark_text:
                    watermark.add_watermark(file_path, output_path, watermark_text)
            
            self.status_label.setText('PDF安全处理完成')
            self.log("PDF安全处理完成")
        except Exception as e:
            self.status_label.setText('PDF安全处理失败')
            self.log(f"PDF安全处理失败: {str(e)}")

    def ocr_pdf(self):
        """OCR识别PDF"""
        self.status_label.setText('OCR识别功能')
        self.log("执行OCR识别功能")

    def add_watermark(self):
        """添加水印"""
        self.status_label.setText('添加水印功能')
        self.log("执行添加水印功能")

    def parse_page_range(self, page_range):
        """解析页面范围字符串为列表"""
        pages = []
        for part in page_range.split(','):
            part = part.strip()
            if '-' in part:
                start, end = part.split('-')
                pages.extend(range(int(start), int(end) + 1))
            else:
                pages.append(int(part))
        return pages

    def rotate_pages(self):
        """旋转页面"""
        # 选择要旋转的PDF文件
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            '选择要旋转的PDF文件', 
            '', 
            'PDF文件 (*.pdf)'
        )
        
        if not file_path:
            return
            
        # 输入旋转角度
        angle, ok = QInputDialog.getInt(self, '旋转角度', '请输入旋转角度 (90, 180, 270):', 90, 90, 270, 90)
        if not ok:
            return
            
        # 选择输出文件路径
        output_path, _ = QFileDialog.getSaveFileName(
            self, 
            '保存旋转后的PDF', 
            'rotated.pdf', 
            'PDF文件 (*.pdf)'
        )
        
        if not output_path:
            return
            
        self.status_label.setText('正在旋转页面...')
        self.log("正在旋转页面...")
        
        try:
            # 导入核心模块
            from core.editor import PDFEditor
            
            # 调用核心功能
            editor = PDFEditor()
            editor.rotate_pages(file_path, output_path, angle)
            
            self.status_label.setText('页面旋转完成')
            self.log("页面旋转完成")
        except Exception as e:
            self.status_label.setText('页面旋转失败')
            self.log(f"页面旋转失败: {str(e)}")

    def add_batch_task(self):
        """添加批量任务"""
        # 创建添加任务对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("添加批量任务")
        dialog.setGeometry(200, 200, 500, 400)
        
        layout = QVBoxLayout()
        
        # 任务名称
        name_layout = QHBoxLayout()
        name_label = QLabel("任务名称:")
        name_edit = QLineEdit()
        name_edit.setText("批量处理任务")
        name_layout.addWidget(name_label)
        name_layout.addWidget(name_edit)
        
        # 选择操作类型
        type_label = QLabel("操作类型:")
        type_combo = QComboBox()
        type_combo.addItems([
            "拆分PDF", "合并PDF", "旋转页面", "压缩PDF", "提取页面",
            "PDF转文本", "PDF转图像", "图像转PDF", "PDF转Word", "Word转PDF",
            "PDF转Excel", "Excel转PDF", "PDF转PPT", "PPT转PDF", "PDF转HTML",
            "PDF转CSV", "PDF转Markdown", "文本转PDF", "删除页面", "插入页面",
            "替换页面", "重排序页面", "添加水印", "裁剪页面", "加密PDF",
            "解密PDF", "数字签名", "移除密码", "OCR识别", "比较文档", "优化压缩"
        ])
        
        # 输入文件选择
        file_layout = QHBoxLayout()
        file_label = QLabel("输入文件:")
        file_edit = QLineEdit()
        file_button = QPushButton("浏览")
        
        def select_files():
            file_paths, _ = QFileDialog.getOpenFileNames(
                dialog, 
                '选择文件', 
                '', 
                'PDF文件 (*.pdf);;图像文件 (*.png *.jpg *.jpeg);;Word文件 (*.docx);;Excel文件 (*.xlsx);;PPT文件 (*.pptx);;文本文件 (*.txt)'
            )
            if file_paths:
                file_edit.setText("; ".join(file_paths))
                
        file_button.clicked.connect(select_files)
        file_layout.addWidget(file_label)
        file_layout.addWidget(file_edit)
        file_layout.addWidget(file_button)
        
        # 输出目录选择
        output_layout = QHBoxLayout()
        output_label = QLabel("输出目录:")
        output_edit = QLineEdit()
        output_button = QPushButton("浏览")
        
        def select_output():
            path = QFileDialog.getExistingDirectory(dialog, "选择输出目录")
            output_edit.setText(path)
            
        output_button.clicked.connect(select_output)
        output_layout.addWidget(output_label)
        output_layout.addWidget(output_edit)
        output_layout.addWidget(output_button)
        
        # 参数设置
        params_label = QLabel("参数设置:")
        params_edit = QTextEdit()
        params_edit.setMaximumHeight(100)
        params_edit.setPlaceholderText("设置操作参数，每行一个参数...")
        
        # 按钮
        button_layout = QHBoxLayout()
        ok_button = QPushButton("添加")
        cancel_button = QPushButton("取消")
        
        def add_task():
            task_name = name_edit.text()
            if not task_name:
                task_name = "未命名任务"
                
            task_type = type_combo.currentText()
            input_files = file_edit.text()
            output_dir = output_edit.text()
            
            # 添加到任务表格
            row = self.task_table.rowCount()
            self.task_table.insertRow(row)
            
            # 创建任务项
            self.task_table.setItem(row, 0, QTableWidgetItem(task_name))
            self.task_table.setItem(row, 1, QTableWidgetItem("待处理"))
            
            # 进度条
            progress = QProgressBar()
            progress.setValue(0)
            self.task_table.setCellWidget(row, 2, progress)
            
            # 保存任务信息
            task_info = {
                "name": task_name,
                "type": task_type,
                "input_files": input_files,
                "output_dir": output_dir,
                "params": params_edit.toPlainText().splitlines(),
                "progress": progress
            }
            self.tasks.append(task_info)
            
            self.status_label.setText(f'任务"{task_name}"已添加')
            self.log(f'任务"{task_name}"已添加')
            
        ok_button.clicked.connect(add_task)
        cancel_button.clicked.connect(dialog.reject)
        
        # 添加控件到布局
        layout.addLayout(name_layout)
        layout.addWidget(type_label)
        layout.addWidget(type_combo)
        layout.addLayout(file_layout)
        layout.addLayout(output_layout)
        layout.addWidget(params_label)
        layout.addWidget(params_edit)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        
        # 显示对话框
        dialog.exec_()
        
    def digital_signature(self):
        """数字签名"""
        # 检查数字签名依赖
        try:
            import pyhanko
        except ImportError as e:
            QMessageBox.critical(self, "依赖缺失", f"数字签名功能需要安装额外依赖: {str(e)}\n请运行: pip install pyhanko pyhanko-certvalidator")
            return
            
        # 选择要签名的PDF文件
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            '选择要签名的PDF文件', 
            '', 
            'PDF文件 (*.pdf)'
        )
        
        if not file_path:
            return
            
        # 选择证书文件
        cert_path, _ = QFileDialog.getOpenFileName(
            self, 
            '选择证书文件', 
            '', 
            '证书文件 (*.pem *.crt *.p12)'
        )
        
        if not cert_path:
            return
            
        # 选择私钥文件（如果证书不包含私钥）
        key_path, _ = QFileDialog.getOpenFileName(
            self, 
            '选择私钥文件（如需要）', 
            '', 
            '私钥文件 (*.pem *.key)'
        )
        
        # 输入签名密码
        password, ok = QInputDialog.getText(self, '证书密码', '请输入证书密码（如需要）:', QLineEdit.Password)
        if not ok:
            password = None
            
        # 选择输出文件路径
        output_path, _ = QFileDialog.getSaveFileName(
            self, 
            '保存签名后的PDF', 
            'signed.pdf', 
            'PDF文件 (*.pdf)'
        )
        
        if not output_path:
            return
            
        self.status_label.setText('正在添加数字签名...')
        self.log("正在添加数字签名...")
        
        try:
            # 导入核心模块
            from core.security import SecurityEngine
            
            # 调用核心功能
            security = SecurityEngine()
            security.add_digital_signature(file_path, output_path, cert_path, key_path, password)
            
            self.status_label.setText('数字签名添加成功')
            self.log("数字签名添加成功")
            QMessageBox.information(self, "成功", "数字签名已成功添加到PDF文件！")
        except Exception as e:
            self.status_label.setText('数字签名添加失败')
            self.log(f"数字签名添加失败: {str(e)}")
            QMessageBox.critical(self, "错误", f"数字签名添加失败: {str(e)}")

    def remove_password(self):
        """移除密码"""
        # 选择要解密的PDF文件
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            '选择要移除密码的PDF文件', 
            '', 
            'PDF文件 (*.pdf)'
        )
        
        if not file_path:
            return
            
        # 输入当前密码
        password, ok = QInputDialog.getText(self, '输入当前密码', '请输入当前密码:', QLineEdit.Password)
        if not ok or not password:
            return
            
        # 选择输出文件路径
        output_path, _ = QFileDialog.getSaveFileName(
            self, 
            '保存无密码的PDF', 
            'unprotected.pdf', 
            'PDF文件 (*.pdf)'
        )
        
        if not output_path:
            return
            
        self.status_label.setText('正在移除密码...')
        self.log("正在移除密码...")
        
        try:
            # 导入核心模块
            from core.security import SecurityEngine
            
            # 调用核心功能
            security = SecurityEngine()
            security.remove_password(file_path, output_path, password)
            
            self.status_label.setText('密码移除成功')
            self.log("密码移除成功")
            QMessageBox.information(self, "成功", "PDF密码已成功移除！")
        except Exception as e:
            self.status_label.setText('密码移除失败')
            self.log(f"密码移除失败: {str(e)}")
            QMessageBox.critical(self, "错误", f"密码移除失败: {str(e)}")

    def optimize_compression(self):
        """优化压缩"""
        # 选择要压缩的PDF文件
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            '选择要压缩的PDF文件', 
            '', 
            'PDF文件 (*.pdf)'
        )
        
        if not file_path:
            return
            
        # 选择压缩级别
        compression_level, ok = QInputDialog.getItem(
            self, 
            '选择压缩级别', 
            '压缩级别:', 
            ['low', 'medium', 'high'], 
            1,  # 默认选择medium
            False
        )
        if not ok:
            return
            
        # 选择输出文件路径
        output_path, _ = QFileDialog.getSaveFileName(
            self, 
            '保存压缩后的PDF', 
            'compressed.pdf', 
            'PDF文件 (*.pdf)'
        )
        
        if not output_path:
            return
            
        self.status_label.setText('正在优化压缩...')
        self.log("正在优化压缩...")
        
        try:
            # 导入核心模块
            from core.optimization import OptimizationEngine
            
            # 调用核心功能
            optimizer = OptimizationEngine()
            optimizer.compress_pdf(file_path, output_path, compression_level)
            
            self.status_label.setText('优化压缩完成')
            self.log("优化压缩完成")
            QMessageBox.information(self, "成功", "PDF优化压缩已完成！")
        except Exception as e:
            self.status_label.setText('优化压缩失败')
            self.log(f"优化压缩失败: {str(e)}")
            QMessageBox.critical(self, "错误", f"优化压缩失败: {str(e)}")

    def compare_documents(self):
        """比较文档"""
        # 选择第一个PDF文件
        file1_path, _ = QFileDialog.getOpenFileName(
            self, 
            '选择第一个PDF文件', 
            '', 
            'PDF文件 (*.pdf)'
        )
        
        if not file1_path:
            return
            
        # 选择第二个PDF文件
        file2_path, _ = QFileDialog.getOpenFileName(
            self, 
            '选择第二个PDF文件', 
            '', 
            'PDF文件 (*.pdf)'
        )
        
        if not file2_path:
            return
            
        self.status_label.setText('正在比较文档...')
        self.log("正在比较文档...")
        
        try:
            # 导入核心模块
            from core.comparison import ComparisonEngine
            
            # 调用核心功能
            comparison = ComparisonEngine()
            result = comparison.compare_documents(file1_path, file2_path)
            
            # 选择报告输出路径
            report_path, _ = QFileDialog.getSaveFileName(
                self, 
                '保存比较报告', 
                'comparison_report.txt', 
                '文本文件 (*.txt)'
            )
            
            if report_path:
                comparison.save_report_as_text(result, report_path)
                self.log(f"比较报告已保存: {report_path}")
            
            # 显示比较结果
            self.status_label.setText('文档比较完成')
            self.log("文档比较完成")
            
            # 构建结果消息
            msg = f"文档比较完成:\n"
            msg += f"页面数差异: {result['page_count_different']}\n"
            msg += f"文档1页面数: {result['page_count']['pdf1']}\n"
            msg += f"文档2页面数: {result['page_count']['pdf2']}\n"
            msg += f"文本差异页数: {len(result['text_differences'])}\n"
            
            QMessageBox.information(self, "比较完成", msg)
        except Exception as e:
            self.status_label.setText('文档比较失败')
            self.log(f"文档比较失败: {str(e)}")
            QMessageBox.critical(self, "错误", f"文档比较失败: {str(e)}")

    def optimize_compression(self):
        """优化压缩"""
        # 选择要压缩的PDF文件
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            '选择要优化压缩的PDF文件', 
            '', 
            'PDF文件 (*.pdf)'
        )
        
        if not file_path:
            return
            
        # 创建压缩选项对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("优化压缩选项")
        dialog.setGeometry(200, 200, 400, 300)
        
        layout = QVBoxLayout()
        
        # 压缩算法选择
        algorithm_label = QLabel("选择压缩算法:")
        algorithm_combo = QComboBox()
        algorithm_combo.addItems([
            "通用压缩", 
            "MRC压缩 (适合扫描文档)", 
            "JBIG2压缩 (适合黑白图像)", 
            "JPEG2000压缩 (适合彩色图像)"
        ])
        algorithm_combo.setCurrentText("通用压缩")
        
        # 质量设置
        quality_label = QLabel("选择压缩质量:")
        quality_combo = QComboBox()
        quality_combo.addItems(["高（质量优先）", "中（平衡）", "低（大小优先）"])
        quality_combo.setCurrentText("中（平衡）")
        
        # 输出路径选择
        output_label = QLabel("输出文件路径:")
        output_path_edit = QLineEdit()
        output_path_edit.setText(file_path.replace(".pdf", "_compressed.pdf"))
        browse_button = QPushButton("浏览...")
        
        def browse_output():
            path, _ = QFileDialog.getSaveFileName(
                self, 
                '保存压缩后的PDF', 
                output_path_edit.text(), 
                'PDF文件 (*.pdf)'
            )
            if path:
                output_path_edit.setText(path)
                
        browse_button.clicked.connect(browse_output)
        
        # 确定和取消按钮
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        
        # 添加控件到布局
        layout.addWidget(algorithm_label)
        layout.addWidget(algorithm_combo)
        layout.addWidget(quality_label)
        layout.addWidget(quality_combo)
        layout.addWidget(output_label)
        layout.addWidget(output_path_edit)
        layout.addWidget(browse_button)
        layout.addWidget(button_box)
        
        dialog.setLayout(layout)
        
        # 显示对话框
        if dialog.exec_() != QDialog.Accepted:
            return
            
        output_path = output_path_edit.text()
        if not output_path:
            return
            
        algorithm = algorithm_combo.currentText()
        quality = quality_combo.currentText()
        
        self.status_label.setText('正在优化压缩...')
        self.log("正在优化压缩...")
        
        try:
            # 导入核心模块
            from core.optimization import OptimizationEngine
            
            # 调用核心功能
            optimizer = OptimizationEngine()
            
            # 根据选择的算法和质量进行压缩
            if algorithm == "通用压缩":
                compression_level = "high" if quality == "低（大小优先）" else "medium" if quality == "中（平衡）" else "low"
                optimizer.compress_pdf(file_path, output_path, compression_level)
            elif algorithm == "MRC压缩 (适合扫描文档)":
                optimizer.mrc_compress(file_path, output_path)
            elif algorithm == "JBIG2压缩 (适合黑白图像)":
                optimizer.jbig2_compress(file_path, output_path)
            elif algorithm == "JPEG2000压缩 (适合彩色图像)":
                quality_value = 20 if quality == "低（大小优先）" else 50 if quality == "中（平衡）" else 85
                optimizer.jpeg2000_compress(file_path, output_path, quality_value)
            else:
                # 默认使用通用压缩
                compression_level = "medium"
                optimizer.compress_pdf(file_path, output_path, compression_level)
            
            self.status_label.setText('优化压缩完成')
            self.log("优化压缩完成")
            QMessageBox.information(self, "压缩完成", f"PDF优化压缩已完成，文件已保存到: {output_path}")
        except Exception as e:
            self.status_label.setText('优化压缩失败')
            self.log(f"优化压缩失败: {str(e)}")
            QMessageBox.critical(self, "错误", f"优化压缩失败: {str(e)}")

    def compress_pdf(self):
        """压缩PDF"""
        # 选择要压缩的PDF文件
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            '选择要压缩的PDF文件', 
            '', 
            'PDF文件 (*.pdf)'
        )
        
        if not file_path:
            return
            
        self.status_label.setText('准备压缩PDF...')
        self.log("准备压缩PDF...")
        
        # 创建压缩选项对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("压缩选项")
        dialog.setGeometry(200, 200, 400, 250)
        
        layout = QVBoxLayout()
        
        # 压缩级别选择
        level_label = QLabel("选择压缩级别:")
        level_combo = QComboBox()
        level_combo.addItems(["低（质量优先）", "中（平衡）", "高（大小优先）"])
        level_combo.setCurrentText("中（平衡）")
        
        # 输出路径选择
        output_layout = QHBoxLayout()
        output_label = QLabel("输出文件:")
        output_edit = QLineEdit()
        output_button = QPushButton("浏览")
        
        # 设置默认输出路径
        default_output = file_path.replace(".pdf", "_compressed.pdf")
        output_edit.setText(default_output)
        
        def select_output():
            path, _ = QFileDialog.getSaveFileName(
                dialog, 
                '保存压缩后的PDF文件', 
                default_output, 
                'PDF文件 (*.pdf)'
            )
            if path:
                output_edit.setText(path)
                
        output_button.clicked.connect(select_output)
        
        output_layout.addWidget(output_label)
        output_layout.addWidget(output_edit)
        output_layout.addWidget(output_button)
        
        # 确定和取消按钮
        button_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        cancel_button = QPushButton("取消")
        
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        
        # 添加控件到布局
        layout.addWidget(level_label)
        layout.addWidget(level_combo)
        layout.addLayout(output_layout)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        
        # 连接按钮事件
        def execute_compression():
            output_path = output_edit.text()
            if not output_path:
                self.status_label.setText('未指定输出文件')
                self.log("未指定输出文件")
                return
                
            self.status_label.setText('正在压缩PDF...')
            self.log("正在压缩PDF...")
            dialog.accept()
            
            try:
                # 解析压缩级别
                level_text = level_combo.currentText()
                compression_level = "medium"
                if "低" in level_text:
                    compression_level = "low"
                elif "高" in level_text:
                    compression_level = "high"
                
                # 导入核心模块
                from core.optimization import OptimizationEngine
                
                # 调用核心功能
                optimizer = OptimizationEngine()
                optimizer.compress_pdf(file_path, output_path, compression_level)
                
                self.status_label.setText('PDF压缩完成')
                self.log("PDF压缩完成")
            except Exception as e:
                self.status_label.setText('PDF压缩失败')
                self.log(f"PDF压缩失败: {str(e)}")
        
        ok_button.clicked.connect(execute_compression)
        cancel_button.clicked.connect(dialog.reject)
        
        # 显示对话框
        dialog.exec_()
        
    def extract_pages(self):
        """提取页面"""
        # 选择要提取页面的PDF文件
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            '选择要提取页面的PDF文件', 
            '', 
            'PDF文件 (*.pdf)'
        )
        
        if not file_path:
            return
            
        self.status_label.setText('准备提取PDF页面...')
        self.log("准备提取PDF页面...")
        
        # 创建提取选项对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("提取页面选项")
        dialog.setGeometry(200, 200, 400, 250)
        
        layout = QVBoxLayout()
        
        # 页面范围输入
        range_label = QLabel("页面范围 (例如: 1-3,5,7-10):")
        range_edit = QLineEdit()
        range_edit.setPlaceholderText("留空表示所有页面")
        
        # 输出路径选择
        output_layout = QHBoxLayout()
        output_label = QLabel("输出文件:")
        output_edit = QLineEdit()
        output_button = QPushButton("浏览")
        
        # 设置默认输出路径
        default_output = file_path.replace(".pdf", "_extracted.pdf")
        output_edit.setText(default_output)
        
        def select_output():
            path, _ = QFileDialog.getSaveFileName(
                dialog, 
                '保存提取后的PDF文件', 
                default_output, 
                'PDF文件 (*.pdf)'
            )
            if path:
                output_edit.setText(path)
                
        output_button.clicked.connect(select_output)
        
        output_layout.addWidget(output_label)
        output_layout.addWidget(output_edit)
        output_layout.addWidget(output_button)
        
        # 确定和取消按钮
        button_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        cancel_button = QPushButton("取消")
        
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        
        # 添加控件到布局
        layout.addWidget(range_label)
        layout.addWidget(range_edit)
        layout.addLayout(output_layout)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        
        # 连接按钮事件
        def execute_extraction():
            output_path = output_edit.text()
            if not output_path:
                self.status_label.setText('未指定输出文件')
                self.log("未指定输出文件")
                return
                
            self.status_label.setText('正在提取PDF页面...')
            self.log("正在提取PDF页面...")
            dialog.accept()
            
            try:
                # 解析页面范围
                page_range = range_edit.text().strip()
                
                # 导入核心模块
                from core.editor import PDFEditor
                
                # 调用核心功能
                editor = PDFEditor()
                editor.extract_pages(file_path, output_path, page_range)
                
                self.status_label.setText('PDF页面提取完成')
                self.log("PDF页面提取完成")
            except Exception as e:
                self.status_label.setText('PDF页面提取失败')
                self.log(f"PDF页面提取失败: {str(e)}")
        
        ok_button.clicked.connect(execute_extraction)
        cancel_button.clicked.connect(dialog.reject)
        
        # 显示对话框
        dialog.exec_()

    def rotate_pages(self):
        """旋转页面"""
        # 选择要旋转的PDF文件
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            '选择要旋转的PDF文件', 
            '', 
            'PDF文件 (*.pdf)'
        )
        
        if not file_path:
            return
            
        self.status_label.setText('准备旋转PDF页面...')
        self.log("准备旋转PDF页面...")
        
        # 创建旋转选项对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("旋转页面选项")
        dialog.setGeometry(200, 200, 400, 300)
        
        layout = QVBoxLayout()
        
        # 旋转角度选择
        angle_label = QLabel("选择旋转角度:")
        angle_combo = QComboBox()
        angle_combo.addItems(["90度", "180度", "270度"])
        
        # 页面范围输入
        range_label = QLabel("页面范围 (例如: 1-3,5,7-10):")
        range_edit = QLineEdit()
        range_edit.setPlaceholderText("留空表示所有页面")
        
        # 输出路径选择
        output_layout = QHBoxLayout()
        output_label = QLabel("输出文件:")
        output_edit = QLineEdit()
        output_button = QPushButton("浏览")
        
        # 设置默认输出路径
        default_output = file_path.replace(".pdf", "_rotated.pdf")
        output_edit.setText(default_output)
        
        def select_output():
            path, _ = QFileDialog.getSaveFileName(
                dialog, 
                '保存旋转后的PDF文件', 
                default_output, 
                'PDF文件 (*.pdf)'
            )
            if path:
                output_edit.setText(path)
                
        output_button.clicked.connect(select_output)
        
        output_layout.addWidget(output_label)
        output_layout.addWidget(output_edit)
        output_layout.addWidget(output_button)
        
        # 确定和取消按钮
        button_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        cancel_button = QPushButton("取消")
        
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        
        # 添加控件到布局
        layout.addWidget(angle_label)
        layout.addWidget(angle_combo)
        layout.addWidget(range_label)
        layout.addWidget(range_edit)
        layout.addLayout(output_layout)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        
        # 连接按钮事件
        def execute_rotation():
            output_path = output_edit.text()
            if not output_path:
                self.status_label.setText('未指定输出文件')
                self.log("未指定输出文件")
                return
                
            self.status_label.setText('正在旋转PDF页面...')
            self.log("正在旋转PDF页面...")
            dialog.accept()
            
            try:
                # 解析旋转角度
                angle_text = angle_combo.currentText()
                angle = 0
                if angle_text == "90度":
                    angle = 90
                elif angle_text == "180度":
                    angle = 180
                elif angle_text == "270度":
                    angle = 270
                
                # 解析页面范围
                page_range = range_edit.text().strip()
                
                # 导入核心模块
                from core.editor import PDFEditor
                
                # 调用核心功能
                editor = PDFEditor()
                editor.rotate_pages(file_path, output_path, angle, page_range)
                
                self.status_label.setText('PDF页面旋转完成')
                self.log("PDF页面旋转完成")
            except Exception as e:
                self.status_label.setText('PDF页面旋转失败')
                self.log(f"PDF页面旋转失败: {str(e)}")
        
        ok_button.clicked.connect(execute_rotation)
        cancel_button.clicked.connect(dialog.reject)
        
        # 显示对话框
        dialog.exec_()
        
    def pdf_to_text(self):
        """PDF转文本"""
        # 选择要转换的PDF文件
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            '选择要转换为文本的PDF文件', 
            '', 
            'PDF文件 (*.pdf)'
        )
        
        if not file_path:
            return
            
        self.status_label.setText('准备转换PDF为文本...')
        self.log("准备转换PDF为文本...")
        
    def ocr_pdf(self):
        """OCR识别"""
        # 选择要进行OCR的PDF文件
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            '选择要进行OCR识别的PDF文件', 
            '', 
            'PDF文件 (*.pdf)'
        )
        
        if not file_path:
            return
            
        self.status_label.setText('准备进行OCR识别...')
        self.log("准备进行OCR识别...")
        
        # 创建OCR选项对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("OCR选项")
        dialog.setGeometry(200, 200, 400, 300)
        
        layout = QVBoxLayout()
        
        # 语言选择
        lang_label = QLabel("选择OCR语言:")
        lang_combo = QComboBox()
        lang_combo.addItems(["中文", "英文", "中英文混合"])
        lang_combo.setCurrentText("中英文混合")
        
        # 输出格式选择
        format_label = QLabel("选择输出格式:")
        format_combo = QComboBox()
        format_combo.addItems(["PDF", "文本文件", "Word文档"])
        format_combo.setCurrentText("PDF")
        
        # 输出路径选择
        output_layout = QHBoxLayout()
        output_label = QLabel("输出文件:")
        output_edit = QLineEdit()
        output_button = QPushButton("浏览")
        
        # 设置默认输出路径
        default_ext = ".pdf"
        if format_combo.currentText() == "文本文件":
            default_ext = ".txt"
        elif format_combo.currentText() == "Word文档":
            default_ext = ".docx"
            
        default_output = file_path.replace(".pdf", "_ocr" + default_ext)
        output_edit.setText(default_output)
        
        def update_default_output():
            ext = ".pdf"
            if format_combo.currentText() == "文本文件":
                ext = ".txt"
            elif format_combo.currentText() == "Word文档":
                ext = ".docx"
            new_output = file_path.replace(".pdf", "_ocr" + ext)
            output_edit.setText(new_output)
            
        format_combo.currentTextChanged.connect(update_default_output)
        
        def select_output():
            filter_str = "PDF文件 (*.pdf)"
            if format_combo.currentText() == "文本文件":
                filter_str = "文本文件 (*.txt)"
            elif format_combo.currentText() == "Word文档":
                filter_str = "Word文档 (*.docx)"
                
            path, _ = QFileDialog.getSaveFileName(
                dialog, 
                '保存OCR结果', 
                default_output, 
                filter_str
            )
            if path:
                output_edit.setText(path)
                
        output_button.clicked.connect(select_output)
        
        output_layout.addWidget(output_label)
        output_layout.addWidget(output_edit)
        output_layout.addWidget(output_button)
        
        # 确定和取消按钮
        button_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        cancel_button = QPushButton("取消")
        
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        
        # 添加控件到布局
        layout.addWidget(lang_label)
        layout.addWidget(lang_combo)
        layout.addWidget(format_label)
        layout.addWidget(format_combo)
        layout.addLayout(output_layout)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        
        # 连接按钮事件
        def execute_ocr():
            output_path = output_edit.text()
            if not output_path:
                self.status_label.setText('未指定输出文件')
                self.log("未指定输出文件")
                return
                
            self.status_label.setText('正在进行OCR识别...')
            self.log("正在进行OCR识别...")
            dialog.accept()
            
            try:
                # 解析语言参数
                lang = "chi_sim+eng"  # 默认中英文混合
                if lang_combo.currentText() == "中文":
                    lang = "chi_sim"
                elif lang_combo.currentText() == "英文":
                    lang = "eng"
                
                # 解析输出格式
                output_format = "pdf"
                if format_combo.currentText() == "文本文件":
                    output_format = "text"
                elif format_combo.currentText() == "Word文档":
                    output_format = "docx"
                
                # 导入核心模块
                from core.ocr import OCREngine
                
                # 调用核心功能
                ocr_engine = OCREngine()
                ocr_engine.perform_ocr(file_path, output_path, lang, output_format)
                
                self.status_label.setText('OCR识别完成')
                self.log("OCR识别完成")
            except Exception as e:
                self.status_label.setText('OCR识别失败')
                self.log(f"OCR识别失败: {str(e)}")
        
        ok_button.clicked.connect(execute_ocr)
        cancel_button.clicked.connect(dialog.reject)
        
        # 显示对话框
        dialog.exec_()
        
    def compare_documents(self):
        
        # 创建转换选项对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("PDF转文本选项")
        dialog.setGeometry(200, 200, 400, 300)
        
        layout = QVBoxLayout()
        
        # 页面范围输入
        range_label = QLabel("页面范围 (例如: 1-3,5,7-10):")
        range_edit = QLineEdit()
        range_edit.setPlaceholderText("留空表示所有页面")
        
        # 输出路径选择
        output_layout = QHBoxLayout()
        output_label = QLabel("输出文件:")
        output_edit = QLineEdit()
        output_button = QPushButton("浏览")
        
        # 设置默认输出路径
        default_output = file_path.replace(".pdf", ".txt")
        output_edit.setText(default_output)
        
        def select_output():
            path, _ = QFileDialog.getSaveFileName(
                dialog, 
                '保存转换后的文本文件', 
                default_output, 
                '文本文件 (*.txt)'
            )
            if path:
                output_edit.setText(path)
                
        output_button.clicked.connect(select_output)
        
        output_layout.addWidget(output_label)
        output_layout.addWidget(output_edit)
        output_layout.addWidget(output_button)
        
        # 确定和取消按钮
        button_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        cancel_button = QPushButton("取消")
        
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        
        # 添加控件到布局
        layout.addWidget(range_label)
        layout.addWidget(range_edit)
        layout.addLayout(output_layout)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        
        # 连接按钮事件
        def execute_conversion():
            output_path = output_edit.text()
            if not output_path:
                self.status_label.setText('未指定输出文件')
                self.log("未指定输出文件")
                return
                
            self.status_label.setText('正在转换PDF为文本...')
            self.log("正在转换PDF为文本...")
            dialog.accept()
            
            try:
                # 解析页面范围
                page_range = range_edit.text().strip()
                
                # 导入核心模块
                from core.converter import PDFConverter
                
                # 调用核心功能
                converter = PDFConverter()
                converter.pdf_to_text(file_path, output_path, page_range)
                
                self.status_label.setText('PDF转文本完成')
                self.log("PDF转文本完成")
            except Exception as e:
                self.status_label.setText('PDF转文本失败')
                self.log(f"PDF转文本失败: {str(e)}")
        
        ok_button.clicked.connect(execute_conversion)
        cancel_button.clicked.connect(dialog.reject)
        
        # 显示对话框
        dialog.exec_()
        
    def add_watermark(self):
        """添加水印"""
        # 选择要添加水印的PDF文件
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            '选择要添加水印的PDF文件', 
            '', 
            'PDF文件 (*.pdf)'
        )
        
        if not file_path:
            return
            
        self.status_label.setText('准备添加水印...')
        self.log("准备添加水印...")
        
        # 创建水印选项对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("水印选项")
        dialog.setGeometry(200, 200, 400, 350)
        
        layout = QVBoxLayout()
        
        # 水印类型选择
        type_label = QLabel("选择水印类型:")
        type_combo = QComboBox()
        type_combo.addItems(["文本水印", "图片水印"])
        
        # 文本水印参数
        text_group = QGroupBox("文本水印参数")
        text_layout = QVBoxLayout()
        text_edit = QLineEdit()
        text_edit.setPlaceholderText("输入水印文本")
        text_layout.addWidget(text_edit)
        
        # 字体大小
        font_size_layout = QHBoxLayout()
        font_size_label = QLabel("字体大小:")
        font_size_spin = QSpinBox()
        font_size_spin.setRange(10, 100)
        font_size_spin.setValue(50)
        font_size_layout.addWidget(font_size_label)
        font_size_layout.addWidget(font_size_spin)
        text_layout.addLayout(font_size_layout)
        
        # 透明度
        opacity_layout = QHBoxLayout()
        opacity_label = QLabel("透明度:")
        opacity_spin = QSpinBox()
        opacity_spin.setRange(1, 100)
        opacity_spin.setValue(50)
        opacity_layout.addWidget(opacity_label)
        opacity_layout.addWidget(opacity_spin)
        text_layout.addLayout(opacity_layout)
        
        text_group.setLayout(text_layout)
        
        # 图片水印参数
        image_group = QGroupBox("图片水印参数")
        image_layout = QVBoxLayout()
        image_edit = QLineEdit()
        image_edit.setPlaceholderText("选择水印图片文件")
        image_button = QPushButton("浏览")
        
        def select_image():
            path, _ = QFileDialog.getOpenFileName(
                dialog, 
                '选择水印图片', 
                '', 
                '图片文件 (*.png *.jpg *.jpeg *.bmp)'
            )
            if path:
                image_edit.setText(path)
                
        image_button.clicked.connect(select_image)
        image_layout.addWidget(image_edit)
        image_layout.addWidget(image_button)
        image_group.setLayout(image_layout)
        
        # 输出路径选择
        output_layout = QHBoxLayout()
        output_label = QLabel("输出文件:")
        output_edit = QLineEdit()
        output_button = QPushButton("浏览")
        
        # 设置默认输出路径
        default_output = file_path.replace(".pdf", "_watermarked.pdf")
        output_edit.setText(default_output)
        
        def select_output():
            path, _ = QFileDialog.getSaveFileName(
                dialog, 
                '保存添加水印后的PDF文件', 
                default_output, 
                'PDF文件 (*.pdf)'
            )
            if path:
                output_edit.setText(path)
                
        output_button.clicked.connect(select_output)
        
        output_layout.addWidget(output_label)
        output_layout.addWidget(output_edit)
        output_layout.addWidget(output_button)
        
        # 确定和取消按钮
        button_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        cancel_button = QPushButton("取消")
        
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        
        # 添加控件到布局
        layout.addWidget(type_label)
        layout.addWidget(type_combo)
        layout.addWidget(text_group)
        layout.addWidget(image_group)
        layout.addLayout(output_layout)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        
        # 初始状态设置
        def update_ui():
            is_text = type_combo.currentText() == "文本水印"
            text_group.setVisible(is_text)
            image_group.setVisible(not is_text)
            
        type_combo.currentTextChanged.connect(update_ui)
        update_ui()  # 初始化状态
        
        # 连接按钮事件
        def execute_watermark():
            output_path = output_edit.text()
            if not output_path:
                self.status_label.setText('未指定输出文件')
                self.log("未指定输出文件")
                return
                
            self.status_label.setText('正在添加水印...')
            self.log("正在添加水印...")
            dialog.accept()
            
            try:
                # 导入核心模块
                from plugins.watermark import WatermarkPlugin
                
                # 调用核心功能
                watermark_plugin = WatermarkPlugin()
                
                if type_combo.currentText() == "文本水印":
                    text = text_edit.text()
                    if not text:
                        raise Exception("请输入水印文本")
                    font_size = font_size_spin.value()
                    opacity = opacity_spin.value() / 100.0
                    watermark_plugin.add_text_watermark(file_path, output_path, text, font_size, opacity)
                else:
                    image_path = image_edit.text()
                    if not image_path:
                        raise Exception("请选择水印图片")
                    watermark_plugin.add_image_watermark(file_path, output_path, image_path)
                
                self.status_label.setText('水印添加完成')
                self.log("水印添加完成")
            except Exception as e:
                self.status_label.setText('水印添加失败')
                self.log(f"水印添加失败: {str(e)}")
        
        ok_button.clicked.connect(execute_watermark)
        cancel_button.clicked.connect(dialog.reject)
        
        # 显示对话框
        dialog.exec_()
        
    def crop_pages(self):
        """裁剪页面"""
        # 选择要裁剪的PDF文件
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            '选择要裁剪的PDF文件', 
            '', 
            'PDF文件 (*.pdf)'
        )
        
        if not file_path:
            return
            
        self.status_label.setText('准备裁剪PDF页面...')
        self.log("准备裁剪PDF页面...")
        
        # 创建裁剪选项对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("裁剪页面选项")
        dialog.setGeometry(200, 200, 400, 300)
        
        layout = QVBoxLayout()
        
        # 裁剪区域输入
        crop_label = QLabel("裁剪区域 (例如: 100,100,300,300):")
        crop_edit = QLineEdit()
        crop_edit.setPlaceholderText("输入裁剪区域坐标")
        
        # 页面范围输入
        range_label = QLabel("页面范围 (例如: 1-3,5,7-10):")
        range_edit = QLineEdit()
        range_edit.setPlaceholderText("留空表示所有页面")
        
        # 输出路径选择
        output_layout = QHBoxLayout()
        output_label = QLabel("输出文件:")
        output_edit = QLineEdit()
        output_button = QPushButton("浏览")
        
        # 设置默认输出路径
        default_output = file_path.replace(".pdf", "_cropped.pdf")
        output_edit.setText(default_output)
        
        def select_output():
            path, _ = QFileDialog.getSaveFileName(
                dialog, 
                '保存裁剪后的PDF文件', 
                default_output, 
                'PDF文件 (*.pdf)'
            )
            if path:
                output_edit.setText(path)
                
        output_button.clicked.connect(select_output)
        
        output_layout.addWidget(output_label)
        output_layout.addWidget(output_edit)
        output_layout.addWidget(output_button)
        
        # 确定和取消按钮
        button_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        cancel_button = QPushButton("取消")
        
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        
        # 添加控件到布局
        layout.addWidget(crop_label)
        layout.addWidget(crop_edit)
        layout.addWidget(range_label)
        layout.addWidget(range_edit)
        layout.addLayout(output_layout)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        
        # 连接按钮事件
        def execute_cropping():
            output_path = output_edit.text()
            if not output_path:
                self.status_label.setText('未指定输出文件')
                self.log("未指定输出文件")
                return
                
            self.status_label.setText('正在裁剪PDF页面...')
            self.log("正在裁剪PDF页面...")
            dialog.accept()
            
            try:
                # 解析页面范围
                page_range = range_edit.text().strip()
                
                # 导入核心模块
                from core.converter import PDFConverter
                
                # 调用核心功能
                converter = PDFConverter()
                converter.pdf_to_text(file_path, output_path, page_range)
                
                self.status_label.setText('PDF转换为文本完成')
                self.log("PDF转换为文本完成")
            except Exception as e:
                self.status_label.setText('PDF转换为文本失败')
                self.log(f"PDF转换为文本失败: {str(e)}")
        
        ok_button.clicked.connect(execute_conversion)
        cancel_button.clicked.connect(dialog.reject)
        
        # 显示对话框
        dialog.exec_()

    def split_pdf(self):
        """拆分PDF"""
        # 选择要拆分的PDF文件
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            '选择要拆分的PDF文件', 
            '', 
            'PDF文件 (*.pdf)'
        )
        
        if not file_path:
            return
            
        self.status_label.setText('准备拆分PDF...')
        self.log("准备拆分PDF...")
        
        # 创建拆分选项对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("拆分选项")
        dialog.setGeometry(200, 200, 400, 300)
        
        layout = QVBoxLayout()
        
        # 拆分方式选择
        method_label = QLabel("选择拆分方式:")
        method_combo = QComboBox()
        method_combo.addItems([
            "按固定页数拆分", 
            "按页码范围拆分", 
            "首页与末页配对拆分"
        ])
        
        # 参数输入
        param_label = QLabel("参数 (例如: 5 表示每5页拆分一次):")
        param_edit = QLineEdit()
        param_edit.setPlaceholderText("输入拆分参数")
        
        # 输出目录选择
        output_layout = QHBoxLayout()
        output_label = QLabel("输出目录:")
        output_edit = QLineEdit()
        output_button = QPushButton("浏览")
        
        # 设置默认输出目录
        default_output = os.path.dirname(file_path)
        output_edit.setText(default_output)
        
        def select_output():
            path = QFileDialog.getExistingDirectory(
                dialog, 
                '选择输出目录', 
                default_output
            )
            if path:
                output_edit.setText(path)
                
        output_button.clicked.connect(select_output)
        
        output_layout.addWidget(output_label)
        output_layout.addWidget(output_edit)
        output_layout.addWidget(output_button)
        
        # 确定和取消按钮
        button_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        cancel_button = QPushButton("取消")
        
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        
        # 添加控件到布局
        layout.addWidget(method_label)
        layout.addWidget(method_combo)
        layout.addWidget(param_label)
        layout.addWidget(param_edit)
        layout.addLayout(output_layout)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        
        # 连接按钮事件
        def execute_split():
            output_dir = output_edit.text()
            if not output_dir:
                self.status_label.setText('未指定输出目录')
                self.log("未指定输出目录")
                return
                
            self.status_label.setText('正在拆分PDF...')
            self.log("正在拆分PDF...")
            dialog.accept()
            
            try:
                # 获取拆分参数
                param = param_edit.text().strip()
                
                # 导入核心模块
                from core.pdf_engine import PDFEngine
                
                # 调用核心功能
                engine = PDFEngine()
                method = method_combo.currentText()
                
                if method == "按固定页数拆分":
                    if not param.isdigit():
                        raise Exception("请正确输入页数参数")
                    pages_per_split = int(param)
                    engine.split_by_pages(file_path, output_dir, pages_per_split)
                elif method == "按页码范围拆分":
                    if not param:
                        raise Exception("请输入页码范围参数")
                    engine.split_by_ranges(file_path, output_dir, param)
                elif method == "首页与末页配对拆分":
                    engine.split_first_last_pairs(file_path, output_dir)
                
                self.status_label.setText('PDF拆分完成')
                self.log("PDF拆分完成")
            except Exception as e:
                self.status_label.setText('PDF拆分失败')
                self.log(f"PDF拆分失败: {str(e)}")
        
        ok_button.clicked.connect(execute_split)
        cancel_button.clicked.connect(dialog.reject)
        
        # 显示对话框
        dialog.exec_()
        
    def merge_pdfs(self):
        """合并PDF"""
        # 选择要合并的PDF文件
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, 
            '选择要合并的PDF文件', 
            '', 
            'PDF文件 (*.pdf)'
        )
        
        if not file_paths:
            return
            
        self.status_label.setText('准备合并PDF...')
        self.log("准备合并PDF...")
        
        # 创建合并选项对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("合并选项")
        dialog.setGeometry(200, 200, 400, 300)
        
        layout = QVBoxLayout()
        
        # 输出路径选择
        output_layout = QHBoxLayout()
        output_label = QLabel("输出文件:")
        output_edit = QLineEdit()
        output_button = QPushButton("浏览")
        
        # 设置默认输出路径
        default_output = os.path.dirname(file_paths[0]) + "/merged.pdf"
        output_edit.setText(default_output)
        
        def select_output():
            path, _ = QFileDialog.getSaveFileName(
                dialog, 
                '保存合并后的PDF文件', 
                default_output, 
                'PDF文件 (*.pdf)'
            )
            if path:
                output_edit.setText(path)
                
        output_button.clicked.connect(select_output)
        
        output_layout.addWidget(output_label)
        output_layout.addWidget(output_edit)
        output_layout.addWidget(output_button)
        
        # 确定和取消按钮
        button_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        cancel_button = QPushButton("取消")
        
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        
        # 添加控件到布局
        layout.addLayout(output_layout)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        
        # 连接按钮事件
        def execute_merge():
            output_path = output_edit.text()
            if not output_path:
                self.status_label.setText('未指定输出文件')
                self.log("未指定输出文件")
                return
                
            self.status_label.setText('正在合并PDF...')
            self.log("正在合并PDF...")
            dialog.accept()
            
            try:
                # 导入核心模块
                from core.pdf_engine import PDFEngine
                
                # 调用核心功能
                engine = PDFEngine()
                engine.merge_pdfs(file_paths, output_path)
                
                self.status_label.setText('PDF合并完成')
                self.log("PDF合并完成")
            except Exception as e:
                self.status_label.setText('PDF合并失败')
                self.log(f"PDF合并失败: {str(e)}")
        
        ok_button.clicked.connect(execute_merge)
        cancel_button.clicked.connect(dialog.reject)
        
        # 显示对话框
        dialog.exec_()

    def insert_pages(self):
        """插入页面"""
        # 选择目标PDF文件
        target_file, _ = QFileDialog.getOpenFileName(
            self, 
            '选择要插入页面的目标PDF文件', 
            '', 
            'PDF文件 (*.pdf)'
        )
        
        if not target_file:
            return
            
        # 选择要插入的PDF文件
        insert_file, _ = QFileDialog.getOpenFileName(
            self, 
            '选择要插入的PDF文件', 
            '', 
            'PDF文件 (*.pdf)'
        )
        
        if not insert_file:
            return
            
        # 输入插入位置
        insert_position, ok = QInputDialog.getInt(self, '插入位置', '请输入插入位置 (页码):', 1, 1, 10000)
        if not ok:
            return
            
        # 选择输出文件路径
        output_path, _ = QFileDialog.getSaveFileName(
            self, 
            '保存插入页面后的PDF', 
            'inserted_pages.pdf', 
            'PDF文件 (*.pdf)'
        )
        
        if not output_path:
            return
            
        self.status_label.setText('正在插入页面...')
        self.log("正在插入页面...")
        
        try:
            # 导入核心模块
            from core.pdf_engine import PDFEngine
            
            # 调用核心功能
            engine = PDFEngine()
            engine.insert_pages(target_file, insert_file, output_path, insert_position)
            
            self.status_label.setText('页面插入成功')
            self.log("页面插入成功")
        except Exception as e:
            self.status_label.setText('页面插入失败')
            self.log(f"页面插入失败: {str(e)}")

    def convert_pdf(self):
        """格式转换"""
        # 创建转换选项对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("格式转换")
        dialog.setGeometry(200, 200, 400, 300)
        
        layout = QVBoxLayout()
        
        # 转换类型选择
        type_label = QLabel("选择转换类型:")
        type_combo = QComboBox()
        type_combo.addItems([
            "PDF转Word", "PDF转Excel", "PDF转PPT", "PDF转HTML", "PDF转文本",
            "PDF转图像", "图像转PDF", "Word转PDF", "Excel转PDF", "PPT转PDF"
        ])
        
        # 输入文件选择
        input_layout = QHBoxLayout()
        input_label = QLabel("输入文件:")
        input_edit = QLineEdit()
        input_button = QPushButton("浏览")
        
        def select_input():
            file_types = {
                "PDF转Word": "PDF文件 (*.pdf)",
                "PDF转Excel": "PDF文件 (*.pdf)",
                "PDF转PPT": "PDF文件 (*.pdf)",
                "PDF转HTML": "PDF文件 (*.pdf)",
                "PDF转文本": "PDF文件 (*.pdf)",
                "PDF转图像": "PDF文件 (*.pdf)",
                "图像转PDF": "图像文件 (*.png *.jpg *.jpeg *.bmp *.tiff)",
                "Word转PDF": "Word文件 (*.docx)",
                "Excel转PDF": "Excel文件 (*.xlsx)",
                "PPT转PDF": "PPT文件 (*.pptx)"
            }
            
            selected_type = type_combo.currentText()
            file_type = file_types.get(selected_type, "所有文件 (*.*)")
            
            path, _ = QFileDialog.getOpenFileName(
                dialog, 
                '选择输入文件', 
                '', 
                file_type
            )
            if path:
                input_edit.setText(path)
                
        input_button.clicked.connect(select_input)
        type_combo.currentTextChanged.connect(select_input)  # 当转换类型改变时更新文件选择
        
        input_layout.addWidget(input_label)
        input_layout.addWidget(input_edit)
        input_layout.addWidget(input_button)
        
        # 输出文件选择
        output_layout = QHBoxLayout()
        output_label = QLabel("输出文件:")
        output_edit = QLineEdit()
        output_button = QPushButton("浏览")
        
        def select_output():
            file_types = {
                "PDF转Word": "Word文件 (*.docx)",
                "PDF转Excel": "Excel文件 (*.xlsx)",
                "PDF转PPT": "PPT文件 (*.pptx)",
                "PDF转HTML": "HTML文件 (*.html)",
                "PDF转文本": "文本文件 (*.txt)",
                "PDF转图像": "图像文件 (*.png)",
                "图像转PDF": "PDF文件 (*.pdf)",
                "Word转PDF": "PDF文件 (*.pdf)",
                "Excel转PDF": "PDF文件 (*.pdf)",
                "PPT转PDF": "PDF文件 (*.pdf)"
            }
            
            selected_type = type_combo.currentText()
            file_type = file_types.get(selected_type, "所有文件 (*.*)")
            
            default_name = "output"
            if selected_type == "PDF转Word":
                default_name = "output.docx"
            elif selected_type == "PDF转Excel":
                default_name = "output.xlsx"
            elif selected_type == "PDF转PPT":
                default_name = "output.pptx"
            elif selected_type == "PDF转HTML":
                default_name = "output.html"
            elif selected_type == "PDF转文本":
                default_name = "output.txt"
            elif selected_type in ["PDF转图像", "图像转PDF"]:
                default_name = "output.pdf" if "图像转PDF" in selected_type else "output.png"
            elif "转PDF" in selected_type:
                default_name = "output.pdf"
                
            path, _ = QFileDialog.getSaveFileName(
                dialog, 
                '选择输出文件', 
                default_name, 
                file_type
            )
            if path:
                output_edit.setText(path)
                
        output_button.clicked.connect(select_output)
        
        output_layout.addWidget(output_label)
        output_layout.addWidget(output_edit)
        output_layout.addWidget(output_button)
        
        # 确定和取消按钮
        button_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        cancel_button = QPushButton("取消")
        
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        
        # 添加控件到布局
        layout.addWidget(type_label)
        layout.addWidget(type_combo)
        layout.addLayout(input_layout)
        layout.addLayout(output_layout)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        
        # 连接按钮事件
        def execute_conversion():
            input_path = input_edit.text()
            output_path = output_edit.text()
            
            if not input_path or not output_path:
                self.status_label.setText('请指定输入和输出文件')
                self.log("请指定输入和输出文件")
                return
                
            self.status_label.setText('正在执行格式转换...')
            self.log("正在执行格式转换...")
            dialog.accept()
            
            try:
                # 导入核心模块
                from core.conversion import ConversionEngine
                
                # 调用核心功能
                converter = ConversionEngine()
                conversion_type = type_combo.currentText()
                
                if conversion_type == "PDF转Word":
                    converter.pdf_to_word(input_path, output_path)
                elif conversion_type == "PDF转Excel":
                    converter.pdf_to_excel(input_path, output_path)
                elif conversion_type == "PDF转PPT":
                    converter.pdf_to_ppt(input_path, output_path)
                elif conversion_type == "PDF转HTML":
                    converter.pdf_to_html(input_path, output_path)
                elif conversion_type == "PDF转文本":
                    converter.pdf_to_text(input_path, output_path)
                elif conversion_type == "PDF转图像":
                    converter.pdf_to_images(input_path, output_path)
                elif conversion_type == "图像转PDF":
                    converter.images_to_pdf(input_path, output_path)
                elif conversion_type == "Word转PDF":
                    converter.word_to_pdf(input_path, output_path)
                elif conversion_type == "Excel转PDF":
                    converter.excel_to_pdf(input_path, output_path)
                elif conversion_type == "PPT转PDF":
                    converter.ppt_to_pdf(input_path, output_path)
                
                self.status_label.setText('格式转换完成')
                self.log("格式转换完成")
                QMessageBox.information(self, "转换完成", f"文件转换已完成，结果已保存到: {output_path}")
            except Exception as e:
                self.status_label.setText('格式转换失败')
                self.log(f"格式转换失败: {str(e)}")
                QMessageBox.critical(self, "转换失败", f"转换过程中发生错误: {str(e)}")
        
        ok_button.clicked.connect(execute_conversion)
        cancel_button.clicked.connect(dialog.reject)
        
        # 显示对话框
        dialog.exec_()

    def edit_pdf(self):
        """编辑PDF"""
        # 创建编辑选项对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("编辑PDF")
        dialog.setGeometry(200, 200, 400, 300)
        
        layout = QVBoxLayout()
        
        # 编辑类型选择
        type_label = QLabel("选择编辑操作:")
        type_combo = QComboBox()
        type_combo.addItems([
            "删除页面", "插入页面", "替换页面", "重排序页面", "添加水印", "裁剪页面"
        ])
        
        # 输入文件选择
        input_layout = QHBoxLayout()
        input_label = QLabel("PDF文件:")
        input_edit = QLineEdit()
        input_button = QPushButton("浏览")
        
        def select_input():
            path, _ = QFileDialog.getOpenFileName(
                dialog, 
                '选择PDF文件', 
                '', 
                'PDF文件 (*.pdf)'
            )
            if path:
                input_edit.setText(path)
                
        input_button.clicked.connect(select_input)
        
        input_layout.addWidget(input_label)
        input_layout.addWidget(input_edit)
        input_layout.addWidget(input_button)
        
        # 参数设置区域
        params_group = QGroupBox("参数设置")
        params_layout = QVBoxLayout()
        
        # 页面范围输入
        range_label = QLabel("页面范围 (例如: 1-3,5,7-10):")
        range_edit = QLineEdit()
        range_edit.setPlaceholderText("适用于删除、替换等操作")
        
        # 水印文本输入
        watermark_label = QLabel("水印文本:")
        watermark_edit = QLineEdit()
        watermark_edit.setPlaceholderText("适用于添加水印操作")
        
        # 插入位置输入
        position_label = QLabel("插入位置:")
        position_spin = QSpinBox()
        position_spin.setRange(1, 10000)
        position_spin.setValue(1)
        position_spin.setPrefix("第 ")
        position_spin.setSuffix(" 页")
        
        # 新顺序输入
        order_label = QLabel("新页面顺序 (例如: 3,1,2,5,4):")
        order_edit = QLineEdit()
        order_edit.setPlaceholderText("适用于重排序操作")
        
        # 添加控件到参数布局
        params_layout.addWidget(range_label)
        params_layout.addWidget(range_edit)
        params_layout.addWidget(watermark_label)
        params_layout.addWidget(watermark_edit)
        params_layout.addWidget(position_label)
        params_layout.addWidget(position_spin)
        params_layout.addWidget(order_label)
        params_layout.addWidget(order_edit)
        params_group.setLayout(params_layout)
        
        # 输出文件选择
        output_layout = QHBoxLayout()
        output_label = QLabel("输出文件:")
        output_edit = QLineEdit()
        output_button = QPushButton("浏览")
        
        def select_output():
            path, _ = QFileDialog.getSaveFileName(
                dialog, 
                '保存编辑后的PDF', 
                'edited.pdf', 
                'PDF文件 (*.pdf)'
            )
            if path:
                output_edit.setText(path)
                
        output_button.clicked.connect(select_output)
        
        output_layout.addWidget(output_label)
        output_layout.addWidget(output_edit)
        output_layout.addWidget(output_button)
        
        # 确定和取消按钮
        button_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        cancel_button = QPushButton("取消")
        
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        
        # 添加控件到布局
        layout.addWidget(type_label)
        layout.addWidget(type_combo)
        layout.addLayout(input_layout)
        layout.addWidget(params_group)
        layout.addLayout(output_layout)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        
        # 根据选择的操作类型显示相应的参数输入
        def update_param_visibility():
            operation = type_combo.currentText()
            
            # 默认隐藏所有参数输入
            range_label.setVisible(False)
            range_edit.setVisible(False)
            watermark_label.setVisible(False)
            watermark_edit.setVisible(False)
            position_label.setVisible(False)
            position_spin.setVisible(False)
            order_label.setVisible(False)
            order_edit.setVisible(False)
            
            # 根据操作类型显示相应的参数输入
            if operation in ["删除页面", "替换页面"]:
                range_label.setVisible(True)
                range_edit.setVisible(True)
            elif operation == "添加水印":
                watermark_label.setVisible(True)
                watermark_edit.setVisible(True)
            elif operation == "插入页面":
                position_label.setVisible(True)
                position_spin.setVisible(True)
            elif operation == "重排序页面":
                order_label.setVisible(True)
                order_edit.setVisible(True)
        
        # 初始化参数可见性
        update_param_visibility()
        type_combo.currentTextChanged.connect(update_param_visibility)
        
        # 连接按钮事件
        def execute_edit():
            input_path = input_edit.text()
            output_path = output_edit.text()
            
            if not input_path or not output_path:
                self.status_label.setText('请指定输入和输出文件')
                self.log("请指定输入和输出文件")
                return
                
            self.status_label.setText('正在执行PDF编辑...')
            self.log("正在执行PDF编辑...")
            dialog.accept()
            
            try:
                # 导入核心模块
                from core.editor import EditorEngine
                
                # 调用核心功能
                editor = EditorEngine()
                edit_type = type_combo.currentText()
                
                if edit_type == "删除页面":
                    page_range = range_edit.text().strip()
                    pages = self.parse_page_range(page_range)
                    editor.delete_pages(input_path, output_path, pages)
                elif edit_type == "插入页面":
                    # 这里需要额外选择要插入的PDF文件
                    insert_file, _ = QFileDialog.getOpenFileName(
                        self, 
                        '选择要插入的PDF文件', 
                        '', 
                        'PDF文件 (*.pdf)'
                    )
                    if not insert_file:
                        return
                    position = position_spin.value()
                    editor.insert_pages(input_path, insert_file, output_path, position)
                elif edit_type == "替换页面":
                    # 这里需要额外选择替换用的PDF文件
                    replacement_file, _ = QFileDialog.getOpenFileName(
                        self, 
                        '选择替换用的PDF文件', 
                        '', 
                        'PDF文件 (*.pdf)'
                    )
                    if not replacement_file:
                        return
                    page_range = range_edit.text().strip()
                    pages = self.parse_page_range(page_range)
                    editor.replace_pages(input_path, replacement_file, output_path, pages)
                elif edit_type == "重排序页面":
                    order_text = order_edit.text().strip()
                    new_order = [int(x.strip()) for x in order_text.split(',')]
                    editor.reorder_pages(input_path, output_path, new_order)
                elif edit_type == "添加水印":
                    watermark_text = watermark_edit.text().strip()
                    editor.add_watermark(input_path, output_path, watermark_text)
                elif edit_type == "裁剪页面":
                    # 这里需要弹出裁剪参数对话框，或者使用默认参数
                    margins = {'left': 0, 'right': 0, 'top': 0, 'bottom': 0}
                    editor.crop_pages(input_path, output_path, margins)
                
                self.status_label.setText('PDF编辑完成')
                self.log("PDF编辑完成")
                QMessageBox.information(self, "编辑完成", f"PDF编辑已完成，结果已保存到: {output_path}")
            except Exception as e:
                self.status_label.setText('PDF编辑失败')
                self.log(f"PDF编辑失败: {str(e)}")
                QMessageBox.critical(self, "编辑失败", f"编辑过程中发生错误: {str(e)}")
        
        ok_button.clicked.connect(execute_edit)
        cancel_button.clicked.connect(dialog.reject)
        
        # 显示对话框
        dialog.exec_()

    def secure_pdf(self):
        """安全处理PDF"""
        # 创建安全处理选项对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("PDF安全处理")
        dialog.setGeometry(200, 200, 400, 250)
        
        layout = QVBoxLayout()
        
        # 安全操作类型选择
        type_label = QLabel("选择安全操作:")
        type_combo = QComboBox()
        type_combo.addItems([
            "加密PDF", "解密PDF", "添加数字签名", "移除密码"
        ])
        
        # 输入文件选择
        input_layout = QHBoxLayout()
        input_label = QLabel("PDF文件:")
        input_edit = QLineEdit()
        input_button = QPushButton("浏览")
        
        def select_input():
            path, _ = QFileDialog.getOpenFileName(
                dialog, 
                '选择PDF文件', 
                '', 
                'PDF文件 (*.pdf)'
            )
            if path:
                input_edit.setText(path)
                
        input_button.clicked.connect(select_input)
        
        input_layout.addWidget(input_label)
        input_layout.addWidget(input_edit)
        input_layout.addWidget(input_button)
        
        # 密码输入
        password_label = QLabel("密码:")
        password_edit = QLineEdit()
        password_edit.setEchoMode(QLineEdit.Password)
        
        # 输出文件选择
        output_layout = QHBoxLayout()
        output_label = QLabel("输出文件:")
        output_edit = QLineEdit()
        output_button = QPushButton("浏览")
        
        def select_output():
            path, _ = QFileDialog.getSaveFileName(
                dialog, 
                '保存处理后的PDF', 
                'secured.pdf', 
                'PDF文件 (*.pdf)'
            )
            if path:
                output_edit.setText(path)
                
        output_button.clicked.connect(select_output)
        
        output_layout.addWidget(output_label)
        output_layout.addWidget(output_edit)
        output_layout.addWidget(output_button)
        
        # 确定和取消按钮
        button_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        cancel_button = QPushButton("取消")
        
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        
        # 添加控件到布局
        layout.addWidget(type_label)
        layout.addWidget(type_combo)
        layout.addLayout(input_layout)
        layout.addWidget(password_label)
        layout.addWidget(password_edit)
        layout.addLayout(output_layout)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        
        # 连接按钮事件
        def execute_security():
            input_path = input_edit.text()
            output_path = output_edit.text()
            password = password_edit.text()
            
            if not input_path or not output_path:
                self.status_label.setText('请指定输入和输出文件')
                self.log("请指定输入和输出文件")
                return
                
            if not password:
                self.status_label.setText('请输入密码')
                self.log("请指定密码")
                return
                
            self.status_label.setText('正在执行安全处理...')
            self.log("正在执行安全处理...")
            dialog.accept()
            
            try:
                # 导入核心模块
                from core.security import SecurityEngine
                
                # 调用核心功能
                security = SecurityEngine()
                security_type = type_combo.currentText()
                
                if security_type == "加密PDF":
                    security.encrypt_pdf(input_path, output_path, password)
                elif security_type == "解密PDF":
                    security.decrypt_pdf(input_path, output_path, password)
                elif security_type == "移除密码":
                    security.remove_password(input_path, output_path, password)
                elif security_type == "添加数字签名":
                    # 数字签名需要额外的证书文件
                    cert_path, _ = QFileDialog.getOpenFileName(
                        self, 
                        '选择证书文件', 
                        '', 
                        '证书文件 (*.pem *.crt *.p12)'
                    )
                    if not cert_path:
                        return
                    security.add_digital_signature(input_path, output_path, cert_path, None, password)
                
                self.status_label.setText('安全处理完成')
                self.log("安全处理完成")
                QMessageBox.information(self, "处理完成", f"PDF安全处理已完成，结果已保存到: {output_path}")
            except Exception as e:
                self.status_label.setText('安全处理失败')
                self.log(f"安全处理失败: {str(e)}")
                QMessageBox.critical(self, "处理失败", f"处理过程中发生错误: {str(e)}")
        
        ok_button.clicked.connect(execute_security)
        cancel_button.clicked.connect(dialog.reject)
        
        # 显示对话框
        dialog.exec_()

    def add_batch_task(self):
        """添加批量任务"""
        # 创建批量任务对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("添加批量任务")
        dialog.setGeometry(200, 200, 400, 300)
        
        layout = QVBoxLayout()
        
        # 任务名称输入
        name_layout = QHBoxLayout()
        name_label = QLabel("任务名称:")
        name_edit = QLineEdit()
        name_layout.addWidget(name_label)
        name_layout.addWidget(name_edit)
        
        # 任务类型选择
        type_label = QLabel("任务类型:")
        type_combo = QComboBox()
        type_combo.addItems([
            "优化压缩", 
            "PDF转文本", 
            "旋转页面",
            "其他任务"
        ])
        
        # 输入文件选择
        file_layout = QHBoxLayout()
        file_label = QLabel("输入文件:")
        file_edit = QLineEdit()
        file_button = QPushButton("浏览")
        
        def select_files():
            paths, _ = QFileDialog.getOpenFileNames(
                dialog, 
                '选择输入文件', 
                '', 
                'PDF文件 (*.pdf)'
            )
            if paths:
                file_edit.setText(";".join(paths))
                
        file_button.clicked.connect(select_files)
        
        file_layout.addWidget(file_label)
        file_layout.addWidget(file_edit)
        file_layout.addWidget(file_button)
        
        # 输出目录选择
        output_layout = QHBoxLayout()
        output_label = QLabel("输出目录:")
        output_edit = QLineEdit()
        output_button = QPushButton("浏览")
        
        def select_output():
            path = QFileDialog.getExistingDirectory(
                dialog, 
                '选择输出目录', 
                ''
            )
            if path:
                output_edit.setText(path)
                
        output_button.clicked.connect(select_output)
        
        output_layout.addWidget(output_label)
        output_layout.addWidget(output_edit)
        output_layout.addWidget(output_button)
        
        # 参数输入
        params_label = QLabel("参数:")
        params_edit = QTextEdit()
        
        # 确定和取消按钮
        button_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        cancel_button = QPushButton("取消")
        
        def add_task():
            task_name = name_edit.text().strip()
            task_type = type_combo.currentText()
            input_files = file_edit.text().strip()
            output_dir = output_edit.text().strip()
            
            if not task_name or not task_type or not input_files or not output_dir:
                self.status_label.setText('请填写所有字段')
                self.log("请填写所有字段")
                return
                
            self.status_label.setText('任务已添加')
            self.log(f"任务已添加: {task_name}")
            
            # 添加任务到表格
            row = self.task_table.rowCount()
            self.task_table.insertRow(row)
            self.task_table.setItem(row, 0, QTableWidgetItem(task_name))
            self.task_table.setItem(row, 1, QTableWidgetItem("待处理"))
            self.task_table.setItem(row, 2, QTableWidgetItem(task_type))
            
            # 添加进度条
            progress = QProgressBar()
            progress.setValue(0)
            self.task_table.setCellWidget(row, 4, progress)
            
            # 操作按钮
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            start_btn = QPushButton("开始")
            remove_btn = QPushButton("移除")
            
            def start_task():
                self.execute_batch_task(row, task_type, input_files, output_dir, params_edit.toPlainText(), progress)
                
            def remove_task():
                self.task_table.removeRow(row)
                
            start_btn.clicked.connect(start_task)
            remove_btn.clicked.connect(remove_task)
            btn_layout.addWidget(start_btn)
            btn_layout.addWidget(remove_btn)
            self.task_table.setCellWidget(row, 3, btn_widget)
            
            dialog.close()
            
        ok_button.clicked.connect(add_task)
        cancel_button.clicked.connect(dialog.close)
        
        # 添加控件到布局
        layout.addLayout(name_layout)
        layout.addWidget(type_label)
        layout.addWidget(type_combo)
        layout.addLayout(file_layout)
        layout.addLayout(output_layout)
        layout.addWidget(params_label)
        layout.addWidget(params_edit)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        dialog.exec_()

    def remove_batch_task(self):
        """移除选中的批量任务"""
        selected_rows = set()
        for item in self.task_table.selectedItems():
            selected_rows.add(item.row())
            
        # 从后往前删除，避免索引问题
        for row in sorted(selected_rows, reverse=True):
            self.task_table.removeRow(row)
            
        if not selected_rows:
            self.status_label.setText("请选择要移除的任务")

    def start_batch_process(self):
        """开始批量处理"""
        self.status_label.setText("开始批量处理...")
        self.log("开始批量处理")
        
        # 检查是否有任务
        if self.task_table.rowCount() == 0:
            self.status_label.setText("没有可处理的任务")
            return
            
        # 开始处理所有任务
        for row in range(self.task_table.rowCount()):
            status_item = self.task_table.item(row, 1)
            if status_item and status_item.text() == "待处理":
                # 获取任务信息
                task_name = self.task_table.item(row, 0).text() if self.task_table.item(row, 0) else "未知任务"
                self.task_table.item(row, 1).setText("处理中")
                self.status_label.setText(f"正在处理: {task_name}")
                self.log(f"正在处理批量任务: {task_name}")
                # 实际处理逻辑需要根据具体任务类型实现
                
        self.status_label.setText("批量处理完成")
        self.log("批量处理完成")

    def execute_batch_task(self, row, task_type, input_files, output_dir, params, progress):
        """执行单个批量任务"""
        try:
            # 更新状态
            self.task_table.item(row, 1).setText("处理中")
            progress.setValue(10)
            
            # 解析输入文件
            files = [f.strip() for f in input_files.split(";") if f.strip()]
            
            # 根据任务类型执行相应操作
            # 这里只是一个示例，实际需要根据每种操作类型实现具体逻辑
            progress.setValue(50)
            
            # 模拟处理过程
            import time
            time.sleep(1)
            
            progress.setValue(100)
            self.task_table.item(row, 1).setText("已完成")
            self.status_label.setText(f"任务完成: {self.task_table.item(row, 0).text()}")
            
        except Exception as e:
            self.task_table.item(row, 1).setText("失败")
            self.status_label.setText(f"任务失败: {str(e)}")
            self.log(f"批量任务执行失败: {str(e)}")

    def refresh_history(self):
        """刷新历史记录"""
        self.status_label.setText("历史记录已刷新")
        self.log("刷新历史记录...")

    def clear_history(self):
        """清空历史记录"""
        reply = QMessageBox.question(self, '确认', '确定要清空所有历史记录吗？',
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.history_table.setRowCount(0)
            self.status_label.setText("历史记录已清空")
            self.log("清空历史记录...")

    def reprocess_selected(self):
        """重新处理选中项"""
        selected_rows = set()
        for item in self.history_table.selectedItems():
            selected_rows.add(item.row())
            
        if not selected_rows:
            self.status_label.setText("请先选择要重新处理的记录")
            return
            
        self.status_label.setText(f"重新处理 {len(selected_rows)} 项记录")
        self.log("重新处理选中项...")

    def log(self, message):
        """记录日志"""
        # 在状态栏显示简短消息
        if len(message) > 50:
            status_msg = message[:47] + "..."
        else:
            status_msg = message
        self.status_label.setText(status_msg)
        QApplication.processEvents()  # 确保界面及时更新

    # 添加所有缺失的工具方法
    def rotate_pages(self):
        """旋转页面"""
        # 选择要旋转的PDF文件
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            '选择要旋转的PDF文件', 
            '', 
            'PDF文件 (*.pdf)'
        )
        
        if not file_path:
            return
            
        # 输入旋转角度
        angle, ok = QInputDialog.getInt(self, '旋转角度', '请输入旋转角度 (90, 180, 270):', 90, 90, 270, 90)
        if not ok:
            return
            
        # 选择输出文件路径
        output_path, _ = QFileDialog.getSaveFileName(
            self, 
            '保存旋转后的PDF', 
            'rotated.pdf', 
            'PDF文件 (*.pdf)'
        )
        
        if not output_path:
            return
            
        self.status_label.setText('正在旋转页面...')
        self.log("正在旋转页面...")
        
        try:
            # 导入核心模块
            from core.editor import PDFEditor
            
            # 调用核心功能
            editor = PDFEditor()
            editor.rotate_pages(file_path, output_path, angle)
            
            self.status_label.setText('页面旋转完成')
            self.log("页面旋转完成")
            QMessageBox.information(self, "成功", "页面旋转完成！")
        except Exception as e:
            self.status_label.setText('页面旋转失败')
            self.log(f"页面旋转失败: {str(e)}")
            QMessageBox.critical(self, "错误", f"页面旋转失败: {str(e)}")

    def pdf_to_text(self):
        """PDF转文本"""
        # 选择要转换的PDF文件
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            '选择要转换为文本的PDF文件', 
            '', 
            'PDF文件 (*.pdf)'
        )
        
        if not file_path:
            return
            
        # 选择输出文件路径
        output_path, _ = QFileDialog.getSaveFileName(
            self, 
            '保存转换后的文本文件', 
            'output.txt', 
            '文本文件 (*.txt)'
        )
        
        if not output_path:
            return
            
        self.status_label.setText('正在转换PDF为文本...')
        self.log("正在转换PDF为文本...")
        
        try:
            # 导入核心模块
            from core.conversion import ConversionEngine
            
            # 调用核心功能
            converter = ConversionEngine()
            converter.pdf_to_text(file_path, output_path)
            
            self.status_label.setText('PDF转文本完成')
            self.log("PDF转文本完成")
            QMessageBox.information(self, "成功", "PDF转文本完成！")
        except Exception as e:
            self.status_label.setText('PDF转文本失败')
            self.log(f"PDF转文本失败: {str(e)}")
            QMessageBox.critical(self, "错误", f"PDF转文本失败: {str(e)}")

    def pdf_to_images(self):
        """PDF转图像"""
        # 选择要转换的PDF文件
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            '选择要转换为图像的PDF文件', 
            '', 
            'PDF文件 (*.pdf)'
        )
        
        if not file_path:
            return
            
        # 选择输出目录
        output_dir = QFileDialog.getExistingDirectory(
            self, 
            '选择图像保存目录'
        )
        
        if not output_dir:
            return
            
        self.status_label.setText('正在转换PDF为图像...')
        self.log("正在转换PDF为图像...")
        
        try:
            # 导入核心模块
            from core.conversion import ConversionEngine
            
            # 调用核心功能
            converter = ConversionEngine()
            converter.pdf_to_images(file_path, output_dir)
            
            self.status_label.setText('PDF转图像完成')
            self.log("PDF转图像完成")
            QMessageBox.information(self, "成功", "PDF转图像完成！")
        except Exception as e:
            self.status_label.setText('PDF转图像失败')
            self.log(f"PDF转图像失败: {str(e)}")
            QMessageBox.critical(self, "错误", f"PDF转图像失败: {str(e)}")

    def images_to_pdf(self):
        """图像转PDF"""
        # 选择要转换的图像文件
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, 
            '选择要转换为PDF的图像文件', 
            '', 
            '图像文件 (*.png *.jpg *.jpeg *.bmp *.tiff)'
        )
        
        if not file_paths:
            return
            
        # 选择输出文件路径
        output_path, _ = QFileDialog.getSaveFileName(
            self, 
            '保存转换后的PDF文件', 
            'output.pdf', 
            'PDF文件 (*.pdf)'
        )
        
        if not output_path:
            return
            
        self.status_label.setText('正在转换图像为PDF...')
        self.log("正在转换图像为PDF...")
        
        try:
            # 导入核心模块
            from core.conversion import ConversionEngine
            
            # 调用核心功能
            converter = ConversionEngine()
            converter.images_to_pdf(file_paths, output_path)
            
            self.status_label.setText('图像转PDF完成')
            self.log("图像转PDF完成")
            QMessageBox.information(self, "成功", "图像转PDF完成！")
        except Exception as e:
            self.status_label.setText('图像转PDF失败')
            self.log(f"图像转PDF失败: {str(e)}")
            QMessageBox.critical(self, "错误", f"图像转PDF失败: {str(e)}")

    def pdf_to_word(self):
        """PDF转Word"""
        # 选择要转换的PDF文件
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            '选择要转换为Word的PDF文件', 
            '', 
            'PDF文件 (*.pdf)'
        )
        
        if not file_path:
            return
            
        # 选择输出文件路径
        output_path, _ = QFileDialog.getSaveFileName(
            self, 
            '保存转换后的Word文件', 
            'output.docx', 
            'Word文件 (*.docx)'
        )
        
        if not output_path:
            return
            
        self.status_label.setText('正在转换PDF为Word...')
        self.log("正在转换PDF为Word...")
        
        try:
            # 导入核心模块
            from core.conversion import ConversionEngine
            
            # 调用核心功能
            converter = ConversionEngine()
            converter.pdf_to_word(file_path, output_path)
            
            self.status_label.setText('PDF转Word完成')
            self.log("PDF转Word完成")
            QMessageBox.information(self, "成功", "PDF转Word完成！")
        except Exception as e:
            self.status_label.setText('PDF转Word失败')
            self.log(f"PDF转Word失败: {str(e)}")
            QMessageBox.critical(self, "错误", f"PDF转Word失败: {str(e)}")

    def word_to_pdf(self):
        """Word转PDF"""
        # 选择要转换的Word文件
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            '选择要转换为PDF的Word文件', 
            '', 
            'Word文件 (*.docx)'
        )
        
        if not file_path:
            return
            
        # 选择输出文件路径
        output_path, _ = QFileDialog.getSaveFileName(
            self, 
            '保存转换后的PDF文件', 
            'output.pdf', 
            'PDF文件 (*.pdf)'
        )
        
        if not output_path:
            return
            
        self.status_label.setText('正在转换Word为PDF...')
        self.log("正在转换Word为PDF...")
        
        try:
            # 导入核心模块
            from core.conversion import ConversionEngine
            
            # 调用核心功能
            converter = ConversionEngine()
            converter.word_to_pdf(file_path, output_path)
            
            self.status_label.setText('Word转PDF完成')
            self.log("Word转PDF完成")
            QMessageBox.information(self, "成功", "Word转PDF完成！")
        except Exception as e:
            self.status_label.setText('Word转PDF失败')
            self.log(f"Word转PDF失败: {str(e)}")
            QMessageBox.critical(self, "错误", f"Word转PDF失败: {str(e)}")

    def pdf_to_excel(self):
        """PDF转Excel"""
        # 选择要转换的PDF文件
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            '选择要转换为Excel的PDF文件', 
            '', 
            'PDF文件 (*.pdf)'
        )
        
        if not file_path:
            return
            
        # 选择输出文件路径
        output_path, _ = QFileDialog.getSaveFileName(
            self, 
            '保存转换后的Excel文件', 
            'output.xlsx', 
            'Excel文件 (*.xlsx)'
        )
        
        if not output_path:
            return
            
        self.status_label.setText('正在转换PDF为Excel...')
        self.log("正在转换PDF为Excel...")
        
        try:
            # 导入核心模块
            from core.conversion import ConversionEngine
            
            # 调用核心功能
            converter = ConversionEngine()
            converter.pdf_to_excel(file_path, output_path)
            
            self.status_label.setText('PDF转Excel完成')
            self.log("PDF转Excel完成")
            QMessageBox.information(self, "成功", "PDF转Excel完成！")
        except Exception as e:
            self.status_label.setText('PDF转Excel失败')
            self.log(f"PDF转Excel失败: {str(e)}")
            QMessageBox.critical(self, "错误", f"PDF转Excel失败: {str(e)}")

    def excel_to_pdf(self):
        """Excel转PDF"""
        # 选择要转换的Excel文件
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            '选择要转换为PDF的Excel文件', 
            '', 
            'Excel文件 (*.xlsx)'
        )
        
        if not file_path:
            return
            
        # 选择输出文件路径
        output_path, _ = QFileDialog.getSaveFileName(
            self, 
            '保存转换后的PDF文件', 
            'output.pdf', 
            'PDF文件 (*.pdf)'
        )
        
        if not output_path:
            return
            
        self.status_label.setText('正在转换Excel为PDF...')
        self.log("正在转换Excel为PDF...")
        
        try:
            # 导入核心模块
            from core.conversion import ConversionEngine
            
            # 调用核心功能
            converter = ConversionEngine()
            converter.excel_to_pdf(file_path, output_path)
            
            self.status_label.setText('Excel转PDF完成')
            self.log("Excel转PDF完成")
            QMessageBox.information(self, "成功", "Excel转PDF完成！")
        except Exception as e:
            self.status_label.setText('Excel转PDF失败')
            self.log(f"Excel转PDF失败: {str(e)}")
            QMessageBox.critical(self, "错误", f"Excel转PDF失败: {str(e)}")

        # 选择输出文件路径
        output_path, _ = QFileDialog.getSaveFileName(
            self, 
            '保存HTML文件', 
            'output.html', 
            'HTML文件 (*.html)'
        )
        
        if not output_path:
            return
            
        self.status_label.setText('正在转换PDF为HTML...')
        self.log("正在转换PDF为HTML...")
        
        try:
            # 导入核心模块
            from core.conversion import ConversionEngine
            
            # 调用核心功能
            converter = ConversionEngine()
            converter.pdf_to_html(file_path, output_path)
            
            self.status_label.setText('PDF转HTML完成')
            self.log("PDF转HTML完成")
            QMessageBox.information(self, "成功", "PDF转HTML完成！")
        except Exception as e:
            self.status_label.setText('PDF转HTML失败')
            self.log(f"PDF转HTML失败: {str(e)}")
            QMessageBox.critical(self, "错误", f"PDF转HTML失败: {str(e)}")

    def pdf_to_ppt(self):
        """PDF转PPT"""
        # 选择要转换的PDF文件
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            '选择要转换为PPT的PDF文件', 
            '', 
            'PDF文件 (*.pdf)'
        )
        
        if not file_path:
            return
            
        # 选择输出文件路径
        output_path, _ = QFileDialog.getSaveFileName(
            self, 
            '保存转换后的PPT文件', 
            'output.pptx', 
            'PPT文件 (*.pptx)'
        )
        
        if not output_path:
            return
            
        self.status_label.setText('正在转换PDF为PPT...')
        self.log("正在转换PDF为PPT...")
        
        try:
            # 导入核心模块
            from core.conversion import ConversionEngine
            
            # 调用核心功能
            converter = ConversionEngine()
            converter.pdf_to_ppt(file_path, output_path)
            
            self.status_label.setText('PDF转PPT完成')
            self.log("PDF转PPT完成")
            QMessageBox.information(self, "成功", "PDF转PPT完成！")
        except Exception as e:
            self.status_label.setText('PDF转PPT失败')
            self.log(f"PDF转PPT失败: {str(e)}")
            QMessageBox.critical(self, "错误", f"PDF转PPT失败: {str(e)}")

    def ppt_to_pdf(self):
        """PPT转PDF"""
        # 选择要转换的PPT文件
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            '选择要转换为PDF的PPT文件', 
            '', 
            'PPT文件 (*.pptx)'
        )
        
        if not file_path:
            return
            
        # 选择输出文件路径
        output_path, _ = QFileDialog.getSaveFileName(
            self, 
            '保存转换后的PDF文件', 
            'output.pdf', 
            'PDF文件 (*.pdf)'
        )
        
        if not output_path:
            return
            
        self.status_label.setText('正在转换PPT为PDF...')
        self.log("正在转换PPT为PDF...")
        
        try:
            # 导入核心模块
            from core.conversion import ConversionEngine
            
            # 调用核心功能
            converter = ConversionEngine()
            converter.ppt_to_pdf(file_path, output_path)
            
            self.status_label.setText('PPT转PDF完成')
            self.log("PPT转PDF完成")
            QMessageBox.information(self, "成功", "PPT转PDF完成！")
        except Exception as e:
            self.status_label.setText('PPT转PDF失败')
            self.log(f"PPT转PDF失败: {str(e)}")
            QMessageBox.critical(self, "错误", f"PPT转PDF失败: {str(e)}")

    def pdf_to_csv(self):
        """PDF转CSV"""
        # 选择要转换的PDF文件
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            '选择要转换为CSV的PDF文件', 
            '', 
            'PDF文件 (*.pdf)'
        )
        
        if not file_path:
            return
            
        # 选择输出文件路径
        output_path, _ = QFileDialog.getSaveFileName(
            self, 
            '保存转换后的CSV文件', 
            'output.csv', 
            'CSV文件 (*.csv)'
        )
        
        if not output_path:
            return
            
        self.status_label.setText('正在转换PDF为CSV...')
        self.log("正在转换PDF为CSV...")
        
        try:
            # 导入核心模块
            from core.conversion import ConversionEngine
            
            # 调用核心功能
            converter = ConversionEngine()
            converter.pdf_to_csv(file_path, output_path)
            
            self.status_label.setText('PDF转CSV完成')
            self.log("PDF转CSV完成")
            QMessageBox.information(self, "成功", "PDF转CSV完成！")
        except Exception as e:
            self.status_label.setText('PDF转CSV失败')
            self.log(f"PDF转CSV失败: {str(e)}")
            QMessageBox.critical(self, "错误", f"PDF转CSV失败: {str(e)}")

    def ocr_pdf(self):
        """OCR识别"""
        # 检查OCR依赖
        try:
            import pytesseract
            from PIL import Image
        except ImportError as e:
            QMessageBox.critical(self, "依赖缺失", f"OCR功能需要安装额外依赖: {str(e)}\n请运行: pip install pytesseract pillow")
            return
            
        # 检查Tesseract可执行文件
        try:
            pytesseract.get_tesseract_version()
        except pytesseract.TesseractNotFoundError:
            QMessageBox.warning(self, "OCR引擎缺失", 
                              "未找到Tesseract-OCR引擎，请安装Tesseract-OCR并确保其在系统PATH中。\n"
                              "Windows用户可以从 https://github.com/UB-Mannheim/tesseract/wiki 下载安装。\n"
                              "安装后可能需要重启应用程序。")
            return
            
        # 选择要进行OCR的PDF文件
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            '选择要进行OCR识别的PDF文件', 
            '', 
            'PDF文件 (*.pdf)'
        )
        
        if not file_path:
            return
            
        # 选择输出文件路径
        output_path, _ = QFileDialog.getSaveFileName(
            self, 
            '保存OCR结果', 
            'ocr_result.txt', 
            '文本文件 (*.txt);;PDF文件 (*.pdf)'
        )
        
        if not output_path:
            return
            
        self.status_label.setText('正在进行OCR识别...')
        self.log("正在进行OCR识别...")
        
        try:
            # 导入核心模块
            from core.ocr import OCREngine
            
            # 调用核心功能
            ocr_engine = OCREngine()
            ocr_engine.process_pdf(file_path, output_path)
            
            self.status_label.setText('OCR识别完成')
            self.log("OCR识别完成")
            QMessageBox.information(self, "OCR完成", f"OCR识别已完成，结果已保存到: {output_path}")
        except Exception as e:
            self.status_label.setText('OCR识别失败')
            self.log(f"OCR识别失败: {str(e)}")
            QMessageBox.critical(self, "OCR失败", f"OCR识别过程中发生错误: {str(e)}")
        
    def delete_pages(self):
        """删除页面"""
        # 选择要删除页面的PDF文件
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            '选择要删除页面的PDF文件', 
            '', 
            'PDF文件 (*.pdf)'
        )
        
        if not file_path:
            return
            
        # 输入页面范围
        page_range, ok = QInputDialog.getText(self, '页面范围', '请输入要删除的页面范围 (例如: 1-3,5,7-9):')
        if not ok or not page_range:
            return
            
        # 选择输出文件路径
        output_path, _ = QFileDialog.getSaveFileName(
            self, 
            '保存删除页面后的PDF', 
            'deleted_pages.pdf', 
            'PDF文件 (*.pdf)'
        )
        
        if not output_path:
            return
            
        self.status_label.setText('正在删除页面...')
        self.log("正在删除页面...")
        
        try:
            # 解析页面范围
            pages = self.parse_page_range(page_range)
            
            # 导入核心模块
            from core.pdf_engine import PDFEngine
            
            # 调用核心功能
            engine = PDFEngine()
            engine.delete_pages(file_path, output_path, pages)
            
            self.status_label.setText('页面删除成功')
            self.log("页面删除成功")
        except Exception as e:
            self.status_label.setText('页面删除失败')
            self.log(f"页面删除失败: {str(e)}")
        
    def insert_pages(self):
        """插入页面"""
        # 选择目标PDF文件
        target_file, _ = QFileDialog.getOpenFileName(
            self, 
            '选择目标PDF文件', 
            '', 
            'PDF文件 (*.pdf)'
        )
        
        if not target_file:
            return
            
        # 选择要插入的PDF文件
        insert_file, _ = QFileDialog.getOpenFileName(
            self, 
            '选择要插入的PDF文件', 
            '', 
            'PDF文件 (*.pdf)'
        )
        
        if not insert_file:
            return
            
        # 输入插入位置
        position, ok = QInputDialog.getInt(self, '插入位置', '请输入插入位置(页码):', 1, 1, 10000)
        if not ok:
            return
            
        # 选择输出文件路径
        output_path, _ = QFileDialog.getSaveFileName(
            self, 
            '保存插入页面后的PDF', 
            'inserted_pages.pdf', 
            'PDF文件 (*.pdf)'
        )
        
        if not output_path:
            return
            
        self.status_label.setText('正在插入页面...')
        self.log("正在插入页面...")
        
        try:
            # 导入核心模块
            from core.editor import PDFEditor
            
            # 调用核心功能
            editor = PDFEditor()
            editor.insert_pages(target_file, insert_file, output_path, position)
            
            self.status_label.setText('页面插入完成')
            self.log("页面插入完成")
        except Exception as e:
            self.status_label.setText('页面插入失败')
            self.log(f"页面插入失败: {str(e)}")

    def replace_pages(self):
        """替换页面"""
        # 选择目标PDF文件
        target_file, _ = QFileDialog.getOpenFileName(
            self, 
            '选择目标PDF文件', 
            '', 
            'PDF文件 (*.pdf)'
        )
        
        if not target_file:
            return
            
        # 选择替换用的PDF文件
        replacement_file, _ = QFileDialog.getOpenFileName(
            self, 
            '选择替换用的PDF文件', 
            '', 
            'PDF文件 (*.pdf)'
        )
        
        if not replacement_file:
            return
            
        # 输入页面范围
        page_range, ok = QInputDialog.getText(self, '页面范围', '请输入要替换的页面范围 (例如: 1-3,5,7-9):')
        if not ok or not page_range:
            return
            
        # 选择输出文件路径
        output_path, _ = QFileDialog.getSaveFileName(
            self, 
            '保存替换页面后的PDF', 
            'replaced_pages.pdf', 
            'PDF文件 (*.pdf)'
        )
        
        if not output_path:
            return
            
        self.status_label.setText('正在替换页面...')
        self.log("正在替换页面...")
        
        try:
            # 解析页面范围
            pages = self.parse_page_range(page_range)
            
            # 导入核心模块
            from core.editor import PDFEditor
            
            # 调用核心功能
            editor = PDFEditor()
            editor.replace_pages(target_file, replacement_file, output_path, pages)
            
            self.status_label.setText('页面替换完成')
            self.log("页面替换完成")
        except Exception as e:
            self.status_label.setText('页面替换失败')
            self.log(f"页面替换失败: {str(e)}")

    def reorder_pages(self):
        """重排序页面"""
        # 选择要重排序的PDF文件
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            '选择要重排序的PDF文件', 
            '', 
            'PDF文件 (*.pdf)'
        )
        
        if not file_path:
            return
            
        # 输入新的页面顺序
        order, ok = QInputDialog.getText(self, '页面顺序', '请输入新的页面顺序 (例如: 3,1,2,5,4):')
        if not ok or not order:
            return
            
        # 选择输出文件路径
        output_path, _ = QFileDialog.getSaveFileName(
            self, 
            '保存重排序后的PDF', 
            'reordered_pages.pdf', 
            'PDF文件 (*.pdf)'
        )
        
        if not output_path:
            return
            
        self.status_label.setText('正在重排序页面...')
        self.log("正在重排序页面...")
        
        try:
            # 解析页面顺序
            new_order = [int(x.strip()) for x in order.split(',')]
            
            # 导入核心模块
            from core.editor import PDFEditor
            
            # 调用核心功能
            editor = PDFEditor()
            editor.reorder_pages(file_path, output_path, new_order)
            
            self.status_label.setText('页面重排序完成')
            self.log("页面重排序完成")
        except Exception as e:
            self.status_label.setText('页面重排序失败')
            self.log(f"页面重排序失败: {str(e)}")

    def crop_pages(self):
        """裁剪页面"""
        # 选择要裁剪的PDF文件
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            '选择要裁剪的PDF文件', 
            '', 
            'PDF文件 (*.pdf)'
        )
        
        if not file_path:
            return
            
        # 输入裁剪参数
        crop_rect, ok = QInputDialog.getText(
            self, 
            '裁剪区域', 
            '请输入裁剪区域 (左边距,下边距,右边距,上边距) (英寸):',
            text='0.5,0.5,0.5,0.5'
        )
        if not ok or not crop_rect:
            return
            
        # 选择输出文件路径
        output_path, _ = QFileDialog.getSaveFileName(
            self, 
            '保存裁剪后的PDF', 
            'cropped_pages.pdf', 
            'PDF文件 (*.pdf)'
        )
        
        if not output_path:
            return
            
        self.status_label.setText('正在裁剪页面...')
        self.log("正在裁剪页面...")
        
        try:
            # 解析裁剪参数
            margins = [float(x.strip()) for x in crop_rect.split(',')]
            if len(margins) != 4:
                raise ValueError("裁剪区域参数必须包含4个数值")
            
            # 导入核心模块
            from core.editor import PDFEditor
            
            # 调用核心功能
            editor = PDFEditor()
            editor.crop_pages(file_path, output_path, margins)
            
            self.status_label.setText('页面裁剪完成')
            self.log("页面裁剪完成")
        except Exception as e:
            self.status_label.setText('页面裁剪失败')
            self.log(f"页面裁剪失败: {str(e)}")

    def encrypt_pdf(self):
        """加密PDF"""
        # 选择要加密的PDF文件
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            '选择要加密的PDF文件', 
            '', 
            'PDF文件 (*.pdf)'
        )
        
        if not file_path:
            return
            
        # 输入密码
        password, ok = QInputDialog.getText(self, '设置密码', '请输入加密密码:', echo=QLineEdit.Password)
        if not ok or not password:
            return
            
        # 选择输出文件路径
        output_path, _ = QFileDialog.getSaveFileName(
            self, 
            '保存加密后的PDF', 
            'encrypted.pdf', 
            'PDF文件 (*.pdf)'
        )
        
        if not output_path:
            return
            
        self.status_label.setText('正在加密PDF...')
        self.log("正在加密PDF...")
        
        try:
            # 导入核心模块
            from core.security import SecurityEngine
            
            # 调用核心功能
            security = SecurityEngine()
            security.encrypt_pdf(file_path, output_path, password)
            
            self.status_label.setText('PDF加密完成')
            self.log("PDF加密完成")
        except Exception as e:
            self.status_label.setText('PDF加密失败')
            self.log(f"PDF加密失败: {str(e)}")

    def decrypt_pdf(self):
        """解密PDF"""
        # 选择要解密的PDF文件
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            '选择要解密的PDF文件', 
            '', 
            'PDF文件 (*.pdf)'
        )
        
        if not file_path:
            return
            
        # 输入密码
        password, ok = QInputDialog.getText(self, '输入密码', '请输入解密密码:', echo=QLineEdit.Password)
        if not ok or not password:
            return
            
        # 选择输出文件路径
        output_path, _ = QFileDialog.getSaveFileName(
            self, 
            '保存解密后的PDF', 
            'decrypted.pdf', 
            'PDF文件 (*.pdf)'
        )
        
        if not output_path:
            return
            
        self.status_label.setText('正在解密PDF...')
        self.log("正在解密PDF...")
        
        try:
            # 导入核心模块
            from core.security import SecurityEngine
            
            # 调用核心功能
            security = SecurityEngine()
            security.decrypt_pdf(file_path, output_path, password)
            
            self.status_label.setText('PDF解密完成')
            self.log("PDF解密完成")
        except Exception as e:
            self.status_label.setText('PDF解密失败')
            self.log(f"PDF解密失败: {str(e)}")

    def digital_signature(self):
        """数字签名"""
        self.status_label.setText('执行数字签名功能')
        self.log("执行数字签名功能")
        QMessageBox.information(self, "功能提示", "数字签名功能将在后续版本中实现")

    def remove_password(self):
        """移除密码"""
        self.status_label.setText('执行移除密码功能')
        self.log("执行移除密码功能")
        QMessageBox.information(self, "功能提示", "移除密码功能将在后续版本中实现")

    def compare_documents(self):
        """比较文档"""
        self.status_label.setText('执行比较文档功能')
        self.log("执行比较文档功能")
        QMessageBox.information(self, "功能提示", "比较文档功能将在后续版本中实现")

    def create_about_page(self):
        """创建关于页面，包含软件介绍、功能说明和法律声明"""

    def optimize_compression(self):
        """优化压缩"""
        self.status_label.setText('执行优化压缩功能')
        self.log("执行优化压缩功能")
        QMessageBox.information(self, "功能提示", "优化压缩功能将在后续版本中实现")

    def create_about_page(self):
        """创建关于页面，包含软件介绍、功能说明和法律声明"""
        about_widget = QWidget()
        about_layout = QVBoxLayout(about_widget)
        about_layout.setSpacing(15)
        about_layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title_label = QLabel("PDF处理器")
        title_label.setObjectName("pageTitle")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin: 10px;")
        about_layout.addWidget(title_label)
        
        # 版本信息
        version_label = QLabel("版本: 1.0.0")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("font-size: 14px; color: #666; margin-bottom: 20px;")
        about_layout.addWidget(version_label)
        
        # 创建标签页
        tab_widget = QTabWidget()
        
        # 软件介绍标签
        intro_widget = QWidget()
        intro_layout = QVBoxLayout(intro_widget)
        intro_text = QTextEdit()
        intro_text.setReadOnly(True)
        intro_text.setHtml("""
        <h2>软件介绍</h2>
        <p>PDF处理器是一个功能强大的PDF文档处理工具，专为个人和企业用户设计。该软件提供了全面的PDF操作功能，包括基础的拆分、合并，到高级的OCR识别、数字签名等。</p>
        
        <h3>主要功能</h3>
        <ul>
        <li><b>基础操作</b>: 拆分、合并、旋转、压缩PDF文档</li>
        <li><b>格式转换</b>: PDF与Word、Excel、PPT、图像等多种格式互转</li>
        <li><b>编辑功能</b>: 删除、插入、替换页面，添加水印等</li>
        <li><b>安全保护</b>: 加密解密、数字签名、权限管理</li>
        <li><b>OCR识别</b>: 将扫描版PDF转换为可编辑文本</li>
        <li><b>批量处理</b>: 支持批量操作，提高工作效率</li>
        <li><b>文档比较</b>: 比较两个PDF文档的差异</li>
        </ul>
        
        <h3>软件特点</h3>
        <ul>
        <li><b>本地处理</b>: 所有操作均在本地完成，保障文档安全</li>
        <li><b>企业兼容</b>: 支持企业内网环境，无需联网即可使用</li>
        <li><b>界面友好</b>: 现代化UI设计，操作简单直观</li>
        <li><b>高效稳定</b>: 优化的处理引擎，支持大文件处理</li>
        <li><b>扩展性强</b>: 支持插件扩展，满足个性化需求</li>
        </ul>
        """)
        intro_layout.addWidget(intro_text)
        tab_widget.addTab(intro_widget, "软件介绍")
        
        # 法律声明标签
        legal_widget = QWidget()
        legal_layout = QVBoxLayout(legal_widget)
        legal_text = QTextEdit()
        legal_text.setReadOnly(True)
        legal_text.setHtml("""
        <h2>法律声明与许可协议</h2>
        
        <h3>版权声明</h3>
        <p>PDF处理器是由PDF处理器开发团队开发的开源软件，遵循MIT许可证协议。本软件完全免费用于商业和个人用途。</p>
        
        <h3>开源许可证</h3>
        <p>本软件采用MIT许可证，这意味着：</p>
        <ul>
        <li>您可以自由使用、复制、修改、分发本软件</li>
        <li>您可以将本软件用于商业用途</li>
        <li>您可以修改源代码以满足您的需求</li>
        <li>您可以将修改后的软件再次开源或闭源发布</li>
        </ul>
        <p>唯一的限制是，软件的原始版权通知和许可证文本必须保留在所有副本或实质性部分中。</p>
        
        <h3>免责声明</h3>
        <p>本软件按"现状"提供，不提供任何形式的担保，包括但不限于适销性、特定用途适用性和非侵权的担保。在任何情况下，作者或版权持有人均不对因使用本软件而产生的任何索赔、损害或其他责任负责。</p>
        
        <h3>第三方库声明</h3>
        <p>本软件使用了以下开源库：</p>
        <ul>
        <li><b>PyPDF2</b>: 用于PDF读写操作</li>
        <li><b>PyQt5</b>: 用于图形界面</li>
        <li><b>reportlab</b>: 用于PDF生成</li>
        <li><b>Pillow</b>: 用于图像处理</li>
        <li><b>pytesseract</b>: 用于OCR识别</li>
        <li><b>以及其他多个优秀的开源库</b></li>
        </ul>
        <p>这些库都有各自的许可证，使用本软件即表示您同意遵守这些库的许可证条款。</p>
        
        <h3>商业使用声明</h3>
        <p>根据MIT许可证条款，本软件可以自由用于商业用途，包括但不限于：</p>
        <ul>
        <li>企业内部使用</li>
        <li>作为商业产品的一部分</li>
        <li>提供商业服务</li>
        <li>修改后重新发布</li>
        </ul>
        <p>我们鼓励商业使用，并欢迎企业根据自身需求对软件进行定制和改进。</p>
        """)
        legal_layout.addWidget(legal_text)
        tab_widget.addTab(legal_widget, "法律声明")
        
        # 开源信息标签
        open_source_widget = QWidget()
        open_source_layout = QVBoxLayout(open_source_widget)
        open_source_text = QTextEdit()
        open_source_text.setReadOnly(True)
        open_source_text.setHtml("""
        <h2>开源信息</h2>
        
        <h3>项目信息</h3>
        <p>PDF处理器是一个开源项目，旨在为用户提供高质量的PDF处理工具。我们相信开源软件的力量，致力于创建一个开放、协作的开发环境。</p>
        
        <h3>开源商用意图</h3>
        <p>我们明确声明，PDF处理器的设计和开发具有以下商用意图：</p>
        <ol>
        <li><b>企业级功能</b>: 软件设计时充分考虑了企业用户的需求，提供了企业环境中所需的各项功能</li>
        <li><b>商业友好许可证</b>: 采用MIT许可证，允许商业使用、修改和再分发</li>
        <li><b>稳定性和可靠性</b>: 软件经过严格测试，确保在商业环境中的稳定运行</li>
        <li><b>技术支持</b>: 我们提供商业技术支持服务（需额外付费）</li>
        <li><b>定制开发</b>: 支持根据企业特定需求进行定制开发</li>
        </ol>
        
        <h3>贡献与社区</h3>
        <p>我们欢迎社区贡献，包括但不限于：</p>
        <ul>
        <li>代码贡献</li>
        <li>文档改进</li>
        <li>问题报告</li>
        <li>功能建议</li>
        <li>翻译工作</li>
        </ul>
        <p>所有贡献者都将被记录在项目的贡献者名单中。</p>
        
        <h3>获取源代码</h3>
        <p>源代码可以从以下地址获取：</p>
        <p>Github: <a href="https://github.com/your-username/pdf-processor">https://github.com/your-username/pdf-processor</a></p>
        <p>您也可以通过Git克隆仓库：</p>
        <code>git clone https://github.com/your-username/pdf-processor.git</code>
        """)
        open_source_layout.addWidget(open_source_text)
        tab_widget.addTab(open_source_widget, "开源信息")
        
        # 项目架构标签
        architecture_widget = QWidget()
        architecture_layout = QVBoxLayout(architecture_widget)
        architecture_text = QTextEdit()
        architecture_text.setReadOnly(True)
        architecture_text.setHtml("""
        <h2>项目架构</h2>
        
        <h3>项目结构</h3>
        <pre>
pdf_processor/
├── main.py                # 程序入口点
├── __init__.py            # 包初始化文件
├── core/                  # 核心引擎层
│   ├── __init__.py
│   ├── pdf_engine.py      # 基础PDF操作（拆分/合并/加密）
│   ├── conversion.py       # 格式转换逻辑
│   ├── editor.py          # PDF编辑功能
│   ├── forms.py           # 表单处理功能
│   ├── security.py        # 安全功能（数字签名/权限控制）
│   ├── ocr.py             # OCR光学字符识别功能
│   ├── optimization.py    # PDF优化和压缩功能
│   ├── comparison.py      # PDF文档比较功能
│   ├── interface.py       # 统一接口模块
│   └── analytics.py       # 数据分析功能
├── ui/                    # GUI层
│   ├── __init__.py
│   ├── main_window.py     # 主窗口逻辑（按企划文档设计）
│   ├── modern_style.css   # 现代样式表
│   └── dialogs/           # 对话框组件
│       ├── __init__.py
│       ├── about_dialog.py
│       └── settings_dialog.py
├── utils/                 # 工具模块
│   ├── __init__.py
│   ├── cache.py           # 操作缓存
│   ├── logger.py          # 日志记录
│   ├── file_handler.py    # 文件操作工具
│   ├── performance_monitor.py # 性能监控
│   └── validators.py      # 数据验证工具
├── plugins/               # 插件系统
│   ├── __init__.py
│   ├── page_numbering.py  # 页码插件
│   ├── watermark.py       # 水印插件
│   ├── plugin_interface.py # 插件接口
│   └── plugin_loader.py   # 插件管理器
├── config/                # 配置文件
│   ├── __init__.py
│   └── settings.py        # 用户设置
├── tests/                 # 测试文件
│   ├── __init__.py
│   ├── test_conversion.py
│   ├── test_editor.py
│   ├── test_pdf_engine.py
│   └── test_performance.py
└── docs/                  # 文档
    └── ...
        </pre>
        
        <h3>项目架构图</h3>
        <pre>
┌─────────────────────────────────────────────────────────────┐
│                    PDF处理器应用架构                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                  用户界面层 (UI)                     │    │
│  │  ┌──────────────┐ ┌──────────────────────────────┐  │    │
│  │  │ 主窗口模块    │ │        对话框模块            │  │    │
│  │  │ main_window  │ │ about_dialog,settings_dialog │  │    │
│  │  └──────────────┘ └──────────────────────────────┘  │    │
│  └─────────────────────────────────────────────────────┘    │
│                         │                                   │
│                         ▼                                   │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                  核心业务逻辑层                      │    │
│  │  ┌─────────────┐ ┌─────────────┐ ┌──────────────┐   │    │
│  │  │ PDF引擎模块  │ │ 转换模块     │ │ 编辑模块      │   │    │
│  │  │ pdf_engine  │ │ conversion  │ │ editor       │   │    │
│  │  ├─────────────┤ ├─────────────┤ ├──────────────┤   │    │
│  │  │ 安全模块     │ │ 表单模块     │ │ OCR模块       │   │    │
│  │  │ security    │ │ forms       │ │ ocr          │   │    │
│  │  ├─────────────┤ ├─────────────┤ ├──────────────┤   │    │
│  │  │ 优化模块     │ │ 比较模块     │ │ 分析模块      │   │    │
│  │  │ optimization│ │ comparison  │ │ analytics    │   │    │
│  │  └─────────────┘ └─────────────┘ └──────────────┘   │    │
│  └─────────────────────────────────────────────────────┘    │
│                         │                                   │
│                         ▼                                   │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                   接口标准化层                        │    │
│  │  ┌─────────────┐ ┌─────────────┐ ┌──────────────┐   │    │
│  │  │ 统一接口模块  │ │ 异常处理模块  │ │ 处理上下文模块  │   │    │
│  │  │ interface   │ │ exceptions  │ │              │   │    │
│  │  └─────────────┘ └─────────────┘ └──────────────┘   │    │
│  └─────────────────────────────────────────────────────┘    │
│                         │                                   │
│                         ▼                                   │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                   功能扩展层                         │    │
│  │  ┌─────────────┐ ┌─────────────┐ ┌──────────────┐   │    │
│  │  │ 插件管理器   │ │ 批量处理器   │ │ 历史管理器    │   │    │
│  │  │ plugin_loader│ │batch_processor│history_manager│   │    │
│  │  ├─────────────┤ ├─────────────┤ ├──────────────┤   │    │
│  │  │ 页码插件     │ │ 水印插件     │ │              │   │    │
│  │  │page_numbering│ │ watermark   │ │              │   │    │
│  │  └─────────────┘ └─────────────┘ └──────────────┘   │    │
│  └─────────────────────────────────────────────────────┘    │
│                         │                                   │
│                         ▼                                   │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                   基础服务层                         │    │
│  │  ┌─────────────┐ ┌─────────────┐ ┌──────────────┐   │    │
│  │  │ 配置管理模块 │ │ 工具模块     │ │ 日志模块      │   │    │
│  │  │ config      │ │ utils       │ │ logger       │   │    │
│  │  ├─────────────┤ ├─────────────┤ ├──────────────┤   │    │
│  │  │ 缓存模块     │ │ 文件处理模块 │ │ 性能监控模块   │   │    │
│  │  │ cache       │ │ file_handler│ │performance_  │   │    │
│  │  │             │ │             │ │monitor       │   │    │
│  │  └─────────────┘ └─────────────┘ └──────────────┘   │    │
│  └─────────────────────────────────────────────────────┘    │
│                         │                                   │
│                         ▼                                   │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                   系统接入层                         │    │
│  │  ┌─────────────┐ ┌─────────────┐ ┌──────────────┐   │    │
│  │  │   PyPDF2    │ │  PyQt5      │ │  reportlab   │   │    │
│  │  ├─────────────┤ ├─────────────┤ ├──────────────┤   │    │
│  │  │ pytesseract │ │ Pillow      │ │ PyHanko      │   │    │
│  │  └─────────────┘ └─────────────┘ └──────────────┘   │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
        </pre>
        
        <h3>架构说明</h3>
        <p>PDF处理器采用分层架构设计，各层之间职责明确，依赖关系清晰：</p>
        
        <h4>用户界面层 (UI)</h4>
        <p>负责与用户交互，包括主窗口、对话框等图形界面组件。</p>
        
        <h4>核心业务逻辑层</h4>
        <p>实现PDF处理的核心功能，包括PDF引擎、格式转换、编辑、安全、OCR等模块。</p>
        
        <h4>接口标准化层</h4>
        <p>为各核心模块提供统一的接口标准，包括：</p>
        <ul>
        <li><b>统一接口模块</b>: 定义ModuleInterface基类，所有核心模块都继承自该类</li>
        <li><b>异常处理模块</b>: 定义统一的异常类体系</li>
        <li><b>处理上下文模块</b>: 提供模块间数据传递的标准方式</li>
        </ul>
        
        <h4>功能扩展层</h4>
        <p>提供插件系统和批量处理等扩展功能。</p>
        
        <h4>基础服务层</h4>
        <p>提供日志、配置、缓存、性能监控等基础服务。</p>
        
        <h4>系统接入层</h4>
        <p>集成第三方库和系统组件。</p>
        """)
        architecture_layout.addWidget(architecture_text)
        tab_widget.addTab(architecture_widget, "项目架构")
        
        about_layout.addWidget(tab_widget)
        self.stacked_widget.addWidget(about_widget)
        self.stacked_widget.addWidget(about_widget)