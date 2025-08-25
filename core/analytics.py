#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据分析功能模块

接口状态: 已更新以符合统一接口标准ModuleInterface
更新内容:
1. 继承ModuleInterface基类
2. 使用标准日志记录方法
3. 实现标准接口方法
"""

from PyPDF2 import PdfReader
import os
from utils.performance_optimizer import PerformanceOptimizer
from collections import Counter
from datetime import datetime
from core.interface import ModuleInterface


class AnalyticsEngine(ModuleInterface):
    """数据分析引擎类"""
    
    def __init__(self):
        """初始化数据分析引擎"""
        super().__init__("analytics")
        self.performance_optimizer = PerformanceOptimizer()
        self.log_info("数据分析引擎初始化完成")

    def get_document_statistics(self, input_path):
        """
        获取文档统计信息
        
        Args:
            input_path (str): 输入PDF文件路径
            
        Returns:
            dict: 文档统计信息
        """
        try:
            self.log_info(f"开始获取文档统计信息")
            
            # 读取PDF文件
            reader = PdfReader(input_path)
            
            # 获取基本统计信息
            stats = {
                'file_name': os.path.basename(input_path),
                'page_count': len(reader.pages),
                'file_size': os.path.getsize(input_path)
            }
            
            # 提取文本并统计
            total_text = ""
            for page in reader.pages:
                total_text += page.extract_text()
            
            stats['character_count'] = len(total_text)
            stats['word_count'] = len(total_text.split())
            stats['line_count'] = len(total_text.splitlines())
            
            # 页面尺寸信息
            if reader.pages:
                first_page = reader.pages[0]
                box = first_page.mediabox
                stats['page_size'] = {
                    'width': float(box.width),
                    'height': float(box.height)
                }
            
            self.log_info(f"文档统计信息获取完成")
            return stats
        except Exception as e:
            self.log_error(f"获取文档统计信息失败: {str(e)}")
            raise Exception(f"获取文档统计信息失败: {str(e)}")

    def generate_processing_report(self, processing_data, output_path):
        """
        生成处理报告
        
        Args:
            processing_data (dict): 处理数据
            output_path (str): 输出报告文件路径
        """
        try:
            self.log_info(f"开始生成处理报告")
            
            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            # 获取文档统计信息
            stats = self.get_document_statistics(input_path)
            
            # 生成报告内容
            report_content = f"""
PDF处理报告
===========

基本信息:
- 文件名: {stats['file_name']}
- 文件大小: {stats['file_size']} 字节
- 页数: {stats['page_count']} 页

内容统计:
- 字符数: {stats['character_count']}
- 单词数: {stats['word_count']}
- 行数: {stats['line_count']}

页面信息:
- 页面尺寸: {stats.get('page_size', {}).get('width', 'N/A')} x {stats.get('page_size', {}).get('height', 'N/A')} 点

