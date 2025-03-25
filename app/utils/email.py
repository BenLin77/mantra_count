from flask import current_app, render_template, url_for
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
from threading import Thread

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
            
            # 確保正確處理中文字符
            text_part = MIMEText(msg.body, 'plain', 'utf-8')
            mime_msg.attach(text_part)
            
            # 增加超時時間
            socket.setdefaulttimeout(60)  # 增加到 60 秒
            
            # 連接到郵件服務器
            print(f"連接到郵件服務器 {smtp_server}:{port}...", file=sys.stderr)
            try:
                if use_ssl:
                    server = smtplib.SMTP_SSL(smtp_server, port, timeout=60, context=context)
                else:
                    server = smtplib.SMTP(smtp_server, port, timeout=60)
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
                
            except socket.timeout:
                print("連接郵件服務器超時，嘗試使用備用方式發送...", file=sys.stderr)
                # 嘗試使用 PythonAnywhere API 作為備用
                if send_email_via_pythonanywhere_api(msg.recipients[0], msg.subject, msg.body):
                    print("使用 PythonAnywhere API 成功發送郵件", file=sys.stderr)
                    return
                else:
                    raise Exception("所有郵件發送方式都失敗了")
                    
            except smtplib.SMTPAuthenticationError:
                print("郵件服務器認證失敗，請檢查用戶名和密碼", file=sys.stderr)
                raise
                
            except smtplib.SMTPException as e:
                print(f"SMTP 錯誤: {str(e)}", file=sys.stderr)
                raise
                
            except Exception as e:
                print(f"發送郵件時發生錯誤: {str(e)}", file=sys.stderr)
                raise
                
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
                # 最後嘗試使用 PythonAnywhere API
                if send_email_via_pythonanywhere_api(msg.recipients[0], msg.subject, msg.body):
                    print("使用 PythonAnywhere API 成功發送郵件", file=sys.stderr)
                else:
                    print("所有郵件發送方式都失敗了", file=sys.stderr)

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

def send_verification_email(temp_user):
    """發送電子郵件驗證連結
    
    Args:
        temp_user: 臨時用戶對象
        
    Returns:
        bool: 郵件發送是否成功
    """
    try:
        current_app.logger.info(f'為臨時用戶 {temp_user.username} ({temp_user.email}) 發送驗證郵件')
        
        verification_url = url_for(
            'auth.verify_email',
            token=temp_user.verification_token,
            _external=True
        )
        
        result = send_email(
            subject='【噶陀十方尊勝佛學會】請驗證您的電子郵件',
            recipients=[temp_user.email],
            text_body=f'''親愛的 {temp_user.username}：

感謝您註冊噶陀十方尊勝佛學會持咒計數系統。

請點擊以下連結驗證您的電子郵件：
{verification_url}

如果您沒有註冊帳號，請忽略此郵件。

祝福您
噶陀十方尊勝佛學會
''',
            html_body=f'''
<p>親愛的 {temp_user.username}：</p>
<p>感謝您註冊噶陀十方尊勝佛學會持咒計數系統。</p>
<p>請點擊以下連結驗證您的電子郵件：</p>
<p><a href="{verification_url}">驗證電子郵件</a></p>
<p>如果您沒有註冊帳號，請忽略此郵件。</p>
<p>祝福您<br>噶陀十方尊勝佛學會</p>
'''
        )
        
        return result
    except Exception as e:
        current_app.logger.error(f'發送驗證郵件時發生錯誤: {str(e)}')
        return False

def send_async_email(app, msg):
    """在背景執行緒中發送電子郵件"""
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            print(f'發送電子郵件失敗: {str(e)}')

