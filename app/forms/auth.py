from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Regexp
from app.models.user import User

class LoginForm(FlaskForm):
    """登入表單"""
    email = StringField('電子郵件', validators=[
        DataRequired(message='請輸入電子郵件'),
        Email(message='請輸入有效的電子郵件地址')
    ])
    password = PasswordField('密碼', validators=[DataRequired(message='請輸入密碼')])
    remember_me = BooleanField('記住我')
    submit = SubmitField('登入')

class RegisterForm(FlaskForm):
    """註冊表單"""
    username = StringField('用戶名', validators=[
        DataRequired(message='請輸入用戶名'),
        Length(min=3, max=20, message='用戶名長度必須在3到20個字符之間')
    ])
    email = StringField('電子郵件', validators=[
        DataRequired(message='請輸入電子郵件'),
        Email(message='請輸入有效的電子郵件地址')
    ])
    password = PasswordField('密碼', validators=[
        DataRequired(message='請輸入密碼'),
        Length(min=6, message='密碼長度不能少於6個字符')
    ])
    password2 = PasswordField('確認密碼', validators=[
        DataRequired(message='請再次輸入密碼'),
        EqualTo('password', message='兩次輸入的密碼不一致')
    ])
    submit = SubmitField('註冊')

    def validate_username(self, username):
        """驗證用戶名是否已存在"""
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('該用戶名已被使用，請選擇其他用戶名')

    def validate_email(self, email):
        """驗證電子郵件是否已存在"""
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('該電子郵件已被註冊')

class VerificationForm(FlaskForm):
    """電子郵件驗證碼表單"""
    code = StringField('驗證碼', validators=[
        DataRequired(message='請輸入驗證碼'),
        Length(min=6, max=6, message='驗證碼必須是6位數字')
    ])
    submit = SubmitField('驗證')

class ResetPasswordRequestForm(FlaskForm):
    """請求重設密碼表單"""
    email = StringField('電子郵件', validators=[
        DataRequired(message='請輸入電子郵件'),
        Email(message='請輸入有效的電子郵件地址')
    ])
    submit = SubmitField('發送重設密碼說明')

class ResetPasswordForm(FlaskForm):
    """重設密碼表單"""
    password = PasswordField('新密碼', validators=[
        DataRequired(message='請輸入新密碼'),
        Length(min=6, message='密碼長度不能少於6個字符')
    ])
    password2 = PasswordField('確認新密碼', validators=[
        DataRequired(message='請再次輸入新密碼'),
        EqualTo('password', message='兩次輸入的密碼不一致')
    ])
    submit = SubmitField('重設密碼')
