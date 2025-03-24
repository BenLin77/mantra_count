from flask import Blueprint, render_template, flash, redirect, url_for, request, current_app
from flask_login import current_user, login_required
from app import db
from app.models.mantra import Mantra, MantraRecord
from app.forms.mantra import MantraCountForm
from sqlalchemy import func
from datetime import datetime

bp = Blueprint('main', __name__)

@bp.route('/', methods=['GET', 'POST'])
def index():
    """首頁"""
    form = MantraCountForm()
    
    # 獲取所有咒語
    mantras = Mantra.query.all()
    form.mantra.choices = [(m.id, m.name) for m in mantras]
    
    # 獲取全球總唸誦次數
    total_count = MantraRecord.get_total_count()
    
    # 如果用戶已登入，獲取今日記錄
    today_records = []
    if current_user.is_authenticated:
        today = datetime.utcnow().date()
        today_records = MantraRecord.query.filter_by(
            user_id=current_user.id,
            record_date=today
        ).join(Mantra).all()
    
    # 處理表單提交
    if form.validate_on_submit() and current_user.is_authenticated:
        mantra_id = form.mantra.data
        count = form.count.data
        
        # 獲取今日記錄，如果不存在則創建
        record = MantraRecord.get_today_record(current_user.id, mantra_id)
        
        # 更新記錄
        record.count += count
        db.session.commit()
        
        flash(f'已記錄 {count} 次唸誦', 'success')
        return redirect(url_for('main.index'))
    
    return render_template('index.html', 
                           title='首頁',
                           form=form, 
                           mantras=mantras,
                           total_count=total_count,
                           today_records=today_records,
                           user_stats=None)

@bp.route('/index', methods=['GET', 'POST'])
def index_alias():
    return index()

@bp.route('/mantra/<int:id>')
def mantra_detail(id):
    """咒語詳情頁"""
    mantra = Mantra.query.get_or_404(id)
    total_count = mantra.get_total_count()
    
    return render_template('mantra_detail.html',
                          title=mantra.name,
                          mantra=mantra,
                          total_count=total_count)

@bp.route('/profile')
@login_required
def user_profile():
    """用戶個人資料頁面"""
    # 獲取用戶的唸誦統計
    stats = db.session.query(
        MantraRecord.mantra_id,
        Mantra,
        func.sum(MantraRecord.count).label('count')
    ).join(Mantra).filter(
        MantraRecord.user_id == current_user.id
    ).group_by(MantraRecord.mantra_id).all()
    
    # 獲取用戶總唸誦次數
    total_count = sum(stat.count for stat in stats)
    
    # 獲取全球總唸誦次數
    global_count = MantraRecord.get_total_count()
    
    # 獲取用戶最近7天的唸誦記錄
    daily_records = MantraRecord.get_user_records_by_date(current_user.id, days=7)
    
    return render_template('user_profile.html', 
                           stats=stats, 
                           total_count=total_count, 
                           global_count=global_count,
                           daily_records=daily_records)

@bp.route('/record/<int:id>/edit', methods=['POST'])
@login_required
def edit_record(id):
    """編輯唸誦記錄"""
    record = MantraRecord.query.get_or_404(id)
    
    # 確保用戶只能編輯自己的記錄
    if record.user_id != current_user.id:
        flash('您沒有權限編輯此記錄', 'danger')
        return redirect(url_for('main.user_profile'))
    
    count = request.form.get('count', type=int)
    if count is not None and count >= 0:
        record.count = count
        db.session.commit()
        flash('記錄已更新', 'success')
    else:
        flash('無效的唸誦次數', 'danger')
    
    return redirect(url_for('main.user_profile'))
