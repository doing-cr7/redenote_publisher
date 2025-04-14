import os
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# 你想访问的页面（必须登录过）
URLS_TO_VISIT = [
    "https://www.xiaohongshu.com",
    "https://creator.xiaohongshu.com",
    "https://school.xiaohongshu.com"
]

# 你关心的 Cookie 字段
TARGET_COOKIE_KEYS = [
    "a1", "abRequestId", "access-token-creator.xiaohongshu.com",
    "customer-sso-sid", "customerClientId", "galaxy_creator_session_id",
    "galaxy.creator.beaker.session.id", "gid", "loadts", "sec_poison_id", "unread",
    "web_session", "webBuild", "webId", "websectiga",
    "x-user-id-creator.xiaohongshu.com", "x-user-id-school.xiaohongshu.com",
    "xsecappid", "acw_tc"
]

# 读取 macOS 本地 Chrome 登录数据
def get_chrome_options():
    chrome_options = Options()
    user_data_dir = '"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"'
    chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
    chrome_options.add_argument("--profile-directory=Default")  # 默认 Profile
    chrome_options.add_experimental_option("detach", True)
    return chrome_options

# 获取一个 URL 下所有 cookie（保留原始 domain）
def get_cookies_from_domain(driver, url):
    print(f"\n🌐 正在访问：{url}")
    driver.get(url)
    time.sleep(2)
    cookies = driver.get_cookies()
    for c in cookies:
        print(f"✅ 获取 cookie: {c['name']} = {c['value']}")
    return cookies

# 合并所有 cookie（不同域名合并）
def extract_target_cookies(all_cookies):
    merged = {}
    for cookie in all_cookies:
        name = cookie["name"]
        domain = cookie.get("domain", "")
        value = cookie["value"]
        key = f"{name}.{domain}" if "xiaohongshu.com" in domain and ("x-user-id" in name or "access-token" in name) else name
        merged[key] = value
    return merged

# 主逻辑
def get_all_target_cookies(urls):
    chrome_options = get_chrome_options()
    driver = webdriver.Chrome(options=chrome_options)

    all_cookies_raw = []
    for url in urls:
        all_cookies_raw.extend(get_cookies_from_domain(driver, url))

    driver.quit()
    cookies_dict = extract_target_cookies(all_cookies_raw)

    # 打印缺失字段
    found_keys = set(cookies_dict.keys())
    missing = set(TARGET_COOKIE_KEYS) - found_keys
    if missing:
        print(f"\n⚠️ 缺失以下字段：{', '.join(missing)}")
    else:
        print("\n✅ 所有目标字段均已获取")

    # 打印 headers 用格式
    cookie_header_str = "; ".join([f"{k}={v}" for k, v in cookies_dict.items()])
    print("\n📦 Cookie Header:")
    print(cookie_header_str)

    # 写入 JSON 文件
    with open("all_xhs_cookies.json", "w") as f:
        json.dump(cookies_dict, f, indent=2, ensure_ascii=False)

    return cookies_dict

if __name__ == "__main__":
    get_all_target_cookies(URLS_TO_VISIT)



