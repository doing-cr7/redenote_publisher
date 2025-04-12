from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                           QFileDialog, QProgressBar, QLineEdit, QTextEdit, QFrame,
                           QScrollArea)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap
import cv2
import os
import requests
import json
from src.config.config import Config  # 添加配置导入
from src.core.alert import TipWindow  # 添加这行导入

class VideoPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent  # 保存父窗口引用
        self.config = Config()  # 初始化配置
        self.init_video()
        self.init_ui()
        self.load_default_author()  # 加载默认作者

    def load_default_author(self):
        """加载默认作者"""
        try:
            title_config = self.config.get_title_config()
            default_author = title_config.get('author', '')
            if default_author:
                self.author_input.setText(default_author)
        except Exception as e:
            print(f"加载默认作者失败: {str(e)}")

    def update_author_config(self, author):
        """更新作者配置"""
        try:
            self.config.update_author_config(author)
        except Exception as e:
            print(f"更新作者配置失败: {str(e)}")

    def init_video(self):
        # 初始化视频相关变量
        self.video_capture = None
        self.is_playing = False
        self.current_frame = None
        
        # 创建定时器用于更新视频帧
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.setInterval(30)  # 约30fps
        
    def init_ui(self):
        main_layout = QHBoxLayout()
        
        # 左侧输入区域
        left_panel = QFrame()
        left_panel.setObjectName("leftPanel")
        left_layout = QVBoxLayout(left_panel)
        
        # 标题区域
        title_frame = QFrame()
        title_layout = QVBoxLayout(title_frame)
        
        # 眉题输入
        subtitle_label = QLabel("眉题:")
        self.subtitle_input = QLineEdit()
        self.subtitle_input.setPlaceholderText("请输入眉题")
        
        # 作者输入
        author_label = QLabel("作者:")
        self.author_input = QLineEdit()
        self.author_input.setPlaceholderText("请输入作者")
        
        # 标题输入
        title_label = QLabel("标题:")
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("请输入标题")
        
        title_layout.addWidget(subtitle_label)
        title_layout.addWidget(self.subtitle_input)
        title_layout.addWidget(author_label)
        title_layout.addWidget(self.author_input)
        title_layout.addWidget(title_label)
        title_layout.addWidget(self.title_input)
        
        # 内容输入区域
        content_label = QLabel("内容:")
        self.content_input = QTextEdit()
        self.content_input.setPlaceholderText("请输入内容")
        
        # 生成内容按钮
        self.generate_btn = QPushButton("生成内容")
        self.generate_btn.clicked.connect(self.generate_content)
        
        left_layout.addWidget(title_frame)
        left_layout.addWidget(content_label)
        left_layout.addWidget(self.content_input)
        left_layout.addWidget(self.generate_btn)
        
        # 右侧视频预览区域
        right_panel = QFrame()
        right_panel.setObjectName("rightPanel")
        right_layout = QVBoxLayout(right_panel)
        
        # 视频预览标题
        preview_title = QLabel("视频预览")
        preview_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px 0;")
        
        # 选择视频按钮
        self.select_btn = QPushButton("选择视频文件")
        self.select_btn.clicked.connect(self.select_video)
        
        # 视频信息显示
        self.info_label = QLabel("未选择视频")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 修改视频预览区域
        video_container = QFrame()
        video_layout = QVBoxLayout(video_container)
        
        # 视频显示标签
        self.video_label = QLabel()
        self.video_label.setMinimumHeight(300)
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                border: 2px dashed #cccccc;
                border-radius: 8px;
            }
        """)
        
        # 播放控制按钮
        self.play_btn = QPushButton("▶️ 播放")
        self.play_btn.setEnabled(False)
        self.play_btn.clicked.connect(self.toggle_play)
        
        # 上传进度条
        self.progress = QProgressBar()
        self.progress.hide()
        
        # 发布按钮
        self.publish_btn = QPushButton("发布视频")
        self.publish_btn.setEnabled(False)
        self.publish_btn.clicked.connect(self.publish_video)
        
        video_layout.addWidget(self.video_label)
        video_layout.addWidget(self.play_btn)
        
        right_layout.addWidget(preview_title)
        right_layout.addWidget(self.select_btn)
        right_layout.addWidget(self.info_label)
        right_layout.addWidget(video_container)
        right_layout.addWidget(self.progress)
        right_layout.addWidget(self.publish_btn)
        
        # 设置左右面板的宽度比例
        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 1)
        
        self.setLayout(main_layout)
        
        # 设置样式
        self.setStyleSheet("""
            QFrame#leftPanel, QFrame#rightPanel {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 20px;
            }
            QLabel {
                font-size: 14px;
                margin-top: 10px;
                color: #2c3e50;
            }
            QLineEdit, QTextEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                color: #2c3e50;
            }
            QLineEdit::placeholder, QTextEdit::placeholder {
                color: #95a5a6;
            }
            QPushButton {
                padding: 8px 16px;
                margin-top: 10px;
                color: white;
            }
        """)

    def select_video(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "选择视频文件",
            "",
            "Video Files (*.mp4 *.avi *.mov *.wmv)"
        )
        
        if file_name and os.path.exists(file_name):
            # 关闭之前的视频
            if self.video_capture is not None:
                self.stop_video()
            
            # 打开新视频
            self.video_capture = cv2.VideoCapture(file_name)
            if self.video_capture.isOpened():
                self.video_path = file_name
                self.info_label.setText(f"已选择: {os.path.basename(file_name)}")
                
                # 读取第一帧
                ret, frame = self.video_capture.read()
                if ret:
                    self.show_frame(frame)
                    self.play_btn.setEnabled(True)
                    self.publish_btn.setEnabled(True)
                    
                    # 重置播放状态
                    self.is_playing = False
                    self.play_btn.setText("▶️ 播放")
            else:
                self.info_label.setText("无法打开视频文件")

    def toggle_play(self):
        if not self.is_playing:
            if self.video_capture is not None:
                self.timer.start()
                self.play_btn.setText("⏸️ 暂停")
                self.is_playing = True
        else:
            self.timer.stop()
            self.play_btn.setText("▶️ 播放")
            self.is_playing = False

    def update_frame(self):
        if self.video_capture is not None:
            ret, frame = self.video_capture.read()
            if ret:
                self.show_frame(frame)
            else:
                # 视频播放完毕，重新开始
                self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                self.toggle_play()

    def show_frame(self, frame):
        # 调整帧大小以适应显示区域
        height, width = frame.shape[:2]
        label_size = self.video_label.size()
        
        # 计算缩放比例
        w_ratio = label_size.width() / width
        h_ratio = label_size.height() / height
        ratio = min(w_ratio, h_ratio)
        
        new_width = int(width * ratio)
        new_height = int(height * ratio)
        
        # 缩放帧
        frame = cv2.resize(frame, (new_width, new_height))
        
        # 转换颜色空间从BGR到RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # 转换为QImage
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        image = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        
        # 显示图像
        self.video_label.setPixmap(QPixmap.fromImage(image))

    def stop_video(self):
        self.timer.stop()
        if self.video_capture is not None:
            self.video_capture.release()
            self.video_capture = None
        self.is_playing = False
        self.play_btn.setText("▶️ 播放")
        self.play_btn.setEnabled(False)
        self.video_label.clear()
        self.video_label.setText("未选择视频")

    def closeEvent(self, event):
        self.stop_video()
        super().closeEvent(event)

    def publish_video(self):
        # 这里实现视频发布逻辑
        self.progress.show()
        # TODO: 实现视频上传和发布功能
        pass
        
    def generate_content(self):
        try:
            # 只获取内容输入
            content = self.content_input.toPlainText().strip()
            
            # 检查内容是否为空
            if not content:
                TipWindow(self.parent, "❌ 请输入内容关键词").show()
                return
                
            # 禁用生成按钮
            self.generate_btn.setEnabled(False)
            self.generate_btn.setText("生成中...")
            
            # 构建提示词
            prompt = f"""
            你现在是一个专业的小红书视频文案写手。请根据以下关键词生成一个视频文案，包括标题和正文。

            关键词: {content}

            要求：
            1. 以 JSON 格式返回，包含两个字段：title（标题）和 content（正文）
            2. 标题要简短有力，最好带emoji，能吸引用户点击
            3. 正文要活泼生动，适合视频内容展示
            4. 增加3-5个相关的话题标签
            5. 适当使用emoji增加活力
            6. 确保整体风格符合小红书调性

            请直接返回 JSON 格式的内容，不要有其他额外的文字。
            """
            
            # 调用本地 Ollama API
            url = "http://127.0.0.1:11434/api/generate"
            payload = {
                "model": "qwen2.5:14b",  # 更新为正确的模型名称
                "prompt": prompt,
                "stream": False
            }
            
            try:
                response = requests.post(url, json=payload, timeout=60)  # 增加超时时间
                response.raise_for_status()
            except requests.RequestException as e:
                if "Connection refused" in str(e):
                    TipWindow(self.parent, "❌ 无法连接到 Ollama 服务，请确保服务已启动").show()
                elif "404" in str(e):
                    TipWindow(self.parent, "❌ API 地址错误，请检查 Ollama 服务配置").show()
                else:
                    TipWindow(self.parent, f"❌ API 请求失败: {str(e)}").show()
                raise
            
            # 解析返回的内容
            response_text = response.json().get('response', '')
            try:
                # 尝试解析JSON
                # 清理可能的多余字符
                response_text = response_text.strip()
                if response_text.startswith('```json'):
                    response_text = response_text[7:]
                if response_text.endswith('```'):
                    response_text = response_text[:-3]
                    
                generated_data = json.loads(response_text)
                generated_title = generated_data.get('title', '')
                generated_content = generated_data.get('content', '')
                
                if not generated_title or not generated_content:
                    raise ValueError("生成的内容格式不正确")
                    
            except (json.JSONDecodeError, ValueError) as e:
                # 如果不是JSON格式，尝试智能分割文本
                lines = response_text.split('\n')
                generated_title = ""
                generated_content = []
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    if not generated_title:
                        generated_title = line
                    else:
                        generated_content.append(line)
                
                generated_content = '\n'.join(generated_content) if generated_content else response_text
                if not generated_title:
                    generated_title = "视频分享"
            
            # 更新界面
            self.title_input.setText(generated_title)
            self.content_input.setPlainText(generated_content)
            
            # 保存当前作者名称
            current_author = self.author_input.text().strip()
            if current_author:
                self.update_author_config(current_author)
            
            TipWindow(self.parent, "✅ 内容生成成功").show()
            
        except Exception as e:
            TipWindow(self.parent, f"❌ 生成失败: {str(e)}").show()
            print(f"生成内容失败: {str(e)}")
        finally:
            # 恢复按钮状态
            self.generate_btn.setEnabled(True)
            self.generate_btn.setText("生成内容") 