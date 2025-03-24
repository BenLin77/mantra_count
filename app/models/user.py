from datetime import datetime, timedelta
import secrets
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)
    verification_code = db.Column(db.String(6))
    verification_code_expires = db.Column(db.DateTime)
    mantra_records = db.relationship('MantraRecord', backref='user', lazy='dynamic')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<用戶 {self.username}>'
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_total_mantras(self):
        """獲取用戶的總唸咒數量"""
        return sum(record.count for record in self.mantra_records)
    
    def get_mantra_count(self, mantra_id):
        """獲取用戶特定咒語的唸咒數量"""
        records = MantraRecord.query.filter_by(user_id=self.id, mantra_id=mantra_id).all()
        return sum(record.count for record in records)
    
    def generate_verification_code(self):
        """生成6位數的驗證碼，並設置10分鐘的有效期"""
        self.verification_code = ''.join(secrets.choice('0123456789') for _ in range(6))
        self.verification_code_expires = datetime.utcnow() + timedelta(minutes=10)
        return self.verification_code
    
    def verify_verification_code(self, code):
        """驗證驗證碼是否正確且未過期"""
        if self.verification_code is None or self.verification_code_expires is None:
            return False
        
        if datetime.utcnow() > self.verification_code_expires:
            return False
        
        return self.verification_code == code

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
