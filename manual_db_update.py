#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
手動數據庫更新腳本
用於添加ceremony表和更新mantra_record表
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
            # 檢查ceremony表是否存在
            with db.engine.connect() as connection:
                result = connection.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='ceremony'"))
                ceremony_exists = result.fetchone() is not None
            
            if ceremony_exists:
                logger.info("ceremony表已存在")
            else:
                # 創建ceremony表
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
            
            # 檢查mantra_record表是否有ceremony_id列
            with db.engine.connect() as connection:
                result = connection.execute(text("PRAGMA table_info(mantra_record)"))
                columns = [row[1] for row in result.fetchall()]
            
            if 'ceremony_id' not in columns:
                logger.info("添加ceremony_id列到mantra_record表...")
                with db.engine.connect() as connection:
                    connection.execute(text("ALTER TABLE mantra_record ADD COLUMN ceremony_id INTEGER"))
                    connection.commit()
                logger.info("ceremony_id列添加成功")
            else:
                logger.info("ceremony_id列已存在")
            
            logger.info("數據庫結構更新完成")
            
            # 創建示例法會
            from app.models.ceremony import Ceremony
            from datetime import datetime, timedelta
            
            existing_ceremony = Ceremony.query.filter_by(name='蓮師薈供法會').first()
            if not existing_ceremony:
                today = datetime.today().date()
                ceremony = Ceremony(
                    name='蓮師薈供法會',
                    description='每月蓮花生大士薈供法會，殊勝功德，共同修持蓮師心咒',
                    start_date=today,
                    end_date=today + timedelta(days=30),
                    is_active=True
                )
                db.session.add(ceremony)
                db.session.commit()
                logger.info(f"創建示例法會：{ceremony.name}")
            else:
                logger.info("示例法會已存在")
            
            # 創建另一個示例法會
            existing_ceremony2 = Ceremony.query.filter_by(name='阿彌陀佛法會').first()
            if not existing_ceremony2:
                today = datetime.today().date()
                ceremony2 = Ceremony(
                    name='阿彌陀佛法會',
                    description='阿彌陀佛念佛法會，專修淨土法門，共同念佛求生極樂',
                    start_date=today + timedelta(days=31),
                    end_date=today + timedelta(days=60),
                    is_active=True
                )
                db.session.add(ceremony2)
                db.session.commit()
                logger.info(f"創建示例法會：{ceremony2.name}")
            else:
                logger.info("阿彌陀佛法會已存在")
                
        except Exception as e:
            logger.error(f"數據庫更新失敗：{str(e)}")
            import traceback
            logger.error(f"詳細錯誤：{traceback.format_exc()}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    manual_db_update() 