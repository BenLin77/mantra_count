"""
注意：此模組目前未被使用。系統已改為使用電子郵件驗證。
此文件僅保留作為將來可能重新啟用手機驗證功能的參考。
"""

from flask import current_app
import requests
from requests.auth import HTTPBasicAuth
import logging
import sys
import os

def send_verification_code(phone_number, code):
    """
    使用 Engagelab 發送驗證碼簡訊
    
    Args:
        phone_number (str): 接收者的手機號碼（格式：09xxxxxxxx）
        code (str): 6位數的驗證碼
    
    Returns:
        bool: 發送成功返回 True，否則返回 False
    """
    try:
        # 獲取 Engagelab 配置
        sms_user = current_app.config['ENGAGELAB_USER']
        sms_key = current_app.config['ENGAGELAB_KEY']
        
        # 檢查是否設置了 Engagelab 配置
        if not all([sms_user, sms_key]):
            error_msg = 'Engagelab 配置不完整，請確認以下設定：\n'
            error_msg += f'ENGAGELAB_USER: {"已設定" if sms_user else "未設定"}\n'
            error_msg += f'ENGAGELAB_KEY: {"已設定" if sms_key else "未設定"}'
            print(error_msg, file=sys.stderr)
            logging.error(error_msg)
            return False
        
        # 將台灣手機號碼轉換為國際格式（例如：+886987654321）
        if phone_number.startswith('0'):
            international_phone = '+886' + phone_number[1:]
        else:
            international_phone = phone_number
            
        # 準備請求資料
        url = "https://sms.api.engagelab.cc/v1/send"
        request_body = {
            "from": "噶陀十方尊勝佛學會",  # 發送者名稱
            "to": [international_phone],
            "text": f"【噶陀十方尊勝佛學會】您的驗證碼是：{code}，10分鐘內有效，請勿洩露給他人，祝您修行順利，吉祥如意。"
        }
        
        print(f'準備發送簡訊到 {international_phone}，內容：{request_body["text"]}', file=sys.stderr)
        
        # 設置請求標頭
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # 設置代理（如果需要）
        proxies = None
        if os.environ.get('HTTP_PROXY'):
            proxies = {
                'http': os.environ.get('HTTP_PROXY'),
                'https': os.environ.get('HTTPS_PROXY', os.environ.get('HTTP_PROXY'))
            }
        
        # 發送請求
        response = requests.post(
            url, 
            json=request_body, 
            auth=HTTPBasicAuth(sms_user, sms_key),
            headers=headers,
            proxies=proxies,
            timeout=10  # 設置超時時間
        )
        
        # 檢查回應
        response.raise_for_status()
        response_data = response.json()
        
        # 記錄回應
        print(f'簡訊 API 回應: {response.text}', file=sys.stderr)
        
        # 根據回應判斷是否發送成功
        if response.status_code == 200:
            logging.info(f'驗證碼已發送到 {international_phone}')
            return True
        else:
            logging.error(f'簡訊發送失敗: {response.text}')
            return False
            
    except requests.exceptions.RequestException as e:
        error_msg = f'發送驗證碼失敗: {str(e)}'
        print(error_msg, file=sys.stderr)
        logging.error(error_msg)
        return False
    except Exception as e:
        error_msg = f'發送驗證碼時發生未知錯誤: {str(e)}'
        print(error_msg, file=sys.stderr)
        logging.error(error_msg)
        return False
