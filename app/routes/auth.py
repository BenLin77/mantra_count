from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.user import User
from app.models.temp_user import TempUser
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
            
        # 檢查臨時用戶表中是否已有此電子郵件
        if TempUser.query.filter_by(email=form.email.data).first():
            flash('此電子郵件已在註冊流程中，請檢查您的郵箱或等待驗證連結過期後再試', 'warning')
            return redirect(url_for('auth.register'))
        
        # 清理過期的臨時用戶
        TempUser.cleanup_expired()
        
        # 創建臨時用戶
        temp_user = TempUser(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
        )
        
        # 添加到數據庫
        db.session.add(temp_user)
        
        try:
            # 提交臨時用戶到數據庫
            db.session.commit()
            
            # 發送驗證郵件
            email_sent = send_verification_email(temp_user)
            
            if email_sent:
                flash('註冊申請已提交！請查看您的電子郵件以完成驗證。驗證連結有效期為24小時。', 'success')
                return redirect(url_for('auth.login'))
            else:
                # 郵件發送失敗，刪除臨時用戶
                db.session.delete(temp_user)
                db.session.commit()
                flash('註冊失敗，無法發送驗證郵件。請稍後再試或聯繫管理員。', 'error')
                return redirect(url_for('auth.register'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'註冊過程中發生錯誤: {str(e)}')
            flash('註冊過程中發生錯誤，請稍後再試。', 'error')
            return redirect(url_for('auth.register'))
        
    return render_template('auth/register.html', title='註冊', form=form)

@bp.route('/verify/<token>')
def verify_email(token):
    # 清理過期的臨時用戶
    TempUser.cleanup_expired()
    
    # 查找對應的臨時用戶
    temp_user = TempUser.query.filter_by(verification_token=token).first()
    
    if not temp_user:
        # 檢查是否是舊系統的令牌
        user = User.verify_email_token(token)
        if user:
            user.email_verified = True
            db.session.commit()
            flash('電子郵件驗證成功！', 'success')
        else:
            flash('驗證連結無效或已過期', 'error')
        return redirect(url_for('auth.login'))
    
    # 檢查臨時用戶是否過期
    if temp_user.is_expired():
        db.session.delete(temp_user)
        db.session.commit()
        flash('驗證連結已過期，請重新註冊', 'error')
        return redirect(url_for('auth.register'))
    
    try:
        # 創建正式用戶
        user = temp_user.to_user()
        
        # 添加到數據庫
        db.session.add(user)
        
        # 刪除臨時用戶
        db.session.delete(temp_user)
        
        # 提交更改
        db.session.commit()
        
        flash('電子郵件驗證成功！您現在可以登入了。', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'驗證過程中發生錯誤: {str(e)}')
        flash('驗證過程中發生錯誤，請稍後再試或聯繫管理員。', 'error')
    
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
