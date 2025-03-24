"""
注意：此模組目前未被使用。系統已改為使用電子郵件驗證。
此文件僅保留作為將來可能重新啟用手機驗證功能的參考。
"""

from flask import current_app
from twilio.rest import Client
import logging

def send_verification_code(phone_number, code):
    """
    使用 Twilio 發送驗證碼簡訊
    
    Args:
        phone_number (str): 接收者的手機號碼
        code (str): 6位數的驗證碼
    
    Returns:
        bool: 發送成功返回 True，否則返回 False
    """
    try:
        # 獲取 Twilio 配置
        account_sid = current_app.config['TWILIO_ACCOUNT_SID']
        auth_token = current_app.config['TWILIO_AUTH_TOKEN']
        twilio_phone = current_app.config['TWILIO_PHONE_NUMBER']
        
        # 檢查是否設置了 Twilio 配置
        if not all([account_sid, auth_token, twilio_phone]):
            # 如果沒有設置 Twilio，則只在日誌中記錄驗證碼
            logging.warning(f'Twilio 未配置，驗證碼 {code} 將發送到 {phone_number}')
            return True
        
        # 創建 Twilio 客戶端
        client = Client(account_sid, auth_token)
        
        # 發送簡訊
        message = client.messages.create(
            body=f'您的噶陀十方尊勝佛學會持咒統計驗證碼是：{code}，10分鐘內有效。',
            from_=twilio_phone,
            to=phone_number
        )
        
        logging.info(f'驗證碼已發送到 {phone_number}，SID: {message.sid}')
        return True
    
    except Exception as e:
        logging.error(f'發送驗證碼失敗: {str(e)}')
        return False
