#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PDF处理器主入口文件
"""

import sys
import os
import logging

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def setup_qt_environment():
    """设置Qt环境"""
    # 设置Qt平台插件路径 - 使用更精确的路径
    qt_plugin_paths = [
        os.path.join(project_root, '..', '.venv', 'Lib', 'site-packages', 'PyQt5', 'Qt5', 'plugins'),
        os.path.join(sys.prefix, 'Lib', 'site-packages', 'PyQt5', 'Qt5', 'plugins'),
        os.path.join(sys.prefix, 'lib', 'site-packages', 'PyQt5', 'Qt5', 'plugins'),  # Linux/Mac路径
        os.path.join(sys.prefix, 'Library', 'plugins'),  # Conda环境路径
    ]
    
    qt_plugin_path = None
    for path in qt_plugin_paths:
        if os.path.exists(path):
            qt_plugin_path = path
            break
    
    if qt_plugin_path:
        os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = qt_plugin_path
        print(f"设置Qt平台插件路径: {qt_plugin_path}")
    else:
        print("警告: 未找到Qt平台插件路径，可能影响界面显示")

# 在导入PyQt5之前设置环境
setup_qt_environment()

from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow
from utils.logger import LoggerManager

def setup_logging():
    """设置日志系统"""
    logger_manager = LoggerManager()
    logger = logger_manager.get_logger("main")
    logger.info("PDF处理器启动")
    return logger

def check_qt_installation():
    """检查Qt安装"""
    try:
        from PyQt5.QtWidgets import QApplication
        return True
    except ImportError as e:
        print(f"无法导入PyQt5: {e}")
        return False
    except Exception as e:
        print(f"Qt安装检查失败: {e}")
        return False

def main():
    """主函数，启动PDF处理器应用程序"""
    try:
        logger = setup_logging()
        
        # 检查Qt安装
        if not check_qt_installation():
            logger.error("PyQt5安装检查失败")
            print("请确保已正确安装PyQt5:")
            print("pip install PyQt5")
            sys.exit(1)
        
        print("正在创建QApplication实例...")
        app = QApplication(sys.argv)
        print("正在创建主窗口...")
        window = MainWindow()
        print("正在显示主窗口...")
        window.show()
        logger.info("主窗口已显示")
        exit_code = app.exec_()
        logger.info("PDF处理器退出")
        sys.exit(exit_code)
    except Exception as e:
        logging.exception("应用程序发生未处理的异常: %s", str(e))
        print(f"应用程序发生未处理的异常: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()