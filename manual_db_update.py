#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
手動數據庫更新腳本
用於檢查並創建所有必要的表
"""

from app import create_app, db
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def manual_db_update():
    """手動更新數據庫結構"""
    app = create_app()
    
    with app.app_context():
        try:
            # 首先檢查所有表的存在情況
            with db.engine.connect() as connection:
                result = connection.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
                existing_tables = [row[0] for row in result.fetchall()]
                logger.info(f"現有表: {existing_tables}")
            
            # 如果沒有任何表，先創建所有基本表
            if not existing_tables or len(existing_tables) == 0:
                logger.info("數據庫為空，創建所有表...")
                db.create_all()
                logger.info("所有表創建完成")
                
                # 重新檢查表
                with db.engine.connect() as connection:
                    result = connection.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
                    existing_tables = [row[0] for row in result.fetchall()]
                    logger.info(f"創建後的表: {existing_tables}")
            
            # 檢查ceremony表是否存在
            if 'ceremony' not in existing_tables:
                logger.info("創建ceremony表...")
                with db.engine.connect() as connection:
                    connection.execute(text("""
                        CREATE TABLE ceremony (
                            id INTEGER PRIMARY KEY,
                            name VARCHAR(100) NOT NULL UNIQUE,
                            description TEXT,
                            start_date DATE NOT NULL,
                            end_date DATE NOT NULL,
                            is_active BOOLEAN DEFAULT 1,
                            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                        )
                    """))
                    connection.commit()
                logger.info("ceremony表創建成功")
            else:
                logger.info("ceremony表已存在")
            
            # 檢查mantra_record表
            if 'mantra_record' not in existing_tables:
                logger.error("mantra_record表不存在！請先運行數據庫初始化")
                logger.info("嘗試創建基本表結構...")
                db.create_all()
                
                # 再次檢查
                with db.engine.connect() as connection:
                    result = connection.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
                    existing_tables = [row[0] for row in result.fetchall()]
                    logger.info(f"重新創建後的表: {existing_tables}")
            
            # 檢查mantra_record表是否有ceremony_id列
            if 'mantra_record' in existing_tables:
                with db.engine.connect() as connection:
                    result = connection.execute(text("PRAGMA table_info(mantra_record)"))
                    columns = [row[1] for row in result.fetchall()]
                    logger.info(f"mantra_record表的列: {columns}")
                
                if 'ceremony_id' not in columns:
                    logger.info("添加ceremony_id列到mantra_record表...")
                    with db.engine.connect() as connection:
                        connection.execute(text("ALTER TABLE mantra_record ADD COLUMN ceremony_id INTEGER"))
                        connection.commit()
                    logger.info("ceremony_id列添加成功")
                else:
                    logger.info("ceremony_id列已存在")
            
            logger.info("數據庫結構檢查完成")
            
            # 創建示例法會
            from app.models.ceremony import Ceremony
            from datetime import datetime, timedelta
            
            # 檢查是否需要創建示例法會
            ceremony_count = Ceremony.query.count()
            logger.info(f"現有法會數量: {ceremony_count}")
            
            if ceremony_count == 0:
                logger.info("創建示例法會...")
                
                today = datetime.today().date()
                
                # 蓮師薈供法會
                ceremony1 = Ceremony(
                    name='蓮師薈供法會',
                    description='每月蓮花生大士薈供法會，殊勝功德，共同修持蓮師心咒',
                    start_date=today,
                    end_date=today + timedelta(days=30),
                    is_active=True
                )
                db.session.add(ceremony1)
                
                # 阿彌陀佛法會
                ceremony2 = Ceremony(
                    name='阿彌陀佛法會',
                    description='阿彌陀佛念佛法會，專修淨土法門，共同念佛求生極樂',
                    start_date=today + timedelta(days=31),
                    end_date=today + timedelta(days=60),
                    is_active=True
                )
                db.session.add(ceremony2)
                
                db.session.commit()
                logger.info("示例法會創建完成")
            else:
                logger.info("法會已存在，跳過創建")
            
            # 最終檢查
            with db.engine.connect() as connection:
                result = connection.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
                final_tables = [row[0] for row in result.fetchall()]
                logger.info(f"最終表列表: {final_tables}")
                
        except Exception as e:
            logger.error(f"數據庫更新失敗：{str(e)}")
            import traceback
            logger.error(f"詳細錯誤：{traceback.format_exc()}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    manual_db_update() 