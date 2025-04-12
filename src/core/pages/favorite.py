from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QTreeWidget, QTreeWidgetItem,
                           QListWidget, QListWidgetItem, QTextEdit,
                           QInputDialog, QMessageBox, QFrame, QSplitter)
from PyQt6.QtCore import Qt
import json
import os

class FavoritePage(QWidget):
    """收藏文案页面"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_categories()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 标题
        title = QLabel("收藏文案")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px 0;")
        layout.addWidget(title)

        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧分类面板
        category_frame = QFrame()
        category_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        category_layout = QVBoxLayout(category_frame)
        
        category_label = QLabel("分类")
        category_label.setStyleSheet("font-weight: bold;")
        
        self.category_tree = QTreeWidget()
        self.category_tree.setHeaderHidden(True)
        self.category_tree.setStyleSheet("""
            QTreeWidget {
                border: none;
                background-color: white;
            }
            QTreeWidget::item {
                padding: 8px;
            }
            QTreeWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
        """)
        
        category_btn_layout = QHBoxLayout()
        add_category_btn = QPushButton("添加分类")
        delete_category_btn = QPushButton("删除分类")
        
        category_btn_layout.addWidget(add_category_btn)
        category_btn_layout.addWidget(delete_category_btn)
        
        category_layout.addWidget(category_label)
        category_layout.addWidget(self.category_tree)
        category_layout.addLayout(category_btn_layout)
        
        # 中间文案列表
        list_frame = QFrame()
        list_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        list_layout = QVBoxLayout(list_frame)
        
        list_label = QLabel("文案列表")
        list_label.setStyleSheet("font-weight: bold;")
        
        self.content_list = QListWidget()
        self.content_list.setStyleSheet("""
            QListWidget {
                border: none;
                background-color: white;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
        """)
        
        list_btn_layout = QHBoxLayout()
        add_content_btn = QPushButton("添加文案")
        delete_content_btn = QPushButton("删除文案")
        
        list_btn_layout.addWidget(add_content_btn)
        list_btn_layout.addWidget(delete_content_btn)
        
        list_layout.addWidget(list_label)
        list_layout.addWidget(self.content_list)
        list_layout.addLayout(list_btn_layout)
        
        # 右侧编辑区域
        editor_frame = QFrame()
        editor_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        editor_layout = QVBoxLayout(editor_frame)
        
        editor_label = QLabel("编辑文案")
        editor_label.setStyleSheet("font-weight: bold;")
        
        self.editor = QTextEdit()
        self.editor.setStyleSheet("""
            QTextEdit {
                border: none;
                background-color: white;
            }
        """)
        
        editor_btn_layout = QHBoxLayout()
        save_btn = QPushButton("保存")
        copy_btn = QPushButton("复制")
        
        editor_btn_layout.addWidget(save_btn)
        editor_btn_layout.addWidget(copy_btn)
        
        editor_layout.addWidget(editor_label)
        editor_layout.addWidget(self.editor)
        editor_layout.addLayout(editor_btn_layout)
        
        # 添加到分割器
        splitter.addWidget(category_frame)
        splitter.addWidget(list_frame)
        splitter.addWidget(editor_frame)
        
        # 设置分割器比例
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 2)
        
        layout.addWidget(splitter)
        
        # 连接信号
        add_category_btn.clicked.connect(self.add_category)
        delete_category_btn.clicked.connect(self.delete_category)
        add_content_btn.clicked.connect(self.add_content)
        delete_content_btn.clicked.connect(self.delete_content)
        save_btn.clicked.connect(self.save_content)
        copy_btn.clicked.connect(self.copy_content)
        
        self.category_tree.itemSelectionChanged.connect(self.load_contents)
        self.content_list.itemSelectionChanged.connect(self.load_editor)

    def load_categories(self):
        """加载分类"""
        try:
            # TODO: 从文件或数据库加载分类
            categories = [
                {"name": "视频文案", "items": ["开箱", "美食", "旅游"]},
                {"name": "图文文案", "items": ["测评", "种草", "日常"]}
            ]
            
            self.category_tree.clear()
            for category in categories:
                root = QTreeWidgetItem(self.category_tree, [category["name"]])
                for item in category["items"]:
                    QTreeWidgetItem(root, [item])
                
            self.category_tree.expandAll()
        except Exception as e:
            print(f"加载分类失败: {str(e)}")

    def add_category(self):
        """添加分类"""
        name, ok = QInputDialog.getText(self, "添加分类", "请输入分类名称:")
        if ok and name:
            current_item = self.category_tree.currentItem()
            if current_item and current_item.parent() is None:
                # 添加子分类
                QTreeWidgetItem(current_item, [name])
            else:
                # 添加主分类
                QTreeWidgetItem(self.category_tree, [name])

    def delete_category(self):
        """删除分类"""
        current_item = self.category_tree.currentItem()
        if current_item:
            reply = QMessageBox.question(self, "确认删除", 
                                       f"确定要删除分类 {current_item.text(0)} 吗？",
                                       QMessageBox.StandardButton.Yes | 
                                       QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                parent = current_item.parent()
                if parent:
                    parent.removeChild(current_item)
                else:
                    self.category_tree.takeTopLevelItem(
                        self.category_tree.indexOfTopLevelItem(current_item)
                    )

    def load_contents(self):
        """加载文案列表"""
        current_item = self.category_tree.currentItem()
        if current_item:
            # TODO: 根据分类加载文案列表
            self.content_list.clear()
            for i in range(5):
                QListWidgetItem(f"示例文案 {i+1}", self.content_list)

    def add_content(self):
        """添加文案"""
        current_item = self.category_tree.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请先选择一个分类")
            return
            
        title, ok = QInputDialog.getText(self, "添加文案", "请输入文案标题:")
        if ok and title:
            QListWidgetItem(title, self.content_list)

    def delete_content(self):
        """删除文案"""
        current_item = self.content_list.currentItem()
        if current_item:
            reply = QMessageBox.question(self, "确认删除", 
                                       f"确定要删除文案 {current_item.text()} 吗？",
                                       QMessageBox.StandardButton.Yes | 
                                       QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.content_list.takeItem(self.content_list.row(current_item))

    def load_editor(self):
        """加载编辑器内容"""
        current_item = self.content_list.currentItem()
        if current_item:
            # TODO: 加载实际的文案内容
            self.editor.setPlainText(f"这是 {current_item.text()} 的内容示例。")

    def save_content(self):
        """保存文案"""
        current_item = self.content_list.currentItem()
        if current_item:
            content = self.editor.toPlainText()
            # TODO: 保存文案内容
            QMessageBox.information(self, "提示", "保存成功")

    def copy_content(self):
        """复制文案"""
        content = self.editor.toPlainText()
        if content:
            clipboard = QApplication.clipboard()
            clipboard.setText(content)
            QMessageBox.information(self, "提示", "已复制到剪贴板") 