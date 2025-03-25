"""
注意：此模組目前未被使用。系統已改為使用電子郵件驗證。
此文件僅保留作為將來可能重新啟用手機驗證功能的參考。
"""

from flask import current_app
import requests
import logging
import sys
import os
import base64
import uuid

# 設置日誌記錄
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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
        template_id = current_app.config.get('ENGAGELAB_TEMPLATE_ID')
        
        # 檢查是否設置了 Engagelab 配置
        if not all([sms_user, sms_key]):
            error_msg = 'Engagelab 配置不完整，請確認以下設定：\n'
            error_msg += f'ENGAGELAB_USER: {"已設定" if sms_user else "未設定"}\n'
            error_msg += f'ENGAGELAB_KEY: {"已設定" if sms_key else "未設定"}'
            logger.error(error_msg)
            return False
            
        if not template_id:
            logger.warning('未設定 ENGAGELAB_TEMPLATE_ID，將使用預設文字內容發送')
        
        # 將台灣手機號碼轉換為國際格式（例如：+886987654321）
        if phone_number.startswith('0'):
            international_phone = '+886' + phone_number[1:]
        else:
            international_phone = phone_number
            
        # 準備請求資料 - 根據 EngageLab API 的要求調整格式
        url = "https://sms.api.engagelab.cc/v1/send"
        
        # 生成唯一的請求 ID
        request_id = str(uuid.uuid4())[:8]
        
        # 根據是否有模板 ID 來構建請求內容
        if template_id:
            # 使用模板 ID 發送
            request_body = {
                "from": "噶陀十方尊勝佛學會",  # 發送者名稱
                "to": [international_phone],
                "request_id": request_id,
                "body": {
                    "template_id": int(template_id),
                    "vars": {
                        "code": code
                    }
                }
            }
        else:
            # 使用純文字發送
            request_body = {
                "from": "噶陀十方尊勝佛學會",  # 發送者名稱
                "to": [international_phone],
                "request_id": request_id,
                "body": {
                    "content": f"【噶陀十方尊勝佛學會】您的驗證碼是：{code}，10分鐘內有效，請勿洩露給他人，祝您修行順利，吉祥如意。"
                }
            }
        
        logger.info(f'準備發送簡訊到 {international_phone}')
        
        # 生成 Basic Auth 認證標頭
        credentials = f"{sms_user}:{sms_key}"
        encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
        
        # 設置請求標頭
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Basic {encoded_credentials}'
        }
        
        # 檢查環境變數中的代理設置
        http_proxy = os.environ.get('HTTP_PROXY', '')
        https_proxy = os.environ.get('HTTPS_PROXY', '')
        no_proxy = os.environ.get('NO_PROXY', '')
        
        logger.debug(f'HTTP_PROXY: {http_proxy}')
        logger.debug(f'HTTPS_PROXY: {https_proxy}')
        logger.debug(f'NO_PROXY: {no_proxy}')
        
        # 明確設置不使用代理
        proxies = None
        logger.debug('不使用代理連接 EngageLab API')
        
        # 發送請求
        try:
            logger.debug(f'發送請求到 {url}')
            logger.debug(f'請求內容: {request_body}')
            
            response = requests.post(
                url, 
                json=request_body, 
                headers=headers,
                proxies=proxies,
                timeout=10,  # 設置超時時間
                verify=True  # 驗證 SSL 證書
            )
            
            # 記錄請求詳情
            logger.debug(f'請求 URL: {url}')
            logger.debug(f'請求標頭: {headers}')
            logger.debug(f'回應狀態碼: {response.status_code}')
            logger.debug(f'回應標頭: {response.headers}')
            logger.debug(f'回應內容: {response.text}')
            
            # 檢查回應
            if response.status_code >= 400:
                logger.error(f'簡訊發送失敗，狀態碼: {response.status_code}, 回應: {response.text}')
                return False
                
            # 嘗試解析 JSON 回應
            try:
                response_data = response.json()
                logger.debug(f'回應 JSON 資料: {response_data}')
            except ValueError:
                logger.warning('回應不是有效的 JSON 格式')
            
            # 根據回應判斷是否發送成功
            if response.status_code == 200 or response.status_code == 201 or response.status_code == 202:
                logger.info(f'驗證碼已發送到 {international_phone}')
                return True
            else:
                logger.error(f'簡訊發送失敗: {response.text}')
                return False
                
        except requests.exceptions.SSLError as e:
            logger.error(f'SSL 證書驗證失敗: {str(e)}')
            return False
        except requests.exceptions.ConnectionError as e:
            logger.error(f'連接錯誤: {str(e)}')
            return False
        except requests.exceptions.Timeout as e:
            logger.error(f'請求超時: {str(e)}')
            return False
    
    except Exception as e:
        logger.error(f'發送驗證碼時發生未知錯誤: {str(e)}', exc_info=True)
        return False