def send_email(subject, recipients, text_body, html_body=None):
    """
    發送電子郵件的通用函數
    
    Args:
        subject (str): 郵件主題
        recipients (list): 收件人列表
        text_body (str): 純文本郵件內容
        html_body (str, optional): HTML 格式郵件內容
        
    Returns:
        bool: 發送成功返回 True，否則返回 False
    """
    try:
        # 打印詳細的郵件配置信息，用於調試
        print(f"郵件配置信息:", file=sys.stderr)
        print(f"MAIL_SERVER: {current_app.config.get('MAIL_SERVER')}", file=sys.stderr)
        print(f"MAIL_PORT: {current_app.config.get('MAIL_PORT')}", file=sys.stderr)
        print(f"MAIL_USE_TLS: {current_app.config.get('MAIL_USE_TLS')}", file=sys.stderr)
        print(f"MAIL_USE_SSL: {current_app.config.get('MAIL_USE_SSL')}", file=sys.stderr)
        print(f"MAIL_USERNAME: {current_app.config.get('MAIL_USERNAME')}", file=sys.stderr)
        print(f"MAIL_DEFAULT_SENDER: {current_app.config.get('MAIL_DEFAULT_SENDER')}", file=sys.stderr)
        
        print(f"嘗試發送郵件至 {recipients}", file=sys.stderr)
        
        # 使用 Flask-Mail 發送郵件（直接方式，不使用背景線程）
        try:
            print(f"使用 Flask-Mail 發送電子郵件...", file=sys.stderr)
            
            msg = Message(
                subject=subject,
                recipients=recipients,
                body=text_body,
                html=html_body,
                sender=current_app.config['MAIL_DEFAULT_SENDER']
            )
            
            # 同步發送郵件
            mail.send(msg)
            
            print(f"使用 Flask-Mail 成功發送郵件至 {recipients}", file=sys.stderr)
            logging.info(f"郵件已發送至 {recipients}")
            return True
            
        except Exception as mail_error:
            print(f"使用 Flask-Mail 發送郵件失敗: {str(mail_error)}", file=sys.stderr)
            
            # 嘗試使用 PythonAnywhere API 作為備選方案
            try:
                print(f"嘗試使用 PythonAnywhere API 發送郵件...", file=sys.stderr)
                if send_email_via_pythonanywhere_api(recipients[0], subject, text_body):
                    print(f"使用 PythonAnywhere API 成功發送郵件至 {recipients}", file=sys.stderr)
                    logging.info(f"郵件已通過 PythonAnywhere API 發送至 {recipients}")
                    return True
                else:
                    print(f"使用 PythonAnywhere API 發送郵件失敗", file=sys.stderr)
            except Exception as api_error:
                print(f"使用 PythonAnywhere API 發送郵件時發生錯誤: {str(api_error)}", file=sys.stderr)
            
            return False
        
    except Exception as e:
        print(f"準備發送電子郵件時發生錯誤: {str(e)}", file=sys.stderr)
        return False

def send_password_reset_email(user):
    """
    發送密碼重設連結
    
    Args:
        user: 用戶對象，包含 email 和 username 屬性
        
    Returns:
        bool: 發送成功返回 True，否則返回 False
    """
    try:
        token = user.get_reset_password_token()
        print(f"為用戶 {user.username} ({user.email}) 生成密碼重設令牌", file=sys.stderr)
        
        return send_email(
            subject='【噶陀十方尊勝佛學會】重設您的密碼',
            recipients=[user.email],
            text_body=f'''親愛的 {user.username}：

您收到此郵件是因為您請求重設密碼。

請點擊以下連結以重設您的密碼：

{url_for('auth.reset_password', token=token, _external=True)}

如果您沒有請求重設密碼，請忽略此郵件。

祝您修行順利！

噶陀十方尊勝佛學會持咒統計團隊''',
            html_body=f'''
<p>親愛的 {user.username}：</p>
<p>您收到此郵件是因為您請求重設密碼。</p>
<p>請點擊以下連結以重設您的密碼：</p>
<p><a href="{url_for('auth.reset_password', token=token, _external=True)}">重設密碼</a></p>
<p>如果您沒有請求重設密碼，請忽略此郵件。</p>
<p>祝您修行順利！</p>
<p>噶陀十方尊勝佛學會持咒統計團隊</p>'''
        )
    except Exception as e:
        print(f"準備發送密碼重設郵件時發生錯誤: {str(e)}", file=sys.stderr)
        return False
