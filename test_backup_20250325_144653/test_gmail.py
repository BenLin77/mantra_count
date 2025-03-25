#!/usr/bin/env python
# -*- coding: utf-8 -*-

import smtplib
import ssl
import os
from dotenv import load_dotenv
import sys
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import socket

# 載入環境變數
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

def test_gmail_smtp():
    """測試使用 Gmail SMTP 發送郵件"""
    # 郵件配置
    smtp_server = "smtp.gmail.com"
    port = 587  # 使用 TLS 的端口
    sender_email = os.environ.get('MAIL_USERNAME', 'bookwormkobo521@gmail.com')
    password = os.environ.get('MAIL_PASSWORD', '')  # 從環境變數獲取密碼
    receiver_email = "bookwormkobo521@gmail.com"  # 發送給自己測試
    
    # 打印配置信息
    print(f"郵件配置信息:")
    print(f"SMTP 服務器: {smtp_server}")
    print(f"端口: {port}")
    print(f"發件人: {sender_email}")
    print(f"收件人: {receiver_email}")
    
    # 創建郵件
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = Header('噶陀十方尊勝佛學會持咒統計 - Gmail SMTP 測試', 'utf-8')
    
    # 郵件內容
    body = f"""
    這是一封測試郵件，用於測試 Gmail SMTP 發送功能。
    
    發送時間: {time.strftime('%Y-%m-%d %H:%M:%S')}
    
    如果您收到這封郵件，表示 Gmail SMTP 發送功能正常。
    
    噶陀十方尊勝佛學會持咒統計團隊
    """
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    try:
        # 創建安全連接
        context = ssl.create_default_context()
        
        # 連接到郵件服務器（設置超時時間為 10 秒）
        print(f"連接到 {smtp_server}:{port}...")
        server = smtplib.SMTP(smtp_server, port, timeout=10)
        
        # 啟用 TLS 加密
        print("啟用 TLS 加密...")
        server.starttls(context=context)
        
        # 登入
        print(f"登入 ({sender_email})...")
        server.login(sender_email, password)
        
        # 發送郵件
        print(f"發送郵件至 {receiver_email}...")
        server.sendmail(sender_email, receiver_email, msg.as_string())
        print("郵件發送成功！")
        
        # 關閉連接
        server.quit()
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("認證失敗！請檢查您的用戶名和密碼。")
        print("如果您使用的是 Gmail，請確保：")
        print("1. 已開啟「允許不安全的應用程式」設定")
        print("2. 或者已設置應用程式專用密碼")
        return False
        
    except socket.timeout:
        print("連接超時！可能是網路問題或郵件服務器回應緩慢。")
        return False
        
    except Exception as e:
        print(f"發送郵件時發生錯誤: {str(e)}")
        print(f"錯誤類型: {type(e).__name__}")
        return False

if __name__ == "__main__":
    print("測試 Gmail SMTP 郵件發送功能")
    test_gmail_smtp()
