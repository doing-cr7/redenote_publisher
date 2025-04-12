import logging
import os
import signal
import sys

from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (QApplication, QHBoxLayout, QMainWindow,
                             QPushButton, QStackedWidget, QVBoxLayout, QWidget)

from src.config.config import Config
from src.core.browser import BrowserThread
from src.core.pages.home import HomePage
from src.core.pages.setting import SettingsPage
from src.core.pages.tools import ToolsPage
from src.core.pages.video import VideoPage
from src.logger.logger import Logger

# 设置日志文件路径
log_path = os.path.expanduser('~/Desktop/xhsai_error.log')
logging.basicConfig(filename=log_path, level=logging.DEBUG)

class XiaohongshuUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.config = Config()

        # 设置应用图标
        icon_path = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), 'build/icon.png')
        self.app_icon = QIcon(icon_path)
        QApplication.setWindowIcon(self.app_icon)
        self.setWindowIcon(self.app_icon)

        # 加载logger
        app_config = self.config.get_app_config()
        self.logger = Logger(is_console=app_config)

        self.logger.success("小红书发文助手启动")

        self.setWindowTitle("✨ 小红书发文助手")

        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: #f8f9fa;
            }}
            QLabel {{
                font-family: {("Menlo" if sys.platform == "darwin" else "Consolas")};
                color: #34495e;
                font-size: 11pt;
                border: none;
                background: transparent;
            }}
            QPushButton {{
                font-family: {("Menlo" if sys.platform == "darwin" else "Consolas")};
                font-size: 11pt;
                font-weight: bold;
                padding: 6px;
                background-color: #4a90e2;
                color: white;
                border: none;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: #357abd;
            }}
            QPushButton:disabled {{
                background-color: #cccccc;
            }}
            QLineEdit, QTextEdit, QComboBox {{
                font-family: {("Menlo" if sys.platform == "darwin" else "Consolas")};
                font-size: 11pt;
                padding: 4px;
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 4px;
            }}
            QFrame {{
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 6px;
            }}
            QScrollArea {{
                border: none;
            }}
            #sidebar {{
                background-color: #2c3e50;
                min-width: 60px;
                max-width: 60px;
                padding: 20px 0;
            }}
            #sidebar QPushButton {{
                background-color: transparent;
                border: none;
                border-radius: 0;
                color: #ecf0f1;
                padding: 15px 0;
                margin: 5px 0;
                font-size: 20px;
            }}
            #sidebar QPushButton:hover {{
                background-color: #34495e;
            }}
            #sidebar QPushButton:checked {{
                background-color: #34495e;
            }}
            #settingsPage {{
                background-color: white;
                padding: 20px;
            }}
        """)

        self.setMinimumSize(1000, 600)
        self.center()

        # 创建主窗口部件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # 创建水平布局
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 创建侧边栏
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # 创建侧边栏按钮
        home_btn = QPushButton("🏠")
        home_btn.setCheckable(True)
        home_btn.setChecked(True)
        home_btn.clicked.connect(lambda: self.switch_page(0))

        # 添加工具箱按钮
        tools_btn = QPushButton("🧰")
        tools_btn.setCheckable(True)
        tools_btn.clicked.connect(lambda: self.switch_page(1))

        # 添加视频发布按钮
        video_btn = QPushButton("🎥")
        video_btn.setCheckable(True)
        video_btn.clicked.connect(lambda: self.switch_page(2))

        settings_btn = QPushButton("⚙️")
        settings_btn.setCheckable(True)
        settings_btn.clicked.connect(lambda: self.switch_page(3))

        sidebar_layout.addWidget(home_btn)
        sidebar_layout.addWidget(tools_btn)
        sidebar_layout.addWidget(video_btn)
        sidebar_layout.addWidget(settings_btn)
        sidebar_layout.addStretch()

        # 添加侧边栏到主布局
        main_layout.addWidget(sidebar)

        # 创建堆叠窗口部件
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)

        # 创建并添加页面
        self.home_page = HomePage(self)
        self.tools_page = ToolsPage(self)
        self.video_page = VideoPage(self)
        self.settings_page = SettingsPage(self)

        # 将页面添加到堆叠窗口
        self.stack.addWidget(self.home_page)
        self.stack.insertWidget(1, self.tools_page)
        self.stack.insertWidget(2, self.video_page)
        self.stack.addWidget(self.settings_page)

        # 创建浏览器线程
        self.browser_thread = BrowserThread()
        # 连接信号
        self.browser_thread.login_status_changed.connect(
            self.update_login_button)
        self.browser_thread.preview_status_changed.connect(
            self.update_preview_button)
        self.browser_thread.login_success.connect(
            self.home_page.handle_poster_ready)
        self.browser_thread.login_error.connect(
            self.home_page.handle_login_error)
        self.browser_thread.preview_success.connect(
            self.home_page.handle_preview_result)
        self.browser_thread.preview_error.connect(
            self.home_page.handle_preview_error)
        self.browser_thread.start()
        
        # 启动下载器线程
        self.start_downloader_thread()

    def center(self):
        """将窗口移动到屏幕中央"""
        # 获取屏幕几何信息
        screen = QApplication.primaryScreen().geometry()
        # 获取窗口几何信息
        size = self.geometry()
        # 计算居中位置
        x = (screen.width() - size.width()) // 2
        y = (screen.height() - size.height()) // 2
        # 移动窗口
        self.move(x, y)

    def update_login_button(self, text, enabled):
        """更新登录按钮状态"""
        login_btn = self.findChild(QPushButton, "login_btn")
        if login_btn:
            login_btn.setText(text)
            login_btn.setEnabled(enabled)

    def update_preview_button(self, text, enabled):
        """更新预览按钮状态"""
        preview_btn = self.findChild(QPushButton, "preview_btn")
        if preview_btn:
            preview_btn.setText(text)
            preview_btn.setEnabled(enabled)

    def switch_page(self, index):
        # 切换页面
        self.stack.setCurrentIndex(index)

        # 更新按钮状态
        sidebar = self.findChild(QWidget, "sidebar")
        if sidebar:
            buttons = [btn for btn in sidebar.findChildren(QPushButton)]
            for i, btn in enumerate(buttons):
                btn.setChecked(i == index)

    def closeEvent(self, event):
        print("关闭应用")
        try:
            # 停止所有线程
            if hasattr(self, 'browser_thread'):
                self.browser_thread.stop()
                self.browser_thread.wait(1000)  # 等待最多1秒
                if self.browser_thread.isRunning():
                    self.browser_thread.terminate()  # 强制终止
                    self.browser_thread.wait()  # 等待终止完成

            if hasattr(self, 'generator_thread') and self.generator_thread.isRunning():
                self.generator_thread.terminate()
                self.generator_thread.wait()

            if hasattr(self, 'image_processor') and self.image_processor.isRunning():
                self.image_processor.terminate()
                self.image_processor.wait()

            # 清理资源
            self.images = []
            self.image_list = []
            self.current_image_index = 0
            # 关闭本机8000端口
            self.stop_downloader()
            # 调用父类的closeEvent
            super().closeEvent(event)

        except Exception as e:
            print(f"关闭应用程序时出错: {str(e)}")
            # 即使出错也强制关闭
            event.accept()
            
    def start_downloader_thread(self):
        """启动下载器线程"""
        try:
            import subprocess
            import threading
            
            def run_downloader():
                downloader_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src/bin/XhsAiDownloader')
                if sys.platform == "win32":
                    downloader_path += ".exe"
                    
                if os.path.exists(downloader_path):
                    try:
                        # 重定向标准输出和错误输出到 /dev/null 或 NUL
                        if sys.platform == "win32":
                            # 使用 start /b 命令在后台运行,避免弹出命令行窗口
                            subprocess.Popen(f"start /b {downloader_path} server", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        else:
                            subprocess.Popen(f"{downloader_path} server > /dev/null 2>&1", shell=True)
                        self.logger.success("下载器启动成功") 
                    except Exception as e:
                        self.logger.error(f"下载器启动失败: {str(e)}")
                else:
                    self.logger.error(f"下载器文件不存在: {downloader_path}")
                    
            # 创建并启动线程
            self.downloader_thread = threading.Thread(target=run_downloader, daemon=True)
            self.downloader_thread.start()
            
        except Exception as e:
            self.logger.error(f"启动下载器线程时出错: {str(e)}")
            
    def stop_downloader(self):
        """关闭下载器"""
        try:
            if sys.platform == "win32":
                # Windows系统使用netstat和taskkill命令
                import subprocess
                cmd = 'netstat -ano | findstr :8000'
                try:
                    result = subprocess.check_output(cmd, shell=True).decode()
                    if result:
                        # 提取PID
                        pid = result.strip().split()[-1]
                        kill_cmd = f'taskkill /F /PID {pid}'
                        subprocess.check_output(kill_cmd, shell=True)
                        self.logger.success("Windows下载器关闭成功")
                except Exception as e:
                    self.logger.error(f"Windows下载器关闭失败: {str(e)}")
            else:
                # Linux/Mac系统使用lsof和ps命令
                import subprocess
                try:
                    # 先尝试使用ps命令查找XhsAiDownloader进程
                    ps_cmd = "ps aux | grep XhsAiDownloader | grep -v grep | awk '{print $2}'"
                    pids = subprocess.check_output(ps_cmd, shell=True).decode().strip().split('\n')
                    
                    if not pids or not pids[0]:
                        # 如果ps命令没找到,再尝试用lsof查找8000端口
                        cmd = "lsof -i :8000 -t"
                        pids = subprocess.check_output(cmd, shell=True).decode().strip().split('\n')
                        
                    if pids and pids[0]:
                        # 终止所有相关进程
                        kill_cmd = f"kill -9 {' '.join(pids)}"
                        subprocess.check_output(kill_cmd, shell=True)
                        self.logger.success("Mac下载器关闭成功")
                    else:
                        self.logger.warning("未找到需要关闭的下载器进程")
                except Exception as e:
                    pass
                    # self.logger.error(f"Mac下载器关闭失败: {str(e)}")
                    
        except Exception as e:
            self.logger.error(f"关闭下载器时出错: {str(e)}")


if __name__ == "__main__":
    try:
        # 设置信号处理
        def signal_handler(signum, frame):
            print("\n正在退出程序...")
            QApplication.quit()
        # 注册信号处理器
        signal.signal(signal.SIGINT, signal_handler)

        app = QApplication(sys.argv)

        # 允许 CTRL+C 中断
        timer = QTimer()
        timer.timeout.connect(lambda: None)
        timer.start(100)

        window = XiaohongshuUI()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        logging.exception("程序运行出错：")
        raise
