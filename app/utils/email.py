from flask import current_app
from flask_mail import Message
from app import mail
import logging
import sys
import threading
import smtplib
import ssl
import socket
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import requests
import os

def send_email_async(app, msg):
    """
    在背景執行緒中發送電子郵件
    
    Args:
        app: Flask 應用程序上下文
        msg: 電子郵件訊息
    """
    with app.app_context():
        # 直接使用 smtplib 發送郵件，跳過 Flask-Mail
        try:
            print(f"直接使用 smtplib 發送電子郵件至 {msg.recipients}...", file=sys.stderr)
            start_time = time.time()
            
            smtp_server = app.config['MAIL_SERVER']
            port = app.config['MAIL_PORT']
            use_ssl = app.config['MAIL_USE_SSL']
            sender_email = app.config['MAIL_USERNAME']
            password = app.config['MAIL_PASSWORD']
            
            # 創建安全連接
            context = ssl.create_default_context()
            
            # 創建 MIME 郵件
            mime_msg = MIMEMultipart()
            mime_msg['From'] = sender_email
            mime_msg['To'] = ', '.join(msg.recipients)
            mime_msg['Subject'] = Header(msg.subject, 'utf-8')
            mime_msg.attach(MIMEText(msg.body, 'plain', 'utf-8'))
            
            # 設置較短的超時時間
            socket.setdefaulttimeout(15)  # 縮短超時時間
            
            # 連接到郵件服務器
            print(f"連接到郵件服務器 {smtp_server}:{port}...", file=sys.stderr)
            if use_ssl:
                server = smtplib.SMTP_SSL(smtp_server, port, timeout=15, context=context)
            else:
                server = smtplib.SMTP(smtp_server, port, timeout=15)
                server.ehlo()
                server.starttls(context=context)
                server.ehlo()
            
            # 登入
            print(f"登入郵件服務器 ({sender_email})...", file=sys.stderr)
            server.login(sender_email, password)
            
            # 發送郵件
            print(f"發送郵件至 {msg.recipients}...", file=sys.stderr)
            server.sendmail(sender_email, msg.recipients, mime_msg.as_string())
            server.quit()
            
            end_time = time.time()
            print(f"郵件發送完成，耗時: {end_time - start_time:.2f} 秒", file=sys.stderr)
            print(f"成功發送電子郵件至 {msg.recipients}", file=sys.stderr)
            
        except Exception as e:
            print(f"發送電子郵件失敗: {str(e)}", file=sys.stderr)
            print(f"錯誤類型: {type(e).__name__}", file=sys.stderr)
            
            # 嘗試使用 Flask-Mail 作為備選方案
            try:
                print(f"嘗試使用 Flask-Mail 發送電子郵件...", file=sys.stderr)
                mail.send(msg)
                print(f"使用 Flask-Mail 成功發送電子郵件至 {msg.recipients}", file=sys.stderr)
            except Exception as mail_error:
                print(f"使用 Flask-Mail 發送電子郵件失敗: {str(mail_error)}", file=sys.stderr)

