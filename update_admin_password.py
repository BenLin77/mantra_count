from app import create_app, db
from app.models.user import User
from config import Config

def update_admin_password():
    """更新管理員密碼"""
    app = create_app()
    with app.app_context():
        # 查找管理員帳號
        admin_username = Config.ADMIN_USERNAME
        admin = User.query.filter_by(username=admin_username).first()
        
        if admin:
            # 更新管理員密碼
            admin.set_password(Config.ADMIN_PASSWORD)
            db.session.commit()
            print(f'已更新管理員 {admin_username} 的密碼')
        else:
            print(f'找不到管理員帳號: {admin_username}')

if __name__ == '__main__':
    update_admin_password()
