# Gmail 設置指南

為了讓應用程式能夠通過 Gmail 發送電子郵件，您需要進行以下設置：

## 1. 開啟 Google 帳戶的兩步驗證

1. 訪問 [Google 帳戶安全性設置](https://myaccount.google.com/security)
2. 點擊「兩步驗證」
3. 按照指示啟用兩步驗證

## 2. 生成應用程式專用密碼

1. 訪問 [Google 帳戶安全性設置](https://myaccount.google.com/security)
2. 點擊「應用程式密碼」（如果沒有看到此選項，請確保已開啟兩步驗證）
3. 在「選擇應用程式」下拉選單中選擇「其他（自訂名稱）」
4. 輸入一個名稱，例如「噶陀十方尊勝佛學會持咒統計」
5. 點擊「生成」
6. Google 會顯示一個 16 位字元的密碼，請複製此密碼

## 3. 更新環境變數

將生成的應用程式專用密碼添加到您的 `.env` 文件中：

```
MAIL_PASSWORD=您的應用程式專用密碼
```

## 注意事項

- 應用程式專用密碼只會顯示一次，請確保您已保存
- 如果您忘記了密碼，可以隨時在 Google 帳戶中撤銷並生成新的密碼
- 不要與他人分享您的應用程式專用密碼
