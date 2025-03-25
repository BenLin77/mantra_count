#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from dotenv import load_dotenv
import sys
from app import create_app

# 載入環境變數
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

def check_email_config():
    """檢查電子郵件配置是否正確"""
    print("檢查電子郵件配置...")
    
    # 從環境變數獲取配置
    mail_server = os.environ.get('MAIL_SERVER')
    mail_port = os.environ.get('MAIL_PORT')
    mail_use_tls = os.environ.get('MAIL_USE_TLS')
    mail_use_ssl = os.environ.get('MAIL_USE_SSL')
    mail_username = os.environ.get('MAIL_USERNAME')
    mail_password = os.environ.get('MAIL_PASSWORD')
    mail_default_sender = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # 打印環境變數配置
    print("\n環境變數配置:")
    print(f"MAIL_SERVER: {mail_server}")
    print(f"MAIL_PORT: {mail_port}")
    print(f"MAIL_USE_TLS: {mail_use_tls}")
    print(f"MAIL_USE_SSL: {mail_use_ssl}")
    print(f"MAIL_USERNAME: {mail_username}")
    print(f"MAIL_PASSWORD: {'已設置' if mail_password else '未設置'}")
    print(f"MAIL_DEFAULT_SENDER: {mail_default_sender}")
    
    # 創建 Flask 應用並獲取配置
    app = create_app()
    
    # 打印 Flask 應用配置
    print("\nFlask 應用配置:")
    print(f"MAIL_SERVER: {app.config.get('MAIL_SERVER')}")
    print(f"MAIL_PORT: {app.config.get('MAIL_PORT')}")
    print(f"MAIL_USE_TLS: {app.config.get('MAIL_USE_TLS')}")
    print(f"MAIL_USE_SSL: {app.config.get('MAIL_USE_SSL')}")
    print(f"MAIL_USERNAME: {app.config.get('MAIL_USERNAME')}")
    print(f"MAIL_PASSWORD: {'已設置' if app.config.get('MAIL_PASSWORD') else '未設置'}")
    print(f"MAIL_DEFAULT_SENDER: {app.config.get('MAIL_DEFAULT_SENDER')}")
    
    # 檢查配置是否完整
    if not app.config.get('MAIL_SERVER'):
        print("\n錯誤: MAIL_SERVER 未設置")
        return False
    
    if not app.config.get('MAIL_PORT'):
        print("\n錯誤: MAIL_PORT 未設置")
        return False
    
    if not app.config.get('MAIL_USERNAME'):
        print("\n錯誤: MAIL_USERNAME 未設置")
        return False
    
    if not app.config.get('MAIL_PASSWORD'):
        print("\n錯誤: MAIL_PASSWORD 未設置")
        return False
    
    # 檢查 TLS 和 SSL 設置
    if not app.config.get('MAIL_USE_TLS') and not app.config.get('MAIL_USE_SSL'):
        print("\n警告: MAIL_USE_TLS 和 MAIL_USE_SSL 都未設置，這可能導致連接問題")
    
    if app.config.get('MAIL_USE_TLS') and app.config.get('MAIL_USE_SSL'):
        print("\n警告: MAIL_USE_TLS 和 MAIL_USE_SSL 不應同時設置為 True")
    
    # 檢查 Gmail 特定設置
    if 'gmail.com' in app.config.get('MAIL_SERVER', ''):
        if app.config.get('MAIL_PORT') == 587 and not app.config.get('MAIL_USE_TLS'):
            print("\n警告: 使用 Gmail 端口 587 時，MAIL_USE_TLS 應設置為 True")
        
        if app.config.get('MAIL_PORT') == 465 and not app.config.get('MAIL_USE_SSL'):
            print("\n警告: 使用 Gmail 端口 465 時，MAIL_USE_SSL 應設置為 True")
    
    print("\n配置檢查完成！")
    return True

if __name__ == "__main__":
    print("電子郵件配置檢查工具")
    check_email_config()
