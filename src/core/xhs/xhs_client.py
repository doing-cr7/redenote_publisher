try:
    from xhs import XhsClient as BaseXhsClient
except ImportError:
    print("请先安装 xhs-sdk: pip install xhs-sdk")
    BaseXhsClient = None

from playwright.sync_api import sync_playwright
import pathlib
import time

class XhsClient(BaseXhsClient):
    """小红书客户端"""
    def __init__(self, cookies=None, sign=None, timeout=60):
        super().__init__(cookies, sign, timeout)

    def get_formatted_cookies(self):
        """获取格式化的cookie字符串"""
        try:
            # 从客户端获取cookie
            cookies = self.get_cookies()
            
            # 格式化cookie字符串
            cookie_str = ';'.join([
                f"{cookie['name']}={cookie['value']}"
                for cookie in cookies
                if cookie.get('domain', '').endswith('.xiaohongshu.com')
            ])
            
            return cookie_str
        except Exception as e:
            print(f"获取cookie失败: {str(e)}")
            return None

    def login_by_phone(self, phone, code):
        """使用手机号登录"""
        try:
            # 实现手机号登录逻辑
            # TODO: 实现具体的登录逻辑
            return {'success': True}
        except Exception as e:
            print(f"手机号登录失败: {str(e)}")
            return {'success': False, 'error': str(e)}

    def get_cookies(self):
        """获取所有cookie"""
        try:
            # 从基类获取cookie
            return super().get_cookies()
        except Exception as e:
            print(f"获取cookies失败: {str(e)}")
            return []

    def verify_cookie(self):
        """验证cookie是否有效"""
        try:
            # 尝试调用一个需要登录的API来验证cookie
            self.get_video_first_frame_image_id("test")
            return True
        except:
            return False 