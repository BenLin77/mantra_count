import smtplib
import ssl
import os
from dotenv import load_dotenv
import sys
import socket
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

# 載入環境變數
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

def send_test_email(receiver_email):
    # 郵件配置
    smtp_server = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    port = int(os.environ.get('MAIL_PORT') or 465)
    use_ssl = os.environ.get('MAIL_USE_SSL') == 'True'
    sender_email = os.environ.get('MAIL_USERNAME')
    password = os.environ.get('MAIL_PASSWORD')
    
    # 打印配置信息
    print(f"郵件配置信息:")
    print(f"MAIL_SERVER: {smtp_server}")
    print(f"MAIL_PORT: {port}")
    print(f"MAIL_USE_SSL: {use_ssl}")
    print(f"MAIL_USERNAME: {sender_email}")
    print(f"接收者: {receiver_email}")
    
    # 創建郵件
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = Header('噶陀十方尊勝佛學會持咒統計 - 測試郵件', 'utf-8')
    
    # 郵件內容
    body = """
    這是一封測試郵件，用於驗證電子郵件發送功能是否正常工作。
    
    如果您收到這封郵件，表示電子郵件發送功能正常。
    
    噶陀十方尊勝佛學會持咒統計團隊
    """
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    try:
        # 創建安全連接
        context = ssl.create_default_context()
        
        # 設置超時時間
        socket.setdefaulttimeout(30)  # 設置 30 秒超時
        
        # 連接到郵件服務器
        print("連接到郵件服務器...")
        start_time = time.time()
        
        try:
            if use_ssl:
                # 使用 SSL 連接
                print("使用 SSL 連接...")
                server = smtplib.SMTP_SSL(smtp_server, port, timeout=30, context=context)
            else:
                # 使用普通連接，後續啟用 TLS
                server = smtplib.SMTP(smtp_server, port, timeout=30)
            
            print(f"連接成功，耗時 {time.time() - start_time:.2f} 秒")
            
            try:
                if not use_ssl:
                    # 如果不使用 SSL，則啟用 TLS
                    print("啟用 TLS 加密...")
                    server.ehlo()  # 與服務器打招呼
                    server.starttls(context=context)  # 啟用 TLS 加密
                    server.ehlo()  # 再次打招呼
                
                print(f"登入郵件服務器 ({sender_email})...")
                server.login(sender_email, password)  # 登入
                
                print(f"發送郵件至 {receiver_email}...")
                server.sendmail(sender_email, receiver_email, msg.as_string())
                print("郵件發送成功！")
                
                server.quit()
                return True
            except Exception as e:
                print(f"與郵件服務器通信時發生錯誤: {str(e)}")
                if hasattr(e, 'smtp_code'):
                    print(f"SMTP 錯誤碼: {e.smtp_code}")
                if hasattr(e, 'smtp_error'):
                    print(f"SMTP 錯誤信息: {e.smtp_error}")
                server.quit()
                return False
        except socket.timeout:
            print("連接到郵件服務器超時，請檢查網絡連接或郵件服務器設置")
            return False
        except socket.gaierror:
            print("無法解析郵件服務器地址，請檢查 MAIL_SERVER 設置")
            return False
        except ConnectionRefusedError:
            print("連接被拒絕，請檢查郵件服務器地址和端口設置")
            return False
    except Exception as e:
        print(f"發送郵件時發生錯誤: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    print("測試電子郵件發送功能")
    # 使用指定的電子郵件地址作為接收者
    receiver_email = "goldking521@gmail.com"
    send_test_email(receiver_email)
