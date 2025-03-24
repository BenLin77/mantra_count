#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import sys
import os
import time

def test_mail_api():
    """
    測試 PythonAnywhere API 郵件發送功能
    """
    # 從環境變數獲取 API 令牌和用戶名，或使用預設值
    api_token = os.environ.get('PYTHONANYWHERE_API_TOKEN', '7d95840bc232406674ed66af90ba7540aba7ada9')
    username = os.environ.get('PYTHONANYWHERE_USERNAME', 'mantra')
    recipient = 'ben198777@gmail.com'  # 收件人郵箱
    
    print(f"=== PythonAnywhere API 郵件測試 ===")
    print(f"時間戳: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API 令牌: {api_token[:5]}...{api_token[-5:]}")
    print(f"用戶名: {username}")
    print(f"收件人: {recipient}")
    print("=" * 40)
    
    # 準備郵件內容
    subject = '測試 PythonAnywhere API 郵件發送'
    message = f"""
    親愛的用戶：

    您好！這是一封測試郵件，用於測試 PythonAnywhere API 的郵件發送功能。

    發送時間: {time.strftime('%Y-%m-%d %H:%M:%S')}
    
    如果您收到此郵件，表示 PythonAnywhere API 郵件發送功能正常運作。

    祝您修行順利！

    噶陀十方尊勝佛學會持咒統計團隊
    """
    
    data = {
        'recipient': recipient,
        'subject': subject,
        'message': message
    }
    
    print(f"API 端點: https://www.pythonanywhere.com/api/v0/user/{username}/mail/")
    print(f"正在發送郵件...")
    
    try:
        # 發送 API 請求
        start_time = time.time()
        response = requests.post(
            f'https://www.pythonanywhere.com/api/v0/user/{username}/mail/',
            headers={'Authorization': f'Token {api_token}'},
            json=data,
            timeout=30  # 設置超時時間為 30 秒
        )
        end_time = time.time()
        
        # 輸出回應詳情
        print(f"請求耗時: {end_time - start_time:.2f} 秒")
        print(f"狀態碼: {response.status_code}")
        print(f"回應內容: {response.text}")
        
        # 判斷是否成功
        if response.status_code == 200:
            print("✓ 郵件發送成功！")
            return True
        else:
            print("✗ 郵件發送失敗！")
            
            # 提供可能的解決方案
            if response.status_code == 401:
                print("可能原因: API 令牌無效或已過期")
                print("解決方案: 在 PythonAnywhere 帳戶設定中重新生成 API 令牌")
            elif response.status_code == 403:
                print("可能原因: 帳戶沒有使用郵件 API 的權限")
                print("解決方案: 升級 PythonAnywhere 帳戶或檢查帳戶權限")
            elif response.status_code == 404:
                print("可能原因: API 端點錯誤或用戶名不正確")
                print("解決方案: 確認用戶名是否正確")
            else:
                print(f"可能原因: 未知錯誤，請查看回應內容")
            
            return False
            
    except requests.exceptions.Timeout:
        print("✗ 請求超時！")
        print("可能原因: PythonAnywhere API 服務器響應緩慢或網絡問題")
        print("解決方案: 稍後再試或檢查網絡連接")
        return False
        
    except requests.exceptions.RequestException as e:
        print(f"✗ 請求異常: {str(e)}")
        print("可能原因: 網絡連接問題或 API 端點錯誤")
        print("解決方案: 檢查網絡連接或 API 端點是否正確")
        return False
        
    except Exception as e:
        print(f"✗ 未知錯誤: {str(e)}")
        print(f"錯誤類型: {type(e).__name__}")
        import traceback
        print(f"錯誤堆疊: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("\n開始測試 PythonAnywhere API 郵件發送功能...\n")
    success = test_mail_api()
    print("\n測試完成！")
    print(f"結果: {'成功' if success else '失敗'}")
    sys.exit(0 if success else 1)
