from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.validators import DataRequired
from datetime import datetime

class CalendarForm(FlaskForm):
    """行事曆表單"""
    year = SelectField('年份', validators=[DataRequired()], coerce=int)
    submit = SubmitField('下載行事曆')
    
    def __init__(self, *args, **kwargs):
        super(CalendarForm, self).__init__(*args, **kwargs)
        # 生成年份選項，從當前年份開始，往後5年
        current_year = datetime.now().year
        roc_years = [(y, f'民國 {y - 1911} 年') for y in range(current_year, current_year + 6)]
        self.year.choices = roc_years
