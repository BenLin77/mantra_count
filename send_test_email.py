#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import logging
from dotenv import load_dotenv
from flask import Flask
from flask_mail import Mail, Message

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 載入環境變數
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

# 創建一個簡單的 Flask 應用
app = Flask(__name__)

# 配置郵件設置
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 465))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'False').lower() == 'true'
app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'True').lower() == 'true'
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'bookwormkobo521@gmail.com')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'bookwormkobo521@gmail.com')

# 初始化 Mail
mail = Mail(app)

def send_test_email(recipient_email):
    """
    發送測試郵件
    
    Args:
        recipient_email (str): 接收者的電子郵件地址
    
    Returns:
        bool: 發送成功返回 True，否則返回 False
    """
    try:
        # 打印詳細的郵件配置信息，用於調試
        print(f"郵件配置信息:")
        print(f"MAIL_SERVER: {app.config.get('MAIL_SERVER')}")
        print(f"MAIL_PORT: {app.config.get('MAIL_PORT')}")
        print(f"MAIL_USE_TLS: {app.config.get('MAIL_USE_TLS')}")
        print(f"MAIL_USE_SSL: {app.config.get('MAIL_USE_SSL')}")
        print(f"MAIL_USERNAME: {app.config.get('MAIL_USERNAME')}")
        print(f"MAIL_DEFAULT_SENDER: {app.config.get('MAIL_DEFAULT_SENDER')}")
        
        subject = "噶陀十方尊勝佛學會持咒統計 - 測試郵件"
        body = f"""
親愛的用戶：

您好！這是一封來自噶陀十方尊勝佛學會持咒統計系統的測試郵件。

如果您收到這封郵件，表示我們的電子郵件發送功能正常運作。

祝您修行順利！

噶陀十方尊勝佛學會持咒統計團隊
"""
        
        print(f"嘗試發送測試郵件至 {recipient_email}")
        
        # 使用 Flask-Mail 發送郵件
        with app.app_context():
            msg = Message(
                subject=subject,
                recipients=[recipient_email],
                body=body,
                sender=app.config['MAIL_DEFAULT_SENDER']
            )
            
            mail.send(msg)
            
        print(f"測試郵件已成功發送至 {recipient_email}")
        logger.info(f"測試郵件已發送至 {recipient_email}")
        return True
        
    except Exception as e:
        print(f"發送測試郵件時發生錯誤: {str(e)}")
        logger.error(f"發送測試郵件時發生錯誤: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        recipient_email = sys.argv[1]
    else:
        recipient_email = "goldking521@gmail.com"  # 預設收件人
    
    logger.info(f"開始發送測試郵件至 {recipient_email}")
    success = send_test_email(recipient_email)
    
    if success:
        logger.info(f"測試郵件已成功發送至 {recipient_email}")
        print(f"測試郵件已成功發送至 {recipient_email}，請檢查收件箱")
    else:
        logger.error(f"測試郵件發送失敗")
        print(f"測試郵件發送失敗，請檢查錯誤日誌")
