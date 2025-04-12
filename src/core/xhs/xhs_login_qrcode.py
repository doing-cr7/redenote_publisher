import time
from src.core.xhs.xhs_client import XhsClient

def get_login_qrcode():
    """获取登录二维码并处理登录"""
    xhs_client = XhsClient(sign=sign, timeout=60)
    qr_res = xhs_client.get_qrcode()
    qr_id = qr_res["qr_id"]
    qr_code = qr_res["code"]

    while True:
        check_qrcode = xhs_client.check_qrcode(qr_id, qr_code)
        if check_qrcode["code_status"] == 2:
            # 登录成功，返回cookie
            return xhs_client.cookie
        time.sleep(1) 