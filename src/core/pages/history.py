from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QTableWidget, QTableWidgetItem,
                           QLineEdit, QComboBox, QFrame, QHeaderView)
from PyQt6.QtCore import Qt
import json
import os
from datetime import datetime

class HistoryPage(QWidget):
    """发布历史页面"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_history()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 标题
        title = QLabel("发布历史")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px 0;")
        layout.addWidget(title)

        # 搜索和筛选区域
        filter_frame = QFrame()
        filter_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        filter_layout = QHBoxLayout(filter_frame)
        
        # 搜索框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索标题...")
        self.search_input.textChanged.connect(self.filter_history)
        
        # 状态筛选
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["全部", "发布成功", "发布失败", "待发布"])
        self.filter_combo.currentTextChanged.connect(self.filter_history)
        
        filter_layout.addWidget(QLabel("搜索:"))
        filter_layout.addWidget(self.search_input)
        filter_layout.addWidget(QLabel("状态:"))
        filter_layout.addWidget(self.filter_combo)
        filter_layout.addStretch()
        
        layout.addWidget(filter_frame)

        # 历史记录表格
        table_frame = QFrame()
        table_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        table_layout = QVBoxLayout(table_frame)
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels(["时间", "标题", "状态", "备注", "操作"])
        
        # 设置表格样式
        self.history_table.setStyleSheet("""
            QTableWidget {
                border: none;
                background-color: white;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 8px;
                border: none;
                border-bottom: 1px solid #ddd;
            }
        """)
        
        # 调整列宽
        header = self.history_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        
        table_layout.addWidget(self.history_table)
        layout.addWidget(table_frame)

    def load_history(self):
        """加载发布历史"""
        try:
            # TODO: 从文件或数据库加载历史记录
            # 这里使用示例数据
            history_data = [
                {
                    "time": "2024-03-20 14:30:00",
                    "title": "测试视频1",
                    "status": "发布成功",
                    "note": "正常发布"
                },
                {
                    "time": "2024-03-20 15:00:00",
                    "title": "测试视频2",
                    "status": "发布失败",
                    "note": "Cookie已失效"
                }
            ]
            
            self.update_table(history_data)
        except Exception as e:
            print(f"加载历史记录失败: {str(e)}")

    def update_table(self, data):
        """更新表格数据"""
        self.history_table.setRowCount(len(data))
        
        for row, item in enumerate(data):
            # 时间
            time_item = QTableWidgetItem(item["time"])
            self.history_table.setItem(row, 0, time_item)
            
            # 标题
            title_item = QTableWidgetItem(item["title"])
            self.history_table.setItem(row, 1, title_item)
            
            # 状态
            status_item = QTableWidgetItem(item["status"])
            status_item.setForeground(
                Qt.GlobalColor.green if item["status"] == "发布成功" 
                else Qt.GlobalColor.red
            )
            self.history_table.setItem(row, 2, status_item)
            
            # 备注
            note_item = QTableWidgetItem(item["note"])
            self.history_table.setItem(row, 3, note_item)
            
            # 操作按钮
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            
            retry_btn = QPushButton("重试")
            delete_btn = QPushButton("删除")
            
            retry_btn.clicked.connect(lambda: self.retry_publish(row))
            delete_btn.clicked.connect(lambda: self.delete_history(row))
            
            btn_layout.addWidget(retry_btn)
            btn_layout.addWidget(delete_btn)
            
            self.history_table.setCellWidget(row, 4, btn_widget)

    def filter_history(self):
        """筛选历史记录"""
        search_text = self.search_input.text().lower()
        status_filter = self.filter_combo.currentText()
        
        for row in range(self.history_table.rowCount()):
            title = self.history_table.item(row, 1).text().lower()
            status = self.history_table.item(row, 2).text()
            
            title_match = search_text in title
            status_match = status_filter == "全部" or status == status_filter
            
            self.history_table.setRowHidden(row, not (title_match and status_match))

    def retry_publish(self, row):
        """重新发布"""
        title = self.history_table.item(row, 1).text()
        # TODO: 实现重新发布逻辑
        print(f"重新发布: {title}")

    def delete_history(self, row):
        """删除历史记录"""
        title = self.history_table.item(row, 1).text()
        # TODO: 实现删除逻辑
        self.history_table.removeRow(row)
        print(f"删除历史记录: {title}") 