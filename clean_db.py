#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
清除資料庫中除了管理者以外的所有使用者及其咒語記錄
"""

import os
from dotenv import load_dotenv
from app import create_app, db
from app.models.user import User
from app.models.mantra import MantraRecord

# 載入環境變數
load_dotenv()

app = create_app()

with app.app_context():
    # 獲取所有非管理員用戶
    non_admin_users = User.query.filter_by(is_admin=False).all()
    
    # 輸出將被刪除的用戶數量
    print(f"找到 {len(non_admin_users)} 個非管理員用戶，準備刪除...")
    
    # 刪除每個非管理員用戶的咒語記錄和用戶本身
    for user in non_admin_users:
        # 刪除用戶的咒語記錄
        records = MantraRecord.query.filter_by(user_id=user.id).all()
        for record in records:
            db.session.delete(record)
        
        # 輸出用戶信息
        print(f"刪除用戶 '{user.username}' 及其 {len(records)} 條咒語記錄")
        
        # 刪除用戶
        db.session.delete(user)
    
    # 提交更改
    db.session.commit()
    
    # 輸出結果
    print("資料庫清理完成！只保留了管理員用戶。")