报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            # 保存报告
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
                
            self.log_info(f"处理报告生成完成: {output_path}")
        except Exception as e:
            self.log_error(f"生成处理报告失败: {str(e)}")
            raise Exception(f"生成处理报告失败: {str(e)}")

    def analyze_usage_patterns(self, usage_data):
        """
        分析使用情况
        
        Args:
            usage_data (list): 使用数据列表
            
        Returns:
            dict: 使用情况分析结果
        """
        try:
            if not usage_data:
                return {
                    'total_operations': 0,
                    'most_used_function': None,
                    'usage_by_function': {},
                    'usage_by_time': {}
                }
            
            # 统计各功能使用次数
            function_counter = Counter()
            time_counter = Counter()
            
            for record in usage_data:
                # 统计功能使用情况
                function = record.get('operation', 'unknown')
                function_counter[function] += 1
                
                # 统计时间使用情况（按小时）
                timestamp = record.get('timestamp')
                if timestamp:
                    try:
                        dt = datetime.fromisoformat(timestamp)
                        hour = dt.hour
                        time_counter[hour] += 1
                    except:
                        pass
            
            # 找出最常用的功能
            most_used_function = function_counter.most_common(1)[0] if function_counter else (None, 0)
            
            return {
                'total_operations': len(usage_data),
                'most_used_function': most_used_function[0],
                'usage_count': most_used_function[1],
                'usage_by_function': dict(function_counter),
                'usage_by_time': dict(time_counter)
            }
        except Exception as e:
            raise Exception(f"使用情况分析失败: {str(e)}")

    def monitor_performance(self):
        """
        性能监控
        
        Returns:
            dict: 性能监控数据
        """
        # 使用PerformanceOptimizer来获取性能数据
        return self.performance_optimizer.monitor_performance_data()

    def generate_analytics_report(self, analytics_data, output_path, report_format="txt"):
        """
        生成分析报告
        
        Args:
            analytics_data (dict): 分析数据
            output_path (str): 输出报告文件路径
            report_format (str): 报告格式 ("txt", "json", "html")
        """
        try:
            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            if report_format == "json":
                import json
                # 生成JSON格式报告
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(analytics_data, f, ensure_ascii=False, indent=2)
                    
            elif report_format == "html":
                # 生成HTML格式报告
                html_content = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>PDF使用分析报告</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #333; }
        h2 { color: #666; }
        table { border-collapse: collapse; width: 100%; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .summary { background-color: #f9f9f9; padding: 15px; border-radius: 5px; margin: 10px 0; }
    </style>
</head>
<body>
    <h1>PDF使用分析报告</h1>
"""
                
                # 添加操作信息
                if 'operations' in analytics_data:
                    html_content += "<div class='section-header'>处理操作</div>\n"
                    html_content += "<ul>\n"
                    for op in analytics_data['operations']:
                        html_content += f"<li>{op}</li>\n"
                    html_content += "</ul>\n"
                
                # 添加统计信息
                stats = analytics_data.get('statistics', {})
                if stats:
                    html_content += "<div class='section-header'>文档统计</div>\n"
                    html_content += "<table>\n"
                    html_content += f"<tr><th>文件名</th><td>{stats.get('file_name', 'N/A')}</td></tr>\n"
                    html_content += f"<tr><th>页数</th><td>{stats.get('page_count', 'N/A')}</td></tr>\n"
                    html_content += f"<tr><th>文件大小</th><td>{stats.get('file_size', 'N/A')} 字节</td></tr>\n"
                    html_content += f"<tr><th>字符数</th><td>{stats.get('character_count', 'N/A')}</td></tr>\n"
                    html_content += f"<tr><th>单词数</th><td>{stats.get('word_count', 'N/A')}</td></tr>\n"
                    html_content += f"<tr><th>行数</th><td>{stats.get('line_count', 'N/A')}</td></tr>\n"
                    html_content += "</table>\n"
                
                # 添加功能使用情况
                usage_by_function = analytics_data.get('usage_by_function', {})
                if usage_by_function:
                    html_content += "<div class='section-header'>功能使用情况</div>\n"
                    html_content += "<table>\n"
                    html_content += "<tr><th>功能</th><th>使用次数</th></tr>\n"
                    for func, count in usage_by_function.items():
                        html_content += f"<tr><td>{func}</td><td>{count}</td></tr>\n"
                    html_content += "</table>\n"
                
                # 添加时间使用情况
                usage_by_time = analytics_data.get('usage_by_time', {})
                if usage_by_time:
                    html_content += "<div class='section-header'>时间使用情况</div>\n"
                    html_content += "<table>\n"
                    html_content += "<tr><th>时间段</th><th>使用次数</th></tr>\n"
                    for hour, count in sorted(usage_by_time.items()):
                        period = f"{hour}:00-{hour+1}:00"
                        html_content += f"<tr><td>{period}</td><td>{count}</td></tr>\n"
                    html_content += "</table>\n"
                
                html_content += """
</body>
</html>
"""
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                    
            else:  # 默认为文本格式
                # 生成文本格式报告
                report_content = "PDF使用分析报告\n"
                report_content += "=" * 50 + "\n\n"
                
                # 添加摘要信息
                if 'operations' in analytics_data:
                    report_content += "## 处理操作\n\n"
                    for op in analytics_data['operations']:
                        report_content += f"- {op}\n"
                    report_content += "\n"
                
                # 添加统计信息
                stats = analytics_data.get('statistics', {})
                if stats:
                    report_content += "## 文档统计\n\n"
                    report_content += f"""文件名: {stats.get('file_name', 'N/A')}
页数: {stats.get('page_count', 'N/A')}
文件大小: {stats.get('file_size', 'N/A')} 字节
字符数: {stats.get('character_count', 'N/A')}
单词数: {stats.get('word_count', 'N/A')}
行数: {stats.get('line_count', 'N/A')}
页面信息:
- 页面尺寸: {stats.get('page_size', {}).get('width', 'N/A')} x {stats.get('page_size', {}).get('height', 'N/A')} 点

"""
                
                # 添加功能使用情况
                usage_by_function = analytics_data.get('usage_by_function', {})
                if usage_by_function:
                    report_content += "功能使用情况:\n"
                    report_content += "-" * 20 + "\n"
                    for func, count in usage_by_function.items():
                        report_content += f"{func}: {count} 次\n"
                    report_content += "\n"
                
                # 添加时间使用情况
                usage_by_time = analytics_data.get('usage_by_time', {})
                if usage_by_time:
                    report_content += "时间使用情况:\n"
                    report_content += "-" * 20 + "\n"
                    for hour, count in sorted(usage_by_time.items()):
                        report_content += f"{hour}:00: {count} 次\n"
                    report_content += "\n"
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                
            return True
        except Exception as e:
            raise Exception(f"分析报告生成失败: {str(e)}")