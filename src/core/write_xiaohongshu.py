# 小红书的自动发稿
from playwright.async_api import async_playwright
import time
import json
import os
import sys
import logging
import asyncio
from PyQt6.QtWidgets import QInputDialog, QLineEdit, QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog
from PyQt6.QtCore import QObject, pyqtSignal, QMetaObject, Qt, QThread, pyqtSlot
from PyQt6.QtGui import QPixmap
log_path = os.path.expanduser('~/Desktop/xhsai_error.log')
logging.basicConfig(filename=log_path, level=logging.DEBUG)

class VerificationCodeHandler(QObject):
    code_received = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.code = None
        self.dialog = None
        
    async def get_verification_code(self):
        # 确保在主线程中执行
        if QApplication.instance().thread() != QThread.currentThread():
            # 如果不在主线程，使用moveToThread移动到主线程
            self.moveToThread(QApplication.instance().thread())
            # 使用invokeMethod确保在主线程中执行
            QMetaObject.invokeMethod(self, "_show_dialog", Qt.ConnectionType.BlockingQueuedConnection)
        else:
            # 如果已经在主线程，直接执行
            self._show_dialog()
        
        # 等待代码输入完成
        while self.code is None:
            await asyncio.sleep(0.1)
            
        return self.code
    
    @pyqtSlot()
    def _show_dialog(self):
        code, ok = QInputDialog.getText(None, "验证码", "请输入验证码:", QLineEdit.EchoMode.Normal)
        if ok:
            self.code = code
            self.code_received.emit(code)
        else:
            self.code = ""

