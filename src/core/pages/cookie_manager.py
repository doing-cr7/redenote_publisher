from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QListWidget, QListWidgetItem, 
                           QDialog, QLineEdit, QMessageBox, QFrame,
                           QTextEdit)
from PyQt6.QtCore import Qt
import configparser
import os
from src.config.config import Config

class CookieManagerPage(QWidget):
    """Cookie管理页面"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = Config()
        self.init_ui()
        self.load_cookies()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 标题
        title = QLabel("Cookie 管理")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px 0;")
        layout.addWidget(title)

        # Cookie列表区域
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
        
        # Cookie列表
        self.cookie_list = QListWidget()
        self.cookie_list.setStyleSheet("""
            QListWidget {
                border: none;
                background-color: white;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
        """)
        list_layout.addWidget(self.cookie_list)

        # 按钮区域
        btn_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("➕ 添加账号")
        self.edit_btn = QPushButton("✏️ 编辑")
        self.delete_btn = QPushButton("🗑️ 删除")
        self.verify_btn = QPushButton("✅ 验证")
        
        for btn in [self.add_btn, self.edit_btn, self.delete_btn, self.verify_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    padding: 8px 16px;
                    background-color: #2c3e50;
                    color: white;
                    border: none;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #34495e;
                }
                QPushButton:disabled {
                    background-color: #95a5a6;
                }
            """)
            btn_layout.addWidget(btn)

        list_layout.addLayout(btn_layout)
        layout.addWidget(list_frame)

        # 状态显示
        self.status_label = QLabel()
        self.status_label.setStyleSheet("""
            QLabel {
                color: #666;
                padding: 10px;
            }
        """)
        layout.addWidget(self.status_label)

        # 连接信号
        self.add_btn.clicked.connect(self.add_cookie)
        self.edit_btn.clicked.connect(self.edit_cookie)
        self.delete_btn.clicked.connect(self.delete_cookie)
        self.verify_btn.clicked.connect(self.verify_cookie)
        
        # 初始化按钮状态
        self.update_button_states()
        
    def load_cookies(self):
        """加载所有Cookie"""
        try:
            accounts = self.config.get_all_accounts()
            self.cookie_list.clear()
            for account in accounts:
                item = QListWidgetItem(f"账号 {account}")
                self.cookie_list.addItem(item)
            self.update_button_states()
        except Exception as e:
            self.status_label.setText(f"加载Cookie失败: {str(e)}")

    def update_button_states(self):
        """更新按钮状态"""
        has_selection = bool(self.cookie_list.currentItem())
        self.edit_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)
        self.verify_btn.setEnabled(has_selection)

    def add_cookie(self):
        """添加新Cookie"""
        dialog = CookieDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                # 保存新Cookie
                account_name = dialog.name_input.text()
                cookie_value = dialog.cookie_input.toPlainText()
                self.config.add_account(account_name, cookie_value)
                
                # 更新列表
                self.load_cookies()
                self.status_label.setText("添加Cookie成功")
            except Exception as e:
                QMessageBox.warning(self, "错误", f"添加Cookie失败: {str(e)}")

    def edit_cookie(self):
        """编辑Cookie"""
        current_item = self.cookie_list.currentItem()
        if not current_item:
            return
            
        account_name = current_item.text().replace("账号 ", "")
        current_cookie = self.config.get_account_cookie(account_name)
        
        dialog = CookieDialog(self, account_name, current_cookie)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                # 更新Cookie
                new_cookie = dialog.cookie_input.toPlainText()
                self.config.update_account_cookie(account_name, new_cookie)
                
                # 更新列表
                self.load_cookies()
                self.status_label.setText("更新Cookie成功")
            except Exception as e:
                QMessageBox.warning(self, "错误", f"更新Cookie失败: {str(e)}")

    def delete_cookie(self):
        """删除Cookie"""
        current_item = self.cookie_list.currentItem()
        if not current_item:
            return
            
        account_name = current_item.text().replace("账号 ", "")
        reply = QMessageBox.question(self, "确认删除", 
                                   f"确定要删除账号 {account_name} 的Cookie吗？",
                                   QMessageBox.StandardButton.Yes | 
                                   QMessageBox.StandardButton.No)
                                   
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.config.delete_account(account_name)
                self.load_cookies()
                self.status_label.setText("删除Cookie成功")
            except Exception as e:
                QMessageBox.warning(self, "错误", f"删除Cookie失败: {str(e)}")

    def verify_cookie(self):
        """验证Cookie"""
        current_item = self.cookie_list.currentItem()
        if not current_item:
            return
            
        account_name = current_item.text().replace("账号 ", "")
        cookie = self.config.get_account_cookie(account_name)
        
        try:
            # TODO: 实现Cookie验证逻辑
            is_valid = True  # 这里需要实际的验证逻辑
            
            if is_valid:
                self.status_label.setText(f"账号 {account_name} 的Cookie有效")
            else:
                self.status_label.setText(f"账号 {account_name} 的Cookie已失效")
        except Exception as e:
            self.status_label.setText(f"验证Cookie失败: {str(e)}")

class CookieDialog(QDialog):
    """Cookie编辑对话框"""
    def __init__(self, parent=None, account_name="", cookie=""):
        super().__init__(parent)
        self.setWindowTitle("编辑Cookie" if account_name else "添加Cookie")
        self.init_ui(account_name, cookie)
        
    def init_ui(self, account_name, cookie):
        layout = QVBoxLayout(self)
        
        # 账号名称输入
        name_layout = QHBoxLayout()
        name_label = QLabel("账号名称:")
        self.name_input = QLineEdit(account_name)
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)
        
        # Cookie输入
        cookie_label = QLabel("Cookie值:")
        self.cookie_input = QTextEdit()
        self.cookie_input.setPlainText(cookie)
        layout.addWidget(cookie_label)
        layout.addWidget(self.cookie_input)
        
        # 按钮
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("保存")
        cancel_btn = QPushButton("取消")
        
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout) 