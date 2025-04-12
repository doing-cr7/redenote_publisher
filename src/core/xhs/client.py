try:
    from src.core.xhs.xhs import XhsClient
except ImportError:
    print("请先安装 xhs-sdk: pip install xhs-sdk")
    XhsClient = None

from playwright.sync_api import sync_playwright
import pathlib
import time
from datetime import datetime

class XhsClientManager:
    def __init__(self):
        if XhsClient is None:
            raise ImportError("请先安装 xhs-sdk: pip install xhs-sdk")
        self.client = None
        
    def sign_local(self, uri, data=None, a1="", web_session=""):
        """本地签名实现"""
        for _ in range(10):
            try:
                with sync_playwright() as playwright:
                    chromium = playwright.chromium
                    browser = chromium.launch(headless=True)
                    browser_context = browser.new_context()
                    context_page = browser_context.new_page()
                    context_page.goto("https://www.xiaohongshu.com")
                    browser_context.add_cookies([
                        {'name': 'a1', 'value': a1, 'domain': ".xiaohongshu.com", 'path': "/"}
                    ])
                    context_page.reload()
                    time.sleep(2)
                    encrypt_params = context_page.evaluate(
                        "([url, data]) => window._webmsxyw(url, data)", 
                        [uri, data]
                    )
                    return {
                        "x-s": encrypt_params["X-s"],
                        "x-t": str(encrypt_params["X-t"])
                    }
            except Exception:
                continue
        raise Exception("签名失败")

    def init_client(self, cookies):
        """初始化客户端"""
        self.client = XhsClient(cookies, sign=self.sign_local, timeout=60)
        return self.client

    def verify_cookies(self):
        """验证cookies是否有效"""
        if not self.client:
            return False
        try:
            self.client.get_video_first_frame_image_id("test")
            return True
        except:
            return False

    def publish_video(self, video_path, title, desc, topics=None):
        """发布视频"""
        if not self.client:
            raise Exception("客户端未初始化")
            
        if not topics:
            topics = []
            
        return self.client.create_video_note(
            title=title[:20],
            video_path=video_path,
            desc=desc,
            topics=topics,
            is_private=False
        )

    def get_topics(self, keyword):
        """获取话题建议"""
        if not self.client:
            raise Exception("客户端未初始化")
            
        topics = self.client.get_suggest_topic(keyword)
        if topics and len(topics) > 0:
            topics[0]['type'] = 'topic'
            return topics[0]
        return None 