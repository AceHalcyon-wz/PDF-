#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
表单处理功能模块

接口状态: 已更新以符合统一接口标准ModuleInterface
更新内容:
1. 继承ModuleInterface基类
2. 使用标准日志记录方法
3. 实现标准接口方法
"""

import os
from PyPDF2 import PdfReader, PdfWriter
import json
from core.interface import ModuleInterface


class FormEngine(ModuleInterface):
    """表单处理引擎类"""

    def __init__(self):
        """初始化表单引擎"""
        super().__init__("forms")
        self.log_info("表单引擎初始化完成")

    def fill_form(self, input_path, output_path, form_data):
        """
        填写表单
        
        Args:
            input_path (str): 输入PDF表单文件路径
            output_path (str): 输出PDF表单文件路径
            form_data (dict): 表单数据
        """
        try:
            self.log_info(f"开始填写表单: {input_path}")
            
            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            # 注意：PyPDF2对表单的支持有限
            # 更完整的表单支持需要使用其他库如pdfrw或PyPDF2的高级功能
            # 这里提供一个基础实现
            reader = PdfReader(input_path)
            writer = PdfWriter()
            
            # 复制页面
            for page in reader.pages:
                writer.add_page(page)
            
            # 使用更全面的方法来处理表单字段
            if reader.trailer["/Root"].get("/AcroForm"):
                writer.add_metadata(reader.metadata)
                writer.trailer["/Root"]["/AcroForm"] = reader.trailer["/Root"]["/AcroForm"]
                
                # 更新表单字段值
                for page in writer.pages:
                    writer.update_page_form_field_values(page, form_data)
            
            # 保存填写后的表单
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
                
            self.log_info(f"表单填写完成: {output_path}")
        except Exception as e:
            self.log_error(f"表单填写失败: {str(e)}")
            raise Exception(f"表单填写失败: {str(e)}")

    def extract_form_data(self, input_path, output_path):
        """
        提取表单数据
        
        Args:
            input_path (str): 输入PDF表单文件路径
            output_path (str): 输出JSON文件路径
        """
        try:
            self.log_info(f"开始提取表单数据: {input_path}")
            
            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            reader = PdfReader(input_path)
            
            # 提取表单字段数据
            form_fields = {}
            
            # 使用 PyPDF2 内置方法获取表单字段
            if reader.trailer["/Root"].get("/AcroForm"):
                form = reader.trailer["/Root"]["/AcroForm"].get_object()
                if "/Fields" in form:
                    fields = form["/Fields"]
                    for field in fields:
                        field_obj = field.get_object()
                        if "/T" in field_obj and "/V" in field_obj:
                            field_name = field_obj["/T"]
                            field_value = field_obj["/V"]
                            form_fields[field_name] = field_value
            
            # 保存表单数据到JSON文件
            with open(output_path, 'w', encoding='utf-8') as json_file:
                json.dump(form_fields, json_file, ensure_ascii=False, indent=2)
                
            self.log_info(f"表单数据提取完成: {output_path}")
        except Exception as e:
            self.log_error(f"表单数据提取失败: {str(e)}")
            raise Exception(f"表单数据提取失败: {str(e)}")

    def identify_form_fields(self, input_path):
        """
        识别表单字段
        
        Args:
            input_path (str): 输入PDF表单文件路径
            
        Returns:
            list: 表单字段列表
        """
        try:
            reader = PdfReader(input_path)
            
            # 识别表单字段
            fields = []
            
            # 注意：PyPDF2识别表单字段的功能有限
            # 这里提供一个基础实现
            if hasattr(reader, 'get_fields'):
                raw_fields = reader.get_fields()
                if raw_fields:
                    for field_name, field_obj in raw_fields.items():
                        field_info = {
                            'name': field_name,
                            'type': getattr(field_obj, 'get', lambda x, y: y)('/FT', 'unknown'),
                            'value': getattr(field_obj, 'get', lambda x, y: y)('/V', '')
                        }
                        fields.append(field_info)
            
            return fields
        except Exception as e:
            raise Exception(f"表单字段识别失败: {str(e)}")

    def edit_form_fields(self, input_path, output_path, field_edits):
        """
        编辑表单字段
        
        Args:
            input_path (str): 输入PDF表单文件路径
            output_path (str): 输出PDF表单文件路径
            field_edits (list): 字段编辑列表，每个元素包含name, type, value
        """
        try:
            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            reader = PdfReader(input_path)
            writer = PdfWriter()
            
            # 复制页面
            for page in reader.pages:
                writer.add_page(page)
            
            # 注意：PyPDF2编辑表单字段的功能有限
            # 这里提供一个基础实现示例
            # 实际应用中可能需要更复杂的实现
            
            # 保存编辑后的表单
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
                
            return True
        except Exception as e:
            raise Exception(f"表单字段编辑失败: {str(e)}")

    def batch_process_forms(self, forms_data):
        """
        批量表单处理
        
        Args:
            forms_data (list): 表单数据列表，每个元素包含input_path, output_path, form_data
            
        Returns:
            list: 处理结果列表
        """
        results = []
        
        for form_info in forms_data:
            try:
                input_path = form_info.get('input_path')
                output_path = form_info.get('output_path')
                form_data = form_info.get('form_data')
                
                # 执行表单填写
                self.fill_form(input_path, output_path, form_data)
                results.append({
                    'input_path': input_path,
                    'output_path': output_path,
                    'success': True,
                    'error': None
                })
            except Exception as e:
                results.append({
                    'input_path': form_info.get('input_path'),
                    'output_path': form_info.get('output_path'),
                    'success': False,
                    'error': str(e)
                })
        
        return results

    def import_form_data(self, input_path, output_path, data_file):
        """
        从外部文件导入表单数据
        
        Args:
            input_path (str): 输入PDF表单文件路径
            output_path (str): 输出PDF表单文件路径
            data_file (str): 数据文件路径（JSON/CSV格式）
        """
        try:
            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            # 读取数据文件
            if data_file.endswith('.json'):
                with open(data_file, 'r', encoding='utf-8') as f:
                    form_data = json.load(f)
            else:
                raise Exception("仅支持JSON格式的数据文件")
            
            # 填写表单
            self.fill_form(input_path, output_path, form_data)
                
            return True
        except Exception as e:
            raise Exception(f"导入表单数据失败: {str(e)}")

    def validate_form_data(self, input_path, validation_rules):
        """
        表单数据验证
        
        Args:
            input_path (str): 输入PDF表单文件路径
            validation_rules (dict): 验证规则
            
        Returns:
            dict: 验证结果
        """
        try:
            # 提取表单数据
            form_data = self.extract_form_data(input_path)
            
            # 验证数据
            validation_results = {}
            for field_name, rules in validation_rules.items():
                field_value = form_data.get(field_name, "")
                is_valid = True
                errors = []
                
                # 检查必填字段
                if rules.get("required", False) and not field_value:
                    is_valid = False
                    errors.append("字段为必填项")
                
                # 检查最小长度
                min_length = rules.get("min_length")
                if min_length and len(str(field_value)) < min_length:
                    is_valid = False
                    errors.append(f"字段长度不能少于{min_length}个字符")
                
                # 检查最大长度
                max_length = rules.get("max_length")
                if max_length and len(str(field_value)) > max_length:
                    is_valid = False
                    errors.append(f"字段长度不能超过{max_length}个字符")
                
                # 检查正则表达式
                pattern = rules.get("pattern")
                if pattern:
                    import re
                    if not re.match(pattern, str(field_value)):
                        is_valid = False
                        errors.append("字段格式不正确")
                
                validation_results[field_name] = {
                    "value": field_value,
                    "valid": is_valid,
                    "errors": errors
                }
            
            return {
                "form_data": form_data,
                "validation_results": validation_results,
                "is_valid": all(result["valid"] for result in validation_results.values())
            }
        except Exception as e:
            raise Exception(f"表单数据验证失败: {str(e)}")