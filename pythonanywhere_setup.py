#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PythonAnywhere 設置腳本
用於重建 Flask 數據庫並清理測試文件

使用方法:
1. 重建數據庫: python pythonanywhere_setup.py rebuild_db
2. 清理測試文件: python pythonanywhere_setup.py clean_tests
3. 執行所有操作: python pythonanywhere_setup.py all
"""

import os
import sys
import glob
import shutil
import logging
from datetime import datetime
from dotenv import load_dotenv

# 載入 .env 文件中的環境變數
load_dotenv()

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"pythonanywhere_setup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 測試文件模式列表
TEST_FILE_PATTERNS = [
    "test_*.py",
    "*_test.py",
    "send_test_*.py"
]

# Flask 應用程序入口點
FLASK_APP = "app.py"

# 管理員設定
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'bookwormkobo521@gmail.com')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', '!Changleisi666')
ADMIN_USERNAME = 'admin'

# 蓮花生大士心咒設定
PADMASAMBHAVA_MANTRA = {
    'name': '蓮花生大士心咒',
    'sanskrit': 'oṃ āḥ hūṃ vajra guru padma siddhi hūṃ',
    'chinese': '嗡啊吽 班雜咕嚕貝瑪悉地吽',
    'description': '蓮花生大士是藏傳佛教的開山祖師，此咒語能消除障礙、增長智慧、圓滿成就。',
    'is_default': True
}

def rebuild_database():
    """重建 Flask 數據庫"""
    try:
        logger.info("開始重建 Flask 數據庫...")
        
        # 刪除現有的數據庫文件 (如果存在)
        db_path = os.path.join(os.getcwd(), "app.db")
        if os.path.exists(db_path):
            backup_name = f"{db_path}.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            logger.info(f"備份現有數據庫到 {backup_name}")
            shutil.copy2(db_path, backup_name)
            os.remove(db_path)
            logger.info("已刪除現有數據庫文件")
        
        # 檢查遷移目錄是否存在
        migrations_dir = os.path.join(os.getcwd(), "migrations")
        if not os.path.exists(migrations_dir):
            logger.info("遷移目錄不存在，將創建新的遷移環境")
            os.system(f"FLASK_APP={FLASK_APP} flask db init")
        else:
            # 刪除遷移文件夾中的版本文件 (保留目錄結構)
            migrations_versions_dir = os.path.join(migrations_dir, "versions")
            if os.path.exists(migrations_versions_dir):
                for file in os.listdir(migrations_versions_dir):
                    if file.endswith(".py") and file != "__init__.py":
                        os.remove(os.path.join(migrations_versions_dir, file))
                logger.info("已清理遷移版本文件")
        
        # 創建遷移腳本
        logger.info("創建遷移腳本...")
        os.system(f"FLASK_APP={FLASK_APP} flask db migrate -m 'initial migration'")
        
        # 應用遷移
        logger.info("應用遷移...")
        os.system(f"FLASK_APP={FLASK_APP} flask db upgrade")
        
        # 初始化數據庫內容
        logger.info("初始化數據庫內容...")
        initialize_database_content()
        
        logger.info("數據庫重建完成！")
        return True
    except Exception as e:
        logger.error(f"重建數據庫時發生錯誤: {str(e)}")
        return False

def initialize_database_content():
    """初始化數據庫內容，創建管理員帳號和預設咒語"""
    try:
        # 導入必要的模型
        from app import create_app, db
        from app.models.user import User
        from app.models.mantra import Mantra
        
        app = create_app()
        with app.app_context():
            # 創建管理員帳號
            admin = User.query.filter_by(username=ADMIN_USERNAME).first()
            if not admin:
                admin = User(
                    username=ADMIN_USERNAME,
                    email=ADMIN_EMAIL,
                    is_admin=True,
                    email_verified=True
                )
                admin.set_password(ADMIN_PASSWORD)
                db.session.add(admin)
                logger.info(f"已創建管理員帳號: {ADMIN_USERNAME} ({ADMIN_EMAIL})")
            else:
                # 更新現有管理員帳號
                admin.email = ADMIN_EMAIL
                admin.set_password(ADMIN_PASSWORD)
                admin.is_admin = True
                admin.email_verified = True
                logger.info(f"已更新管理員帳號: {ADMIN_USERNAME} ({ADMIN_EMAIL})")
            
            # 創建蓮花生大士心咒
            padmasambhava = Mantra.query.filter_by(name=PADMASAMBHAVA_MANTRA['name']).first()
            if not padmasambhava:
                padmasambhava = Mantra(
                    name=PADMASAMBHAVA_MANTRA['name'],
                    sanskrit=PADMASAMBHAVA_MANTRA['sanskrit'],
                    chinese=PADMASAMBHAVA_MANTRA['chinese'],
                    description=PADMASAMBHAVA_MANTRA['description'],
                    is_default=PADMASAMBHAVA_MANTRA['is_default']
                )
                db.session.add(padmasambhava)
                logger.info(f"已創建預設咒語: {PADMASAMBHAVA_MANTRA['name']}")
            else:
                # 確保蓮花生大士心咒為預設咒語
                padmasambhava.is_default = True
                logger.info(f"已將 {PADMASAMBHAVA_MANTRA['name']} 設為預設咒語")
                
                # 將其他咒語設為非預設
                other_mantras = Mantra.query.filter(Mantra.id != padmasambhava.id).all()
                for mantra in other_mantras:
                    if mantra.is_default:
                        mantra.is_default = False
                        logger.info(f"已將 {mantra.name} 設為非預設咒語")
            
            # 提交所有更改
            db.session.commit()
            logger.info("數據庫內容初始化完成")
            
    except Exception as e:
        logger.error(f"初始化數據庫內容時發生錯誤: {str(e)}")
        raise

def clean_test_files():
    """清理測試相關的 Python 文件"""
    try:
        logger.info("開始清理測試文件...")
        
        removed_count = 0
        for pattern in TEST_FILE_PATTERNS:
            for file_path in glob.glob(pattern):
                if os.path.isfile(file_path):
                    logger.info(f"刪除測試文件: {file_path}")
                    os.remove(file_path)
                    removed_count += 1
        
        if removed_count > 0:
            logger.info(f"已清理 {removed_count} 個測試文件")
        else:
            logger.info("未找到需要清理的測試文件")
        
        return True
    except Exception as e:
        logger.error(f"清理測試文件時發生錯誤: {str(e)}")
        return False

def main():
    """主函數"""
    if len(sys.argv) < 2:
        logger.error("請指定操作: rebuild_db, clean_tests, 或 all")
        sys.exit(1)
    
    action = sys.argv[1].lower()
    
    if action == "rebuild_db":
        if rebuild_database():
            logger.info("數據庫重建成功")
        else:
            logger.error("數據庫重建失敗")
            sys.exit(1)
    
    elif action == "clean_tests":
        if clean_test_files():
            logger.info("測試文件清理成功")
        else:
            logger.error("測試文件清理失敗")
            sys.exit(1)
    
    elif action == "all":
        success = rebuild_database() and clean_test_files()
        if success:
            logger.info("所有操作完成")
        else:
            logger.error("操作過程中發生錯誤")
            sys.exit(1)
    
    else:
        logger.error(f"未知操作: {action}")
        logger.error("有效操作: rebuild_db, clean_tests, all")
        sys.exit(1)

if __name__ == "__main__":
    logger.info("開始執行 PythonAnywhere 設置腳本")
    main()
    logger.info("腳本執行完畢")
