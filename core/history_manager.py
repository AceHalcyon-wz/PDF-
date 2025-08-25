#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
历史记录管理模块
参考企划文档中的历史记录功能设计
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any


class HistoryManager:
    """历史记录管理类"""
    
    def __init__(self, history_file: str = "history.json"):
        """初始化历史记录管理器"""
        self.history_file = history_file
        self.history: List[Dict[str, Any]] = []
        self.load_history()
        
    def add_record(self, operation: str, input_files: List[str], output_files: List[str], 
                   success: bool = True, error_message: str = ""):
        """添加历史记录"""
        record = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "input_files": input_files,
            "output_files": output_files,
            "success": success,
            "error_message": error_message
        }
        self.history.append(record)
        self.save_history()
        
    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """获取历史记录"""
        # 返回最近的记录，按时间倒序排列
        return sorted(self.history, key=lambda x: x["timestamp"], reverse=True)[:limit]
        
    def clear_history(self):
        """清空历史记录"""
        self.history = []
        self.save_history()
        
    def delete_record(self, timestamp: str):
        """删除指定记录"""
        self.history = [record for record in self.history if record["timestamp"] != timestamp]
        self.save_history()
        
    def save_history(self):
        """保存历史记录到文件"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存历史记录失败: {e}")
            
    def load_history(self):
        """从文件加载历史记录"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
            except Exception as e:
                print(f"加载历史记录失败: {e}")
                self.history = []
        else:
            self.history = []