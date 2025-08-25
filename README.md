# PDF处理器

## 项目概述

PDF处理器是一个基于Python的桌面应用程序，旨在为用户提供一套完整的PDF文档处理工具。该应用程序采用模块化架构设计，支持本地运行，兼容企业环境，并可打包为商业软件。

## 依赖管理

本项目使用现代Python标准的 `pyproject.toml` 文件来管理依赖，不再使用传统的 `requirements.txt` 文件。

安装依赖：
```bash
pip install -e .
```

安装开发依赖：
```bash
pip install -e ".[dev]"
```

## 功能特性

### 基础PDF处理功能
- PDF拆分（按页数、按范围、配对拆分）
- PDF合并
- PDF压缩
- PDF页面旋转

### 格式转换功能
- PDF转文本、图像（PNG/JPG/BMP/TIFF/WebP）
- 图像转PDF
- PDF转Word/Excel/PPT
- Word/Excel/PPT转PDF
- 文本转PDF
- PDF转HTML/Markdown/EPUB/CSV

### 安全处理功能
- PDF加密/解密
- 权限控制
- 数字签名添加与验证

### 编辑功能
- 页面删除、插入、替换、重新排序
- 页眉页脚添加
- 页面背景设置