from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.user import User
from app.forms.auth import LoginForm, RegisterForm, ResetPasswordRequestForm, ResetPasswordForm
from app.utils.email import send_verification_email, send_password_reset_email
from app import db
import random
import string

bp = Blueprint('auth', __name__)

def generate_verification_code():
    """生成6位數字驗證碼"""
    return ''.join(random.choices(string.digits, k=6))

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('無效的電子郵件或密碼', 'error')
            return redirect(url_for('auth.login'))
        if not user.email_verified:
            flash('請先驗證您的電子郵件地址', 'warning')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('auth/login.html', title='登入', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegisterForm()
    if form.validate_on_submit():
        # 檢查電子郵件是否已被使用
        if User.query.filter_by(email=form.email.data).first():
            flash('此電子郵件已被註冊', 'error')
            return redirect(url_for('auth.register'))
            
        # 創建新用戶但暫不提交到數據庫
        user = User(
            username=form.username.data,
            email=form.email.data,
            verification_code=generate_verification_code()
        )
        user.set_password(form.password.data)
        db.session.add(user)
        
        # 發送驗證郵件
        email_sent = send_verification_email(user)
        
        if email_sent:
            # 只有在郵件發送成功後才提交到數據庫
            db.session.commit()
            flash('註冊成功！請查看您的電子郵件以完成驗證。', 'success')
            return redirect(url_for('auth.login'))
        else:
            # 郵件發送失敗，回滾數據庫操作
            db.session.rollback()
            flash('註冊失敗，無法發送驗證郵件。請稍後再試或聯繫管理員。', 'error')
            return redirect(url_for('auth.register'))
        
    return render_template('auth/register.html', title='註冊', form=form)

@bp.route('/verify/<token>')
def verify_email(token):
    user = User.verify_email_token(token)
    if not user:
        flash('驗證連結無效或已過期', 'error')
    else:
        user.email_verified = True
        db.session.commit()
        flash('電子郵件驗證成功！', 'success')
    return redirect(url_for('auth.login'))

@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            email_sent = send_password_reset_email(user)
            if email_sent:
                flash('重設密碼的說明已發送到您的電子郵件', 'info')
            else:
                flash('發送重設密碼郵件失敗，請稍後再試或聯繫管理員', 'error')
        else:
            # 為了安全考慮，即使找不到用戶也顯示相同的消息
            flash('重設密碼的說明已發送到您的電子郵件', 'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html',
                         title='重設密碼', form=form)

@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        flash('重設密碼連結無效或已過期', 'error')
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('您的密碼已重設', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)
