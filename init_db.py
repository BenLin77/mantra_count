from app import create_app, db
from app.models.user import User
from app.models.mantra import Mantra
from config import Config
import os

def init_db():
    """初始化資料庫，創建管理員帳號和預設咒語"""
    app = create_app()
    with app.app_context():
        # 創建資料表
        db.create_all()
        
        # 檢查是否已有管理員帳號
        admin_username = Config.ADMIN_USERNAME
        admin = User.query.filter_by(username=admin_username).first()
        
        if not admin:
            # 創建管理員帳號
            admin = User(
                username=admin_username,
                email=Config.ADMIN_EMAIL,
                is_admin=True,
                email_verified=True
            )
            admin.set_password(Config.ADMIN_PASSWORD)
            db.session.add(admin)
            print(f'已創建管理員帳號: {admin_username}')
        
        # 檢查是否已有預設咒語
        default_mantra = Mantra.query.filter_by(is_default=True).first()
        
        if not default_mantra:
            # 創建預設咒語（蓮花生大士心咒）
            default_mantra = Mantra(
                name='蓮花生大士心咒',
                sanskrit='ॐ ཨཱཿ ཧཱུྃ བཛྲ གུ རུ པདྨ སིདྡྷི ཧཱུྃ',
                chinese='嗡阿吽 班雜 咕嚕 貝瑪 悉地吽',
                description='蓮花生大士心咒是藏傳佛教中最重要的咒語之一，也稱為十二字咒或金剛上師心咒。',
                benefits='持誦此咒可以消除障礙、增長智慧、獲得加持，並與蓮師相應。',
                is_default=True
            )
            db.session.add(default_mantra)
            print(f'已創建預設咒語: {default_mantra.name}')
        
        # 提交更改
        db.session.commit()
        print('資料庫初始化完成！')

if __name__ == '__main__':
    init_db()
