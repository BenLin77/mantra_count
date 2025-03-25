#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import logging
from dotenv import load_dotenv
from flask import Flask
from app import create_app, db
from app.models.user import User
from app.utils.email import send_verification_email

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 載入環境變數
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

def test_verification_email():
    """測試網頁驗證郵件發送功能"""
    
    # 創建應用程序上下文
    app = create_app()
    
    # 設置必要的配置項，以便在非請求上下文中生成 URL
    app.config['SERVER_NAME'] = 'localhost:5000'
    app.config['APPLICATION_ROOT'] = '/'
    app.config['PREFERRED_URL_SCHEME'] = 'http'
    
    with app.app_context():
        # 檢查是否已有測試用戶
        test_email = "goldking521@gmail.com"
        user = User.query.filter_by(email=test_email).first()
        
        if not user:
            # 創建測試用戶
            logger.info(f"創建測試用戶: {test_email}")
            user = User(
                username="測試用戶",
                email=test_email,
                email_verified=False
            )
            user.set_password("testpassword123")
            db.session.add(user)
            db.session.commit()
            logger.info(f"測試用戶已創建")
        else:
            logger.info(f"使用現有測試用戶: {test_email}")
        
        # 打印郵件配置信息
        logger.info("Flask 郵件配置信息:")
        logger.info(f"MAIL_SERVER: {app.config.get('MAIL_SERVER')}")
        logger.info(f"MAIL_PORT: {app.config.get('MAIL_PORT')}")
        logger.info(f"MAIL_USE_TLS: {app.config.get('MAIL_USE_TLS')}")
        logger.info(f"MAIL_USE_SSL: {app.config.get('MAIL_USE_SSL')}")
        logger.info(f"MAIL_USERNAME: {app.config.get('MAIL_USERNAME')}")
        logger.info(f"MAIL_DEFAULT_SENDER: {app.config.get('MAIL_DEFAULT_SENDER')}")
        logger.info(f"SERVER_NAME: {app.config.get('SERVER_NAME')}")
        
        # 發送驗證郵件
        logger.info(f"開始發送驗證郵件至 {test_email}...")
        result = send_verification_email(user)
        
        if result:
            logger.info(f"驗證郵件已成功發送至 {test_email}")
            print(f"驗證郵件已成功發送至 {test_email}，請檢查收件箱")
            print("如果您沒有收到郵件，請檢查垃圾郵件資料夾")
        else:
            logger.error(f"驗證郵件發送失敗")
            print(f"驗證郵件發送失敗，請檢查錯誤日誌")

if __name__ == "__main__":
    logger.info("測試網頁驗證郵件發送功能")
    test_verification_email()
