from datetime import datetime, timedelta
import secrets
from werkzeug.security import generate_password_hash
from app import db
from app.models.user import User

class TempUser(db.Model):
    """臨時用戶模型，用於存儲未驗證的用戶資料"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    verification_token = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    
    def __init__(self, username, email, password, expires_in=86400):
        """初始化臨時用戶，設置過期時間為24小時"""
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.verification_token = secrets.token_urlsafe(32)
        self.created_at = datetime.utcnow()
        self.expires_at = self.created_at + timedelta(seconds=expires_in)
    
    def is_expired(self):
        """檢查臨時用戶是否已過期"""
        return datetime.utcnow() > self.expires_at
    
    def to_user(self):
        """將臨時用戶轉換為正式用戶"""
        user = User(
            username=self.username,
            email=self.email,
            email_verified=True
        )
        user.password_hash = self.password_hash  # 直接設置密碼哈希，避免再次哈希
        return user
    
    @staticmethod
    def cleanup_expired():
        """清理所有過期的臨時用戶"""
        expired = TempUser.query.filter(TempUser.expires_at < datetime.utcnow()).all()
        for temp_user in expired:
            db.session.delete(temp_user)
        db.session.commit()
        return len(expired)