def send_email_via_pythonanywhere_api(recipient, subject, message):
    """
    使用 PythonAnywhere API 發送電子郵件
    
    Args:
        recipient (str): 收件人電子郵件地址
        subject (str): 郵件主題
        message (str): 郵件內容
        
    Returns:
        bool: 發送成功返回 True，否則返回 False
    """
    try:
        # 從環境變數或配置中獲取 API 令牌和用戶名
        api_token = os.environ.get('PYTHONANYWHERE_API_TOKEN') or current_app.config.get('PYTHONANYWHERE_API_TOKEN')
        username = os.environ.get('PYTHONANYWHERE_USERNAME') or current_app.config.get('PYTHONANYWHERE_USERNAME', 'mantra')
        
        print(f"API 令牌: {api_token[:5]}...{api_token[-5:] if api_token else 'None'}", file=sys.stderr)
        print(f"用戶名: {username}", file=sys.stderr)
        
        if not api_token:
            print("缺少 PYTHONANYWHERE_API_TOKEN 環境變數或配置項", file=sys.stderr)
            return False
            
        # 準備請求數據
        data = {
            'recipient': recipient,
            'subject': subject,
            'message': message
        }
        
        # 發送 API 請求
        print(f"使用 PythonAnywhere API 發送郵件至 {recipient}...", file=sys.stderr)
        print(f"API URL: https://www.pythonanywhere.com/api/v0/user/{username}/mail/", file=sys.stderr)
        
        try:
            response = requests.post(
                f'https://www.pythonanywhere.com/api/v0/user/{username}/mail/',
                headers={'Authorization': f'Token {api_token}'},
                json=data,
                timeout=30  # 設置超時時間為30秒
            )
            
            # 檢查回應
            print(f"API 回應狀態碼: {response.status_code}", file=sys.stderr)
            print(f"API 回應內容: {response.text}", file=sys.stderr)
            
            if response.status_code == 200:
                print(f"使用 PythonAnywhere API 成功發送郵件至 {recipient}", file=sys.stderr)
                return True
            else:
                print(f"使用 PythonAnywhere API 發送郵件失敗: {response.text}", file=sys.stderr)
                return False
                
        except requests.exceptions.RequestException as req_err:
            print(f"API 請求異常: {str(req_err)}", file=sys.stderr)
            return False
            
    except Exception as e:
        print(f"使用 PythonAnywhere API 發送郵件時發生錯誤: {str(e)}", file=sys.stderr)
        print(f"錯誤類型: {type(e).__name__}", file=sys.stderr)
        import traceback
        print(f"錯誤堆疊: {traceback.format_exc()}", file=sys.stderr)
        return False

def send_verification_code(email, code):
    """
    發送驗證碼電子郵件
    
    Args:
        email (str): 接收者的電子郵件地址
        code (str): 6位數的驗證碼
    
    Returns:
        bool: 發送成功返回 True，否則返回 False
    """
    try:
        subject = "噶陀十方尊勝佛學會持咒統計 - 您的驗證碼"
        body = f"""
        親愛的用戶：
        
        您好！感謝您註冊噶陀十方尊勝佛學會持咒統計。
        
        您的驗證碼是：{code}
        
        此驗證碼將在 10 分鐘內有效。請不要將此驗證碼分享給其他人。
        
        如果您沒有請求此驗證碼，請忽略此郵件。
        
        祝您修行順利！
        
        噶陀十方尊勝佛學會持咒統計團隊
        """
        
        # 打印詳細的郵件配置信息，用於調試
        print(f"郵件配置信息:", file=sys.stderr)
        print(f"MAIL_SERVER: {current_app.config.get('MAIL_SERVER')}", file=sys.stderr)
        print(f"MAIL_PORT: {current_app.config.get('MAIL_PORT')}", file=sys.stderr)
        print(f"MAIL_USE_TLS: {current_app.config.get('MAIL_USE_TLS')}", file=sys.stderr)
        print(f"MAIL_USE_SSL: {current_app.config.get('MAIL_USE_SSL')}", file=sys.stderr)
        print(f"MAIL_USERNAME: {current_app.config.get('MAIL_USERNAME')}", file=sys.stderr)
        print(f"MAIL_DEFAULT_SENDER: {current_app.config.get('MAIL_DEFAULT_SENDER')}", file=sys.stderr)
        
        print(f"嘗試發送驗證碼 {code} 至 {email}", file=sys.stderr)
        
        # 使用 Flask-Mail 發送郵件
        msg = Message(
            subject=subject,
            recipients=[email],
            body=body,
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        
        # 在背景執行緒中發送電子郵件，避免阻塞主執行緒
        threading.Thread(
            target=send_email_async,
            args=(current_app._get_current_object(), msg)
        ).start()
        
        # 立即返回成功，不等待電子郵件實際發送完成
        return True
        
    except Exception as e:
        print(f"準備發送電子郵件時發生錯誤: {str(e)}", file=sys.stderr)
        return False
