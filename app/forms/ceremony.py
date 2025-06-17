from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, ValidationError
from datetime import datetime

class CeremonyCreateForm(FlaskForm):
    """創建法會表單"""
    name = StringField('法會名稱', validators=[
        DataRequired(message='請輸入法會名稱'),
        Length(min=2, max=100, message='法會名稱長度必須在2到100個字符之間')
    ])
    description = TextAreaField('法會描述', validators=[Optional()])
    start_date = DateField('開始日期', validators=[
        DataRequired(message='請選擇開始日期')
    ], default=datetime.today)
    end_date = DateField('結束日期', validators=[
        DataRequired(message='請選擇結束日期')
    ], default=datetime.today)
    is_active = BooleanField('啟用法會', default=True)
    submit = SubmitField('創建法會')
    
    def validate_end_date(self, field):
        if field.data < self.start_date.data:
            raise ValidationError('結束日期不能早於開始日期')

class CeremonyEditForm(FlaskForm):
    """編輯法會表單"""
    name = StringField('法會名稱', validators=[
        DataRequired(message='請輸入法會名稱'),
        Length(min=2, max=100, message='法會名稱長度必須在2到100個字符之間')
    ])
    description = TextAreaField('法會描述', validators=[Optional()])
    start_date = DateField('開始日期', validators=[
        DataRequired(message='請選擇開始日期')
    ])
    end_date = DateField('結束日期', validators=[
        DataRequired(message='請選擇結束日期')
    ])
    is_active = BooleanField('啟用法會')
    submit = SubmitField('更新法會')
    
    def validate_end_date(self, field):
        if field.data < self.start_date.data:
            raise ValidationError('結束日期不能早於開始日期') 