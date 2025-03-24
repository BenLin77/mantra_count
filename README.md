# 噶陀十方尊勝佛學會持咒統計

這是一個用於噶陀十方尊勝佛學會的持咒統計系統，用戶可以記錄自己的唸咒次數，查看個人和全體的持咒總計。

## 功能特點

- 用戶註冊和登入
- 電子郵件驗證
- 記錄唸咒次數
- 查看個人唸咒統計
- 查看持咒總計
- 管理員功能

## 安裝與運行

1. 使用 pipenv 安裝依賴套件：
   ```
   # 安裝 pipenv (如果尚未安裝)
   pip install pipenv
   
   # 使用 pipenv 安裝依賴
   pipenv install
   
   # 或者使用傳統方式安裝
   pip install -r requirements.txt
   ```

2. 設定環境變數（創建 .env 文件）：
   ```
   FLASK_APP=app.py
   FLASK_ENV=development
   SECRET_KEY=your_secret_key
   TWILIO_ACCOUNT_SID=your_twilio_sid
   TWILIO_AUTH_TOKEN=your_twilio_token
   TWILIO_PHONE_NUMBER=your_twilio_phone
   ```

3. 初始化資料庫：
   ```
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

4. 運行應用：
   ```
   flask run
   ```

## 技術架構

- 後端：Python + Flask
- 資料庫：SQLite (開發) / PostgreSQL (生產)
- 簡訊服務：Twilio API
- 前端：Bootstrap + jQuery
