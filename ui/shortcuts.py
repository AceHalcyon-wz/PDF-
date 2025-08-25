#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
快捷键管理模块
"""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QShortcut, QAction


class ShortcutManager:
    """快捷键管理器"""

    def __init__(self, parent):
        """
        初始化快捷键管理器
        
        Args:
            parent (QWidget): 父级窗口
        """
        self.parent = parent
        self.shortcuts = {}
        self._setup_shortcuts()

    def _setup_shortcuts(self):
        """设置快捷键"""
        # 定义快捷键映射
        shortcut_map = {
            #'open_file': (QKeySequence.Open, self.parent.open_file),  # 暂时注释掉不存在的方法
            #'save_file': (QKeySequence.Save, self.parent.save_file),  # 暂时注释掉不存在的方法
            'quit_app': (QKeySequence.Quit, self.parent.close),
            #'undo_action': (QKeySequence.Undo, self.parent.undo_action),  # 暂时注释掉不存在的方法
            #'redo_action': (QKeySequence.Redo, self.parent.redo_action),  # 暂时注释掉不存在的方法
            #'copy_action': (QKeySequence.Copy, self.parent.copy_action),  # 暂时注释掉不存在的方法
            #'cut_action': (QKeySequence.Cut, self.parent.cut_action),  # 暂时注释掉不存在的方法
            #'paste_action': (QKeySequence.Paste, self.parent.paste_action),  # 暂时注释掉不存在的方法
            #'select_all': (QKeySequence.SelectAll, self.parent.select_all),  # 暂时注释掉不存在的方法
            #'find_text': (QKeySequence.Find, self.parent.find_text),  # 暂时注释掉不存在的方法
            #'find_next': (QKeySequence.FindNext, self.parent.find_next),  # 暂时注释掉不存在的方法
            #'find_previous': (QKeySequence.FindPrevious, self.parent.find_previous),  # 暂时注释掉不存在的方法
            #'help_contents': (QKeySequence.HelpContents, self.parent.show_help),  # 暂时注释掉不存在的方法
            #'fullscreen': (QKeySequence.FullScreen, self.parent.toggle_fullscreen),  # 暂时注释掉不存在的方法
            #'zoom_in': (QKeySequence.ZoomIn, self.parent.zoom_in),  # 暂时注释掉不存在的方法
            #'zoom_out': (QKeySequence.ZoomOut, self.parent.zoom_out),  # 暂时注释掉不存在的方法
            #'print_file': (QKeySequence.Print, self.parent.print_file)  # 暂时注释掉不存在的方法
        }
        
        # 创建快捷键
        for name, (key_sequence, callback) in shortcut_map.items():
            shortcut = QShortcut(key_sequence, self.parent)
            shortcut.activated.connect(callback)
            self.shortcuts[name] = shortcut

    def add_shortcut(self, name, key_sequence, callback):
        """
        添加快捷键
        
        Args:
            name (str): 快捷键名称
            key_sequence (QKeySequence): 快捷键序列
            callback (callable): 回调函数
        """
        shortcut = QShortcut(key_sequence, self.parent)
        shortcut.activated.connect(callback)
        self.shortcuts[name] = shortcut

    def remove_shortcut(self, name):
        """
        移除快捷键
        
        Args:
            name (str): 快捷键名称
        """
        if name in self.shortcuts:
            del self.shortcuts[name]

    def get_shortcut(self, name):
        """
        获取快捷键
        
        Args:
            name (str): 快捷键名称
            
        Returns:
            QShortcut: 快捷键对象
        """
        return self.shortcuts.get(name)
        
    def update_shortcuts(self, shortcuts_dict):
        """
        更新快捷键设置
        
        Args:
            shortcuts_dict (dict): 快捷键字典，格式为 {功能名称: 快捷键字符串}
        """
        # 清除现有快捷键
        self.shortcuts.clear()
        
        # 根据新设置创建快捷键
        for action, key_str in shortcuts_dict.items():
            try:
                key_sequence = QKeySequence(key_str)
                # 根据功能名称映射到对应的回调函数
                callback = self._get_callback_for_action(action)
                if callback:
                    self.add_shortcut(action, key_sequence, callback)
            except Exception as e:
                print(f"无法为 {action} 创建快捷键 {key_str}: {e}")
                
    def _get_callback_for_action(self, action):
        """
        根据功能名称获取对应的回调函数
        
        Args:
            action (str): 功能名称
            
        Returns:
            callable: 对应的回调函数
        """
        action_map = {
            "打开文件": self.parent.open_file,
            "保存文件": self.parent.save_file,
            "新建窗口": self.parent.new_file,
            "打印文档": self.parent.print_file,
            "撤销": self.parent.undo_action,
            "重做": self.parent.redo_action,
            "复制": self.parent.copy_action,
            "粘贴": self.parent.paste_action,
            "全选": self.parent.select_all,
            "查找": self.parent.find_text,
            "替换": self.parent.replace_text,
            "帮助": self.parent.show_help,
            # "首选项": self.parent.show_preferences,  # 暂时注释掉不存在的方法
            "全屏": self.parent.toggle_fullscreen,
            "放大": self.parent.zoom_in,
            "缩小": self.parent.zoom_out,
            "关闭": self.parent.close
        }
        return action_map.get(action)