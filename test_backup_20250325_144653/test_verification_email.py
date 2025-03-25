#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask
from app import create_app
from app.utils.email import send_verification_code
import logging
import sys
import random
import string

# 設置日誌記錄
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def generate_verification_code(length=6):
    """生成指定長度的隨機驗證碼"""
    return ''.join(random.choices(string.digits, k=length))

def test_verification_code():
    """測試發送驗證碼郵件功能"""
    try:
        # 創建 Flask 應用
        app = create_app()
        
        with app.app_context():
            # 打印郵件配置信息
            print(f"Flask 郵件配置信息:")
            print(f"MAIL_SERVER: {app.config.get('MAIL_SERVER')}")
            print(f"MAIL_PORT: {app.config.get('MAIL_PORT')}")
            print(f"MAIL_USE_TLS: {app.config.get('MAIL_USE_TLS')}")
            print(f"MAIL_USE_SSL: {app.config.get('MAIL_USE_SSL')}")
            print(f"MAIL_USERNAME: {app.config.get('MAIL_USERNAME')}")
            print(f"MAIL_DEFAULT_SENDER: {app.config.get('MAIL_DEFAULT_SENDER')}")
            
            # 生成隨機驗證碼
            verification_code = generate_verification_code()
            
            # 測試郵件接收者
            recipient_email = "bookwormkobo521@gmail.com"
            
            print(f"開始發送驗證碼 {verification_code} 至 {recipient_email}...")
            
            try:
                # 使用 send_verification_code 函數發送驗證碼
                result = send_verification_code(recipient_email, verification_code)
                
                if result:
                    print(f"驗證碼已發送至 {recipient_email}，請檢查收件箱")
                    logger.info(f"驗證碼已發送至 {recipient_email}")
                else:
                    print(f"驗證碼發送失敗")
                    logger.error(f"驗證碼發送失敗")
                
            except Exception as e:
                print(f"發送驗證碼時發生錯誤: {str(e)}")
                logger.error(f"發送驗證碼時發生錯誤: {str(e)}")
            
    except Exception as e:
        print(f"初始化應用時發生錯誤: {str(e)}")
        logger.error(f"初始化應用時發生錯誤: {str(e)}")

if __name__ == "__main__":
    print("測試驗證碼郵件發送功能")
    test_verification_code()
