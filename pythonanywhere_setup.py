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

def rebuild_database():
    """重建 Flask 數據庫"""
    try:
        logger.info("開始重建 Flask 數據庫...")
        
        # 刪除現有的數據庫文件 (如果存在)
        db_path = os.path.join(os.getcwd(), "app.db")
        if os.path.exists(db_path):
            logger.info(f"備份現有數據庫到 app.db.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            shutil.copy2(db_path, f"{db_path}.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            os.remove(db_path)
            logger.info("已刪除現有數據庫文件")
        
        # 刪除遷移文件夾中的版本文件 (保留目錄結構)
        migrations_versions_dir = os.path.join(os.getcwd(), "migrations", "versions")
        if os.path.exists(migrations_versions_dir):
            for file in os.listdir(migrations_versions_dir):
                if file.endswith(".py") and file != "__init__.py":
                    os.remove(os.path.join(migrations_versions_dir, file))
            logger.info("已清理遷移版本文件")
        
        # 初始化遷移環境
        logger.info("初始化遷移環境...")
        os.system("FLASK_APP=mantra_count.py flask db init")
        
        # 創建遷移腳本
        logger.info("創建遷移腳本...")
        os.system("FLASK_APP=mantra_count.py flask db migrate -m 'initial migration'")
        
        # 應用遷移
        logger.info("應用遷移...")
        os.system("FLASK_APP=mantra_count.py flask db upgrade")
        
        logger.info("數據庫重建完成！")
        return True
    except Exception as e:
        logger.error(f"重建數據庫時發生錯誤: {str(e)}")
        return False

def clean_test_files():
    """清理測試相關的 Python 文件"""
    try:
        logger.info("開始清理測試文件...")
        
        # 創建備份目錄
        backup_dir = os.path.join(os.getcwd(), f"test_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        os.makedirs(backup_dir, exist_ok=True)
        logger.info(f"創建備份目錄: {backup_dir}")
        
        # 查找並移動測試文件
        test_files = []
        for pattern in TEST_FILE_PATTERNS:
            test_files.extend(glob.glob(os.path.join(os.getcwd(), pattern)))
        
        if not test_files:
            logger.info("未找到測試文件")
            return True
        
        for file_path in test_files:
            if os.path.isfile(file_path):
                file_name = os.path.basename(file_path)
                backup_path = os.path.join(backup_dir, file_name)
                shutil.copy2(file_path, backup_path)
                os.remove(file_path)
                logger.info(f"已備份並刪除測試文件: {file_name}")
        
        logger.info(f"測試文件清理完成！所有文件已備份到 {backup_dir}")
        return True
    except Exception as e:
        logger.error(f"清理測試文件時發生錯誤: {str(e)}")
        return False

def main():
    """主函數"""
    if len(sys.argv) < 2:
        print("用法: python pythonanywhere_setup.py [rebuild_db|clean_tests|all]")
        return
    
    command = sys.argv[1].lower()
    
    if command == "rebuild_db":
        rebuild_database()
    elif command == "clean_tests":
        clean_test_files()
    elif command == "all":
        db_result = rebuild_database()
        test_result = clean_test_files()
        
        if db_result and test_result:
            logger.info("所有操作已成功完成！")
        else:
            logger.warning("部分操作失敗，請查看日誌了解詳情")
    else:
        print("無效的命令。用法: python pythonanywhere_setup.py [rebuild_db|clean_tests|all]")

if __name__ == "__main__":
    logger.info("開始執行 PythonAnywhere 設置腳本")
    main()
    logger.info("腳本執行完畢")
