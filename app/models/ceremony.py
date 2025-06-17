from datetime import datetime, timedelta
from app import db

class Ceremony(db.Model):
    """法會模型"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)  # 法會名稱
    description = db.Column(db.Text)  # 法會描述
    start_date = db.Column(db.Date, nullable=False)  # 開始日期
    end_date = db.Column(db.Date, nullable=False)  # 結束日期
    is_active = db.Column(db.Boolean, default=True)  # 是否啟用
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 與唸誦記錄的關聯
    records = db.relationship('MantraRecord', backref='ceremony', lazy='dynamic')
    
    def __repr__(self):
        return f'<法會 {self.name}>'
    
    def get_total_count(self):
        """獲取此法會的總唸誦次數"""
        return sum(record.count for record in self.records)
    
    def get_days_count(self):
        """獲取法會總天數"""
        return (self.end_date - self.start_date).days + 1
    
    def is_in_period(self, date):
        """檢查指定日期是否在法會期間內"""
        return self.start_date <= date <= self.end_date
    
    @staticmethod
    def get_active_ceremony_for_date(date):
        """獲取指定日期的啟用法會"""
        return Ceremony.query.filter(
            Ceremony.is_active == True,
            Ceremony.start_date <= date,
            Ceremony.end_date >= date
        ).first()
    
    @staticmethod
    def get_current_ceremony():
        """獲取當前日期的法會"""
        today = datetime.utcnow().date()
        return Ceremony.get_active_ceremony_for_date(today) 