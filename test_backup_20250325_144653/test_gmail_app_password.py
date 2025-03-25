#!/usr/bin/env python
# -*- coding: utf-8 -*-

import smtplib
import ssl
import os
from dotenv import load_dotenv
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import logging
import socket

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 載入環境變數
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

def test_gmail_app_password():
    """測試使用 Gmail 應用程式專用密碼發送郵件"""
    # 郵件配置
    smtp_server = "smtp.gmail.com"
    port = 465  # 使用 SSL 的端口
    sender_email = os.environ.get('MAIL_USERNAME', 'bookwormkobo521@gmail.com')
    password = os.environ.get('MAIL_PASSWORD', '')  # 從環境變數獲取應用程式專用密碼
    receiver_email = "bookwormkobo521@gmail.com"  # 發送給自己測試
    
    # 打印配置信息
    logger.info(f"郵件配置信息:")
    logger.info(f"SMTP 服務器: {smtp_server}")
    logger.info(f"端口: {port}")
    logger.info(f"發件人: {sender_email}")
    logger.info(f"收件人: {receiver_email}")
    
    # 創建郵件
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = Header('噶陀十方尊勝佛學會持咒統計 - 應用程式專用密碼測試', 'utf-8')
    
    # 郵件內容
    body = f"""
    這是一封測試郵件，用於測試 Gmail 應用程式專用密碼功能。
    
    發送時間: {time.strftime('%Y-%m-%d %H:%M:%S')}
    
    如果您收到這封郵件，表示您已正確設置 Gmail 應用程式專用密碼，電子郵件發送功能正常。
    
    噶陀十方尊勝佛學會持咒統計團隊
    """
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    try:
        # 創建安全連接
        context = ssl.create_default_context()
        
        # 連接到郵件服務器
        logger.info(f"連接到 {smtp_server}:{port}...")
        server = smtplib.SMTP_SSL(smtp_server, port, context=context, timeout=30)
        
        # 登入
        logger.info(f"登入 ({sender_email})...")
        server.login(sender_email, password)
        
        # 發送郵件
        logger.info(f"發送郵件至 {receiver_email}...")
        server.sendmail(sender_email, receiver_email, msg.as_string())
        logger.info("郵件發送成功！")
        
        # 關閉連接
        server.quit()
        
        # 提示用戶檢查郵件
        logger.info("請檢查您的收件箱，郵件可能需要幾分鐘才能到達。")
        logger.info("如果您沒有收到郵件，請檢查垃圾郵件資料夾。")
        
        return True
        
    except smtplib.SMTPAuthenticationError:
        logger.error("認證失敗！請檢查您的用戶名和應用程式專用密碼。")
        logger.error("請確保您已按照 gmail_setup_guide.md 中的步驟設置應用程式專用密碼。")
        return False
    
    except socket.timeout:
        logger.error("連接超時！可能是網路問題或郵件服務器回應緩慢。")
        return False
        
    except Exception as e:
        logger.error(f"發送郵件時發生錯誤: {str(e)}")
        logger.error(f"錯誤類型: {type(e).__name__}")
        return False

if __name__ == "__main__":
    logger.info("測試 Gmail 應用程式專用密碼郵件發送功能")
    success = test_gmail_app_password()
    
    if success:
        logger.info("測試完成，郵件發送成功")
        logger.info("請等待幾分鐘，然後檢查您的郵箱")
    else:
        logger.error("測試失敗，郵件發送失敗")
