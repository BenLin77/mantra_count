import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Email 配置
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'false').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'bookwormkobo521@gmail.com')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'xxxxxxxxxxxxxx')  # 請在 .env 中設定正確的密碼
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'bookwormkobo521@gmail.com')
    
    # Engagelab SMS 配置
    ENGAGELAB_USER = os.environ.get('ENGAGELAB_USER')
    ENGAGELAB_KEY = os.environ.get('ENGAGELAB_KEY')
    ENGAGELAB_TEMPLATE_ID = os.environ.get('ENGAGELAB_TEMPLATE_ID')
    
    # 管理員帳號配置
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME') or 'admin'
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD') or '!Changleisi666'
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL') or 'admin@example.com'
    
    # 每頁顯示的記錄數
    RECORDS_PER_PAGE = 10
