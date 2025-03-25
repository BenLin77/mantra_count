import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
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