class XiaohongshuPoster:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.verification_handler = VerificationCodeHandler()
        self.loop = None
        # 不再在初始化时调用 initialize，而是让调用者显式调用
        
    async def initialize(self):
        """初始化浏览器"""
        if self.playwright is not None:
            return
            
        try:
            print("开始初始化Playwright...")
            self.playwright = await async_playwright().start()

            # 获取可执行文件所在目录
            launch_args = {
                'headless': False,
                'args': [
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--disable-extensions',
                    '--disable-infobars',
                    '--start-maximized',
                    '--ignore-certificate-errors',
                    '--ignore-ssl-errors'
                ]
            }

            chromium_path = None

            if getattr(sys, 'frozen', False):
                # 如果是打包后的可执行文件
                executable_dir = os.path.dirname(sys.executable)
                logging.debug(f"executable_dir: {executable_dir}")
                if sys.platform == 'darwin':  # macOS系统
                    if 'XhsAi' in executable_dir:
                        # 如果在 DMG 中运行
                        browser_path = os.path.join(
                            executable_dir, "ms-playwright")
                    else:
                        # 如果已经安装到应用程序文件夹
                        browser_path = os.path.join(
                            executable_dir, "Contents", "MacOS", "ms-playwright")
                    logging.debug(f"浏览器路径: {browser_path}")
                    chromium_path = os.path.join(
                        browser_path, "chromium-1161/chrome-mac/Chromium.app/Contents/MacOS/Chromium")
                else:
                    # Windows系统
                    executable_dir = sys._MEIPASS
                    print(f"临时解压目录: {executable_dir}")
                    browser_path = os.path.join(executable_dir, "ms-playwright")
                    print(f"浏览器路径: {browser_path}")
                    chromium_path = os.path.join(
                        browser_path, "chrome-win", "chrome.exe")
                    logging.debug(f"Chromium 路径: {chromium_path}")
            logging.debug(f"Chromium 路径: {chromium_path}")
            if chromium_path:
                # 确保浏览器文件存在且有执行权限
                if os.path.exists(chromium_path):
                    os.chmod(chromium_path, 0o755)
                    launch_args['executable_path'] = chromium_path
                else:
                    raise Exception(f"浏览器文件不存在: {chromium_path}")

            # 获取默认的 Chromium 可执行文件路径
            self.browser = await self.playwright.chromium.launch(**launch_args)
            # 创建新的上下文时设置权限
            self.context = await self.browser.new_context(
                permissions=['geolocation']  # 自动允许位置信息访问
            )
            self.page = await self.context.new_page()
            
            # 注入stealth.min.js
            stealth_js = """
            (function(){
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
                
                const getParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {
                    if (parameter === 37445) {
                        return 'Intel Open Source Technology Center';
                    }
                    if (parameter === 37446) {
                        return 'Mesa DRI Intel(R) HD Graphics (SKL GT2)';
                    }
                    return getParameter.apply(this, arguments);
                };
                
                const originalGetBoundingClientRect = Element.prototype.getBoundingClientRect;
                Element.prototype.getBoundingClientRect = function() {
                    const rect = originalGetBoundingClientRect.apply(this, arguments);
                    rect.width = Math.round(rect.width);
                    rect.height = Math.round(rect.height);
                    return rect;
                };
                
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['zh-CN', 'zh']
                });
                
                window.chrome = {
                    runtime: {}
                };
            })();
            """
            await self.page.add_init_script(stealth_js)
            
            print("浏览器启动成功！")
            logging.debug("浏览器启动成功！")
            
            # 获取用户主目录
            home_dir = os.path.expanduser('~')
            app_dir = os.path.join(home_dir, '.xhs_system')
            if not os.path.exists(app_dir):
                os.makedirs(app_dir)

            # 设置token和cookies文件路径
            self.token_file = os.path.join(app_dir, "xiaohongshu_token.json")
            self.cookies_file = os.path.join(app_dir, "xiaohongshu_cookies.json")
            self.token = self._load_token()
            await self._load_cookies()

        except Exception as e:
            print(f"初始化过程中出现错误: {str(e)}")
            logging.debug(f"初始化过程中出现错误: {str(e)}")
            await self.close(force=True)  # 确保资源被正确释放
            raise

    def _load_token(self):
        """从文件加载token"""
        if os.path.exists(self.token_file):
            try:
                with open(self.token_file, 'r') as f:
                    token_data = json.load(f)
                    # 检查token是否过期
                    if token_data.get('expire_time', 0) > time.time():
                        return token_data.get('token')
            except:
                pass
        return None

    def _save_token(self, token):
        """保存token到文件"""
        token_data = {
            'token': token,
            # token有效期设为30天
            'expire_time': time.time() + 30 * 24 * 3600
        }
        with open(self.token_file, 'w') as f:
            json.dump(token_data, f)

    async def _load_cookies(self):
        """从文件加载cookies"""
        if os.path.exists(self.cookies_file):
            try:
                with open(self.cookies_file, 'r') as f:
                    cookies = json.load(f)
                    # 确保cookies包含必要的字段
                    for cookie in cookies:
                        if 'domain' not in cookie:
                            cookie['domain'] = '.xiaohongshu.com'
                        if 'path' not in cookie:
                            cookie['path'] = '/'
                    await self.context.add_cookies(cookies)
            except Exception as e:
                logging.debug(f"加载cookies失败: {str(e)}")

    async def _save_cookies(self):
        """保存cookies到文件"""
        try:
            cookies = await self.context.cookies()
            with open(self.cookies_file, 'w') as f:
                json.dump(cookies, f)
        except Exception as e:
            logging.debug(f"保存cookies失败: {str(e)}")

    async def login(self, phone, country_code="+86"):
        """登录小红书"""
        await self.ensure_browser()  # 确保浏览器已初始化
        # 如果token有效则直接返回
        if self.token:
            return

        # 尝试加载cookies进行登录
        await self.page.goto("https://creator.xiaohongshu.com/login", wait_until="networkidle")
        # 先清除所有cookies
        await self.context.clear_cookies()
        
        # 重新加载cookies
        await self._load_cookies()
        # 刷新页面并等待加载完成
        await self.page.reload(wait_until="networkidle")

        # 检查是否已经登录
        current_url = self.page.url
        if "login" not in current_url:
            print("使用cookies登录成功")
            self.token = self._load_token()
            await self._save_cookies()
            return
        else:
            # 清理无效的cookies
            await self.context.clear_cookies()
            
        # 如果cookies登录失败，则进行手动登录
        await self.page.goto("https://creator.xiaohongshu.com/login")
        await asyncio.sleep(1)

        # 输入手机号
        await self.page.fill("//input[@placeholder='手机号']", phone)

        await asyncio.sleep(2)
        # 点击发送验证码按钮
        try:
            await self.page.click(".css-uyobdj")
        except:
            try:
                await self.page.click(".css-1vfl29")
            except:
                try:
                    await self.page.click("//button[text()='发送验证码']")
                except:
                    print("无法找到发送验证码按钮")

        # 使用信号机制获取验证码
        verification_code = await self.verification_handler.get_verification_code()
        if verification_code:
            await self.page.fill("//input[@placeholder='验证码']", verification_code)

        # 点击登录按钮
        await self.page.click(".beer-login-btn")

        # 等待登录成功
        await asyncio.sleep(3)
        # 保存cookies
        await self._save_cookies()

    async def post_article(self, title, content, images=None):
        """发布文章
        Args:
            title: 文章标题
            content: 文章内容
            images: 图片路径列表
        """
        await self.ensure_browser()  # 确保浏览器已初始化
        print("点击发布按钮")
        # 点击发布按钮
        await self.page.click(".btn.el-tooltip__trigger.el-tooltip__trigger")

        # 切换到上传图文
        await asyncio.sleep(1)
        tabs = await self.page.query_selector_all(".creator-tab")
        if len(tabs) > 1:
            await tabs[1].click()
        await asyncio.sleep(1)

        # 上传图片
        if images:
            async with self.page.expect_file_chooser() as fc_info:
                await self.page.click(".upload-input")
            file_chooser = await fc_info.value
            await file_chooser.set_files(images)
            await asyncio.sleep(1)

        await asyncio.sleep(3)
        # 输入标题
        await self.page.fill(".d-text", title)

        # 输入内容
        print(content)
        await self.page.fill(".ql-editor", content)

        # 发布
        await asyncio.sleep(1)
        # await self.page.click(".el-button.publishBtn")

    async def post_video(self, title, content, video_path=None):
        """发布视频
        Args:
            title: 视频标题
            content: 视频描述
            video_path: 视频文件路径
        """
        # 检查视频文件格式
        if video_path:
            allowed_formats = [".mp4", ".mov", ".avi"]
            if not any(video_path.lower().endswith(fmt) for fmt in allowed_formats):
                raise ValueError(f"不支持的视频格式。支持的格式：{', '.join(allowed_formats)}")
            
            # 检查文件是否存在
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"视频文件不存在：{video_path}")
        
        await self.ensure_browser()  # 确保浏览器已初始化
        print("点击发布按钮")
        try:
            # 点击发布按钮
            await self.page.click(".btn.el-tooltip__trigger.el-tooltip__trigger")

            # 切换到上传视频
            await asyncio.sleep(1)
            tabs = await self.page.query_selector_all(".creator-tab")
            if len(tabs) > 2:  # 确保有视频上传选项
                await tabs[2].click()
            else:
                raise Exception("找不到视频上传选项")
            await asyncio.sleep(1)

            # 上传视频
            if video_path:
                async with self.page.expect_file_chooser() as fc_info:
                    await self.page.click(".upload-input")
                file_chooser = await fc_info.value
                await file_chooser.set_files(video_path)
                print("开始上传视频...")
                await asyncio.sleep(3)  # 等待视频上传开始
                
                # 等待上传完成（可以根据实际情况调整等待时间或添加上传进度检测）
                await self.page.wait_for_selector(".upload-success", timeout=300000)  # 5分钟超时
                print("视频上传完成")

            # 输入标题
            await self.page.fill(".d-text", title)

            # 输入描述
            await self.page.fill(".ql-editor", content)

            # 发布
            await asyncio.sleep(1)
            # await self.page.click(".el-button.publishBtn")
            
        except Exception as e:
            logging.error(f"发布视频时出错: {str(e)}")
            raise Exception(f"发布视频失败: {str(e)}")

    async def close(self, force=False):
        """关闭浏览器
        Args:
            force: 是否强制关闭浏览器，默认为False
        """
        try:
            if force:
                if self.context:
                    await self.context.close()
                if self.browser:
                    await self.browser.close()
                if self.playwright:
                    await self.playwright.stop()
                self.playwright = None
                self.browser = None
                self.context = None
                self.page = None
        except Exception as e:
            logging.debug(f"关闭浏览器时出错: {str(e)}")

    async def ensure_browser(self):
        """确保浏览器已初始化"""
        if not self.playwright:
            await self.initialize()


class VideoPreviewWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(5)
        
        # 创建预览图片标签
        self.preview_label = QLabel()
        self.preview_label.setMinimumHeight(300)
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet("background-color: #f0f0f0; border-radius: 4px;")
        
        # 添加文件选择按钮
        self.file_controls = QHBoxLayout()
        self.file_controls.setContentsMargins(10, 5, 10, 5)
        self.select_button = QPushButton("选择视频")
        
        # 设置按钮样式
        button_style = """
            QPushButton {
                background-color: #ff2442;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #ff4d66;
            }
            QPushButton:pressed {
                background-color: #e61e3a;
            }
        """
        self.select_button.setStyleSheet(button_style)
        self.select_button.clicked.connect(self.select_video)
        
        self.file_controls.addWidget(self.select_button)
        self.file_controls.addStretch()
        
        # 添加预览控制按钮
        self.preview_controls = QHBoxLayout()
        self.preview_controls.setContentsMargins(10, 5, 10, 5)
        self.preview_button = QPushButton("预览")
        self.preview_button.setStyleSheet(button_style)
        self.preview_button.clicked.connect(self.play_video)
        
        self.preview_controls.addWidget(self.preview_button)
        self.preview_controls.addStretch()
        
        self.layout.addWidget(self.preview_label)
        self.layout.addLayout(self.file_controls)
        self.layout.addLayout(self.preview_controls)
        
        self.video_path = None
    
    def select_video(self):
        # 打开文件选择对话框
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("视频文件 (*.mp4 *.mov *.avi)")
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                video_path = selected_files[0]
                # 验证文件格式
                allowed_formats = [".mp4", ".mov", ".avi"]
                if any(video_path.lower().endswith(fmt) for fmt in allowed_formats):
                    self.set_video(video_path)
                else:
                    TipWindow.info("不支持的视频格式，请选择 MP4、MOV 或 AVI 格式的视频文件。")

    def set_video(self, video_path):
        self.video_path = video_path
        # 显示视频文件名
        self.preview_label.setText("视频已选择：" + os.path.basename(video_path))
        # 启用预览按钮
        self.preview_button.setEnabled(True)
    
    def play_video(self):
        # 使用系统默认播放器打开视频
        if self.video_path and os.path.exists(self.video_path):
            if sys.platform == "darwin":  # macOS
                os.system(f"open {self.video_path}")
            elif sys.platform == "win32":  # Windows
                os.system(f"start {self.video_path}")
    
    def stop_video(self):
        pass  # 不需要实现停止功能
