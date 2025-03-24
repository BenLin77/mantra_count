from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, NumberRange, Optional, Length

class MantraCountForm(FlaskForm):
    """唸咒計數表單"""
    mantra = SelectField('咒語', validators=[
        DataRequired(message='請輸入唸咒次數'),
    ], coerce=int)
    count = IntegerField('唸咒次數', validators=[
        DataRequired(message='請輸入唸咒次數'),
        NumberRange(min=1, message='唸咒次數必須大於0')
    ])
    submit = SubmitField('記錄')

class MantraCreateForm(FlaskForm):
    """創建新咒語表單（管理員使用）"""
    name = StringField('咒語名稱', validators=[
        DataRequired(message='請輸入咒語名稱'),
        Length(min=2, max=100, message='咒語名稱長度必須在2到100個字符之間')
    ])
    sanskrit = StringField('梵文原文', validators=[Optional()])
    chinese = StringField('中文音譯', validators=[Optional()])
    description = TextAreaField('咒語描述', validators=[Optional()])
    benefits = TextAreaField('功德利益', validators=[Optional()])
    is_default = BooleanField('設為預設咒語')
    submit = SubmitField('創建')

class MantraEditForm(FlaskForm):
    """編輯咒語表單（管理員使用）"""
    name = StringField('咒語名稱', validators=[
        DataRequired(message='請輸入咒語名稱'),
        Length(min=2, max=100, message='咒語名稱長度必須在2到100個字符之間')
    ])
    sanskrit = StringField('梵文原文', validators=[Optional()])
    chinese = StringField('中文音譯', validators=[Optional()])
    description = TextAreaField('咒語描述', validators=[Optional()])
    benefits = TextAreaField('功德利益', validators=[Optional()])
    is_default = BooleanField('設為預設咒語')
    submit = SubmitField('更新')
