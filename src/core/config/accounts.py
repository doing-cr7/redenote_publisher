import configparser
from pathlib import Path
import os

def validate_cookie_format(cookie):
    """验证cookie格式"""
    try:
        # 检查必要的cookie字段
        required_fields = ['a1', 'web_session', 'xsecappid']
        cookie_dict = dict(item.split('=', 1) for item in cookie.split(';'))
        
        # 验证必要字段是否存在
        for field in required_fields:
            if field not in cookie_dict:
                return False
                
        return True
    except:
        return False

class AccountManager:
    def __init__(self):
        self.config = configparser.RawConfigParser()
        self.config_file = Path(os.path.expanduser('~/.xhsai/accounts.ini'))
        self.ensure_config_file()
        self.load_config()

    def ensure_config_file(self):
        """确保配置文件存在"""
        if not self.config_file.parent.exists():
            self.config_file.parent.mkdir(parents=True)
        if not self.config_file.exists():
            self.config_file.touch()
            self.config['account1'] = {'cookies': ''}
            self.save_config()

    def load_config(self):
        """加载配置"""
        self.config.read(self.config_file)

    def save_config(self):
        """保存配置"""
        with open(self.config_file, 'w') as f:
            self.config.write(f)

    def get_account_cookies(self, account_name='account1'):
        """获取账号cookie"""
        try:
            return self.config[account_name]['cookies']
        except:
            return None

    def set_account_cookies(self, cookie, account_name):
        """设置账号cookie"""
        if not validate_cookie_format(cookie):
            raise ValueError("Cookie格式不正确")
            
        if account_name not in self.config:
            self.config[account_name] = {}
        self.config[account_name]['cookies'] = cookie
        self.save_config()

    def get_all_accounts(self):
        """获取所有账号"""
        return list(self.config.sections())

    def delete_account(self, account_name):
        """删除账号"""
        self.config.remove_section(account_name)
        self.save_config()

    def get_latest_account(self):
        """获取最新添加的账号"""
        try:
            # 直接从配置文件中获取所有 section
            accounts = self.config.sections()
            # 过滤出账号 section
            accounts = [acc for acc in accounts if acc.startswith(('account_', 'phone_'))]
            if accounts:
                # 按时间戳排序
                return max(accounts, key=lambda x: x.split('_')[1] if '_' in x else '')
        except Exception as e:
            print(f"获取最新账号失败: {str(e)}")
        return None 