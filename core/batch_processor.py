#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
批量处理功能模块
"""

from datetime import datetime
import time
import os
import re
from core.pdf_engine import PDFEngine
from core.conversion import ConversionEngine
from core.editor import EditorEngine


class BatchProcessor:
    """批量处理器类"""

    def __init__(self):
        """初始化批量处理器"""
        self.tasks = []
        self.templates = {}
        self.history = []
        self.scheduled_tasks = []
        # 初始化处理引擎
        self.pdf_engine = PDFEngine()
        self.conversion_engine = ConversionEngine()
        self.editor_engine = EditorEngine()

    def add_task(self, task):
        """
        添加处理任务
        
        Args:
            task (dict): 任务信息
        """
        task['id'] = len(self.tasks) + 1
        task['status'] = 'pending'  # pending, processing, completed, failed
        task['created_time'] = datetime.now()
        self.tasks.append(task)

    def remove_task(self, index):
        """
        移除处理任务
        
        Args:
            index (int): 任务索引
        """
        if 0 <= index < len(self.tasks):
            del self.tasks[index]

    def clear_tasks(self):
        """清空任务队列"""
        self.tasks.clear()

    def save_template(self, name, task_config):
        """
        保存处理模板
        
        Args:
            name (str): 模板名称
            task_config (dict): 任务配置
        """
        self.templates[name] = {
            'config': task_config,
            'created_time': datetime.now()
        }

    def load_template(self, name):
        """
        加载处理模板
        
        Args:
            name (str): 模板名称
            
        Returns:
            dict: 任务配置
        """
        template = self.templates.get(name, None)
        return template['config'] if template else None

    def list_templates(self):
        """
        列出所有模板
        
        Returns:
            list: 模板名称列表
        """
        return list(self.templates.keys())

    def execute_batch(self, progress_callback=None):
        """
        执行批量处理
        
        Args:
            progress_callback (function): 进度更新回调函数
            
        Returns:
            dict: 处理结果
        """
        results = {
            'total': len(self.tasks),
            'success': 0,
            'failed': 0,
            'details': []
        }
        
        total_tasks = len(self.tasks)
        for i, task in enumerate(self.tasks):
            task['status'] = 'processing'
            task['start_time'] = datetime.now()
            
            # 更新进度
            if progress_callback:
                progress_callback(int((i / total_tasks) * 100))
            
            try:
                # 根据任务类型执行不同的操作
                task_type = task.get('type', 'unknown')
                result = self._execute_task(task_type, task)
                
                task['status'] = 'completed'
                task['end_time'] = datetime.now()
                results['success'] += 1
                results['details'].append({
                    'task_id': task['id'],
                    'status': 'success',
                    'message': f'任务 {task_type} 执行成功',
                    'result': result
                })
                
            except Exception as e:
                task['status'] = 'failed'
                task['end_time'] = datetime.now()
                task['error'] = str(e)
                results['failed'] += 1
                results['details'].append({
                    'task_id': task['id'],
                    'status': 'failed',
                    'message': str(e)
                })
        
        # 记录到历史
        self.history.append({
            'execution_time': datetime.now(),
            'results': results
        })
        
        # 最后更新进度为100%
        if progress_callback:
            progress_callback(100)
        
        return results

    def _execute_task(self, task_type, task):
        """
        执行单个任务
        
        Args:
            task_type (str): 任务类型
            task (dict): 任务信息
            
        Returns:
            任务执行结果
        """
        if task_type == 'split':
            pages = task.get('pages', [])
            return self.pdf_engine.split_pdf(
                task.get('input_path'), 
                task.get('output_path'), 
                pages
            )
        elif task_type == 'merge':
            return self.pdf_engine.merge_pdfs(
                task.get('input_paths', []), 
                task.get('output_path')
            )
        elif task_type == 'compress':
            return self.pdf_engine.compress_pdf(
                task.get('input_path'), 
                task.get('output_path')
            )
        elif task_type == 'rotate':
            return self.pdf_engine.rotate_pdf(
                task.get('input_path'), 
                task.get('output_path'), 
                task.get('angle', 0)
            )
        elif task_type == 'delete_pages':
            pages = task.get('pages', [])
            return self.editor_engine.delete_pages(
                task.get('input_path'), 
                task.get('output_path'), 
                pages
            )
        elif task_type == 'reorder_pages':
            order = task.get('order', [])
            return self.editor_engine.reorder_pages(
                task.get('input_path'), 
                task.get('output_path'), 
                order
            )
        elif task_type == 'pdf_to_text':
            return self.conversion_engine.pdf_to_text(
                task.get('input_path'), 
                task.get('output_path')
            )
        elif task_type == 'image_to_pdf':
            return self.conversion_engine.image_to_pdf(
                task.get('input_paths', []), 
                task.get('output_path')
            )
        else:
            raise Exception(f'不支持的任务类型: {task_type}')

    def schedule_task(self, task, schedule_time):
        """
        定时任务处理
        
        Args:
            task (dict): 任务信息
            schedule_time (datetime): 定时执行时间
        """
        scheduled_task = {
            'task': task,
            'schedule_time': schedule_time,
            'id': len(self.scheduled_tasks) + 1
        }
        self.scheduled_tasks.append(scheduled_task)
        return scheduled_task['id']

    def get_scheduled_tasks(self):
        """
        获取所有定时任务
        
        Returns:
            list: 定时任务列表
        """
        return self.scheduled_tasks

    def remove_scheduled_task(self, task_id):
        """
        移除定时任务
        
        Args:
            task_id (int): 任务ID
        """
        self.scheduled_tasks = [task for task in self.scheduled_tasks if task['id'] != task_id]

    def check_scheduled_tasks(self):
        """
        检查并执行到期的定时任务
        
        Returns:
            list: 已执行的任务列表
        """
        executed_tasks = []
        current_time = datetime.now()
        
        for scheduled_task in self.scheduled_tasks[:]:  # 使用切片复制列表以避免在迭代时修改
            if scheduled_task['schedule_time'] <= current_time:
                # 执行任务
                try:
                    task = scheduled_task['task']
                    task_type = task.get('type', 'unknown')
                    result = self._execute_task(task_type, task)
                    executed_tasks.append({
                        'task_id': scheduled_task['id'],
                        'status': 'success',
                        'result': result
                    })
                except Exception as e:
                    executed_tasks.append({
                        'task_id': scheduled_task['id'],
                        'status': 'failed',
                        'error': str(e)
                    })
                
                # 移除已执行的任务
                self.scheduled_tasks.remove(scheduled_task)
        
        return executed_tasks

    def batch_rename_files(self, file_list, naming_pattern, output_dir=None):
        """
        批量重命名功能
        
        Args:
            file_list (list): 文件路径列表
            naming_pattern (str): 命名模式，支持占位符如 {index}, {name}, {ext}, {date}
            output_dir (str): 输出目录，如果为None则在原目录重命名
            
        Returns:
            list: 重命名结果列表
        """
        results = []
        date_str = datetime.now().strftime("%Y%m%d")
        
        for i, file_path in enumerate(file_list):
            try:
                # 获取文件信息
                file_dir, file_name = os.path.split(file_path)
                file_name_without_ext, file_ext = os.path.splitext(file_name)
                
                # 根据命名模式生成新文件名
                new_name = naming_pattern.format(
                    index=i+1,
                    name=file_name_without_ext,
                    ext=file_ext.lstrip('.'),
                    date=date_str
                )
                
                # 确定输出路径
                if output_dir:
                    # 确保输出目录存在
                    if not os.path.exists(output_dir):
                        os.makedirs(output_dir)
                    new_path = os.path.join(output_dir, new_name)
                else:
                    new_path = os.path.join(file_dir, new_name)
                
                # 重命名文件
                os.rename(file_path, new_path)
                
                results.append({
                    'original_path': file_path,
                    'new_path': new_path,
                    'success': True,
                    'error': None
                })
            except Exception as e:
                results.append({
                    'original_path': file_path,
                    'new_path': None,
                    'success': False,
                    'error': str(e)
                })
        
        return results