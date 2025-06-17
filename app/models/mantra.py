from datetime import datetime, timedelta
from app import db

class Mantra(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True, unique=True)
    sanskrit = db.Column(db.String(200))  # 梵文原文
    chinese = db.Column(db.String(200))   # 中文音譯
    description = db.Column(db.Text)      # 咒語描述
    benefits = db.Column(db.Text)         # 功德利益
    is_default = db.Column(db.Boolean, default=False)  # 是否為預設咒語
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    records = db.relationship('MantraRecord', backref='mantra', lazy='dynamic')
    
    def __repr__(self):
        return f'<咒語 {self.name}>'
    
    def get_total_count(self):
        """獲取此咒語的總唸誦次數"""
        return sum(record.count for record in self.records)
    
    @staticmethod
    def get_default_mantra():
        """獲取預設咒語（蓮花生大士心咒）"""
        default_mantra = Mantra.query.filter_by(is_default=True).first()
        if not default_mantra:
            # 如果沒有預設咒語，創建蓮花生大士心咒
            default_mantra = Mantra(
                name='蓮花生大士心咒',
                sanskrit='ॐ ཨཱཿ ཧཱུྃ བཛྲ གུ རུ པདྨ སིདྡྷི ཧཱུྃ',
                chinese='嗡阿吽 班雜 咕嚕 貝瑪 悉地吽',
                description='蓮花生大士心咒是藏傳佛教中最重要的咒語之一，也稱為十二字咒或金剛上師心咒。',
                benefits='持誦此咒可以消除障礙、增長智慧、獲得加持，並與蓮師相應。',
                is_default=True
            )
            db.session.add(default_mantra)
            db.session.commit()
        return default_mantra


class MantraRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    mantra_id = db.Column(db.Integer, db.ForeignKey('mantra.id'))
    ceremony_id = db.Column(db.Integer, db.ForeignKey('ceremony.id'), nullable=True)  # 法會關聯
    count = db.Column(db.Integer, default=0)  # 唸誦次數
    record_date = db.Column(db.Date, default=datetime.utcnow().date)  # 記錄日期
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新時間
    
    def __repr__(self):
        return f'<唸誦記錄 用戶:{self.user_id} 咒語:{self.mantra_id} 次數:{self.count}>'
    
    def get_weekday_name(self):
        """獲取記錄日期的星期名稱"""
        weekdays = ['週一', '週二', '週三', '週四', '週五', '週六', '週日']
        return weekdays[self.record_date.weekday()]
    
    def get_formatted_date(self):
        """獲取格式化的日期字符串（包含星期）"""
        return f"{self.record_date.strftime('%Y-%m-%d')} ({self.get_weekday_name()})"
    
    @staticmethod
    def get_today_record(user_id, mantra_id):
        """獲取今日的唸誦記錄，如果不存在則創建"""
        from app.models.ceremony import Ceremony  # 避免循環導入
        
        today = datetime.utcnow().date()
        record = MantraRecord.query.filter_by(
            user_id=user_id,
            mantra_id=mantra_id,
            record_date=today
        ).first()
        
        if not record:
            # 檢查當前日期是否有對應的法會
            current_ceremony = Ceremony.get_current_ceremony()
            
            record = MantraRecord(
                user_id=user_id,
                mantra_id=mantra_id,
                ceremony_id=current_ceremony.id if current_ceremony else None,
                count=0,
                record_date=today
            )
            db.session.add(record)
            db.session.commit()
        
        return record
    
    @staticmethod
    def get_user_records_by_date(user_id, days=7):
        """獲取用戶最近幾天的唸誦記錄"""
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days-1)
        
        records = MantraRecord.query.filter(
            MantraRecord.user_id == user_id,
            MantraRecord.record_date >= start_date,
            MantraRecord.record_date <= end_date
        ).order_by(MantraRecord.record_date.desc()).all()
        
        return records
    
    @staticmethod
    def get_total_count():
        """獲取所有用戶的總唸誦次數"""
        return sum(record.count for record in MantraRecord.query.all())
    
    @staticmethod
    def get_total_count_by_mantra(mantra_id):
        """獲取特定咒語的總唸誦次數"""
        return sum(record.count for record in MantraRecord.query.filter_by(mantra_id=mantra_id).all())
