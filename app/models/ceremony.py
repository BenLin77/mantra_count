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
    ceremony_order = db.Column(db.Integer, default=0)  # 法會順序，用於輪替
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 與唸誦記錄的關聯
    records = db.relationship('MantraRecord', backref='ceremony', lazy='dynamic', foreign_keys='MantraRecord.ceremony_id')
    
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
    
    @staticmethod
    def get_fridays_in_month(year, month):
        """獲取指定年月的所有週五日期"""
        fridays = []
        # 找到該月第一天
        first_day = datetime(year, month, 1).date()
        # 找到該月最後一天
        if month == 12:
            last_day = datetime(year + 1, 1, 1).date() - timedelta(days=1)
        else:
            last_day = datetime(year, month + 1, 1).date() - timedelta(days=1)
        
        # 找到第一個週五
        current_date = first_day
        while current_date.weekday() != 4:  # 4 = 週五
            current_date += timedelta(days=1)
        
        # 收集所有週五
        while current_date <= last_day:
            fridays.append(current_date)
            current_date += timedelta(days=7)
        
        return fridays
    
    @staticmethod
    def assign_ceremonies_to_fridays(year, month):
        """將法會分配到指定年月的週五，返回分配結果"""
        fridays = Ceremony.get_fridays_in_month(year, month)
        ceremonies = Ceremony.query.filter_by(is_active=True).order_by(Ceremony.ceremony_order).all()
        
        if not ceremonies:
            return []
        
        assignments = []
        for i, friday in enumerate(fridays):
            ceremony = ceremonies[i % len(ceremonies)]  # 輪替分配
            assignments.append({
                'date': friday,
                'ceremony': ceremony,
                'weekday': friday.strftime('%A'),
                'formatted_date': f"{friday.strftime('%m月%d日')} ({['週一', '週二', '週三', '週四', '週五', '週六', '週日'][friday.weekday()]})"
            })
        
        return assignments 