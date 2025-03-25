from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, session
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from app.models.user import User
from app.forms.auth import (LoginForm, RegistrationForm, VerificationForm,
                          ResetPasswordRequestForm, ResetPasswordForm)
from app.utils.sms import send_verification_code
import sys
import secrets
from datetime import datetime, timedelta

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """用戶登入視圖"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('用戶名或密碼不正確', 'danger')
            return redirect(url_for('auth.login'))
        
        if not user.is_verified:
            flash('請先驗證您的手機號碼', 'warning')
            return redirect(url_for('auth.verify', username=user.username))
        
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('main.index')
        return redirect(next_page)
    
    return render_template('auth/login.html', title='登入', form=form)

@bp.route('/logout')
def logout():
    """用戶登出視圖"""
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """用戶註冊視圖"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # 檢查用戶名和手機號碼是否已存在
        if User.query.filter_by(username=form.username.data).first():
            flash('該用戶名已被使用', 'danger')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(phone=form.phone.data).first():
            flash('該手機號碼已被註冊', 'danger')
            return redirect(url_for('auth.register'))
        
        # 生成驗證碼
        verification_code = ''.join(secrets.choice('0123456789') for _ in range(6))
        verification_expires = datetime.utcnow() + timedelta(minutes=10)
        
        # 將用戶資料存儲在 session 中，而不是直接寫入資料庫
        session['pending_user'] = {
            'username': form.username.data,
            'phone': form.phone.data,
            'password': form.password.data,  # 這裡存儲的是明文密碼，將在驗證成功後進行哈希處理
            'verification_code': verification_code,
            'verification_expires': verification_expires.timestamp()
        }
        
        # 發送驗證碼簡訊
        send_verification_code(form.phone.data, verification_code)
        
        flash('請輸入您收到的驗證碼完成手機號碼驗證', 'success')
        return redirect(url_for('auth.verify', username=form.username.data))
    
    return render_template('auth/register.html', title='註冊', form=form)

@bp.route('/verify/<username>', methods=['GET', 'POST'])
def verify(username):
    """手機號碼驗證視圖"""
    if current_user.is_authenticated and current_user.is_verified:
        return redirect(url_for('main.index'))
    
    # 檢查 session 中是否有待驗證的用戶資料
    pending_user = session.get('pending_user')
    if not pending_user or pending_user.get('username') != username:
        flash('註冊會話已過期或無效，請重新註冊', 'danger')
        return redirect(url_for('auth.register'))
    
    form = VerificationForm()
    
    if form.validate_on_submit():
        # 驗證碼是否正確且未過期
        if (pending_user.get('verification_code') == form.code.data and 
                datetime.utcnow().timestamp() < pending_user.get('verification_expires')):
            
            # 驗證成功，創建新用戶並寫入資料庫
            user = User(
                username=pending_user.get('username'),
                phone=pending_user.get('phone'),
                is_verified=True
            )
            user.set_password(pending_user.get('password'))
            
            db.session.add(user)
            db.session.commit()
            
            # 清除 session 中的臨時資料
            session.pop('pending_user', None)
            
            flash('驗證成功！您現在可以登入了', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('驗證碼無效或已過期', 'danger')
    
    return render_template('auth/verify.html', title='驗證手機號碼', form=form, username=username)

@bp.route('/resend_code/<username>')
def resend_code(username):
    """重新發送驗證碼"""
    # 檢查 session 中是否有待驗證的用戶資料
    pending_user = session.get('pending_user')
    if not pending_user or pending_user.get('username') != username:
        flash('註冊會話已過期或無效，請重新註冊', 'danger')
        return redirect(url_for('auth.register'))
    
    # 生成新的驗證碼
    verification_code = ''.join(secrets.choice('0123456789') for _ in range(6))
    verification_expires = datetime.utcnow() + timedelta(minutes=10)
    
    # 更新 session 中的驗證碼
    pending_user['verification_code'] = verification_code
    pending_user['verification_expires'] = verification_expires.timestamp()
    session['pending_user'] = pending_user
    
    # 發送新的驗證碼
    send_verification_code(pending_user.get('phone'), verification_code)
    
    flash('新的驗證碼已發送至您的手機', 'info')
    return redirect(url_for('auth.verify', username=username))

@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    """請求重設密碼視圖"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(phone=form.phone.data).first()
        
        if user:
            # 生成驗證碼
            verification_code = user.generate_verification_code()
            db.session.commit()
            
            # 發送驗證碼簡訊
            send_verification_code(user.phone, verification_code)
            
            flash('驗證碼已發送至您的手機，請查收', 'info')
            return redirect(url_for('auth.reset_password', phone=user.phone))
        else:
            flash('找不到該手機號碼的用戶', 'danger')
    
    return render_template('auth/reset_password_request.html', title='重設密碼', form=form)

@bp.route('/reset_password/<phone>', methods=['GET', 'POST'])
def reset_password(phone):
    """重設密碼視圖"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    user = User.query.filter_by(phone=phone).first_or_404()
    form = ResetPasswordForm()
    
    if form.validate_on_submit():
        if user.verify_verification_code(form.code.data):
            user.set_password(form.password.data)
            db.session.commit()
            flash('您的密碼已重設成功！', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('驗證碼無效或已過期', 'danger')
    
    return render_template('auth/reset_password.html', title='重設密碼', form=form)

@bp.route('/test_verification_code')
def test_verification_code():
    """測試驗證碼生成和顯示"""
    import secrets
    code = ''.join(secrets.choice('0123456789') for _ in range(6))
    print(f"\n\n==== 測試驗證碼: {code} ====\n\n", file=sys.stderr)
    return f"驗證碼已生成，請查看控制台輸出。驗證碼：{code}"
