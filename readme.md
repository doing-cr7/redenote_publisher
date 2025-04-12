# 小红书发文助手

<div align="center">

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)
[![Version](https://img.shields.io/badge/version-1.0.0-orange.svg)](https://github.com/yourusername/xhs_ai_publisher/releases)

[简体中文](./readme.md) | [English](./readme_en.md)

</div>

## ✨ 项目简介

`xhs_ai_publisher` 是一个基于 Python 的自动化工具，专为小红书平台内容创作者设计。该项目结合了图形用户界面与自动化脚本，利用大模型技术生成内容，并通过浏览器自动登录和发布文章，旨在简化内容创作与发布流程。

![软件界面效果](./images/new_ui.gif)

## 🚀 功能特点

- **智能内容生成**：利用大模型技术自动生成文章标题和内容
- **图片智能处理**：自动下载并预览封面图和内容图片
- **便捷登录**：支持手机号登录，自动保存登录凭证
- **一键发布**：支持文章预览和自动发布
- **用户友好界面**：简洁直观的图形界面操作
- **定时发布**：支持定时任务，自动发布文章

## 📁 项目结构

```
xhs_ai_publisher/
├── src/                    # 源代码目录
│   ├── core/              # 核心功能模块
│   │   ├── processor/     # 内容处理模块
│   │   ├── browser/       # 浏览器自动化
│   │   └── pages/         # 界面页面
│   ├── cron/              # 定时任务
│   ├── logger/            # 日志模块
│   └── config/            # 配置模块
├── static/                # 静态资源
├── test/                  # 测试目录
├── build/                 # 构建输出
├── main.py                # 主程序入口
└── requirements.txt       # 依赖包列表
```

## 🛠️ 安装与使用

### 环境要求

- Python 3.8+
- Chrome 浏览器
- 其他依赖见 requirements.txt

## 📋 待办事项

- **内容库**：计划添加内容库功能，支持保存和管理多种类型的内容素材
- **模板库**：开发模板库系统，提供多种预设模板，方便快速创建不同风格的文章


### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/yourusername/xhs_ai_publisher.git
cd xhs_ai_publisher
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```
3. **安装游览器依赖**
```bash
playwright install chromium
```
4. **运行程序**
```bash
python main.py
```

### 使用流程

1. 启动程序后，输入手机号登录小红书账户
2. 在标题编辑区设置文章标题和作者信息
3. 在内容输入区输入文章主题
4. 点击"生成内容"按钮生成文章
5. 预览生成的内容和配图
6. 确认无误后点击"预览发布"

## 📦 快速使用

如果您不想配置开发环境，可以直接下载打包好的 Windows 可执行程序：

[百度网盘下载链接](https://pan.baidu.com/s/1rIQ-ZgyHYN_ncVXlery4yQ)  
提取码: iqiy

### 使用说明
1. 下载并解压压缩包
2. 运行文件夹中的 `easy_ui.exe`
3. 按照界面提示操作即可

### 注意事项
- 仅支持 Windows 系统
- 首次运行可能需要等待较长时间加载
- 如遇到杀毒软件报警，请添加信任

## 📝 注意事项

- 确保已安装 Chrome 浏览器，并下载对应版本的 ChromeDriver
- 登录过程中需要输入验证码，请确保手机畅通
- 发布文章前，请核对生成的内容和图片，确保符合发布要求
- 建议定期备份登录凭证和配置文件

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request 来帮助改进项目。

## 📞 联系方式

### 我新建了一个群聊，如果有任何问题或者需求，都可以进群沟通
<img src="images/wechat_talking.jpg" width="200" height="200">

### 公众号
<img src="images/mp_qr.jpg" width="200" height="200">

---   

<div align="center">
  <sub>Built with ❤️ for Xiaohongshu content creators</sub>
</div>
