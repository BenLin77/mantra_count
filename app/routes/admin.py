from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_file
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.mantra import Mantra, MantraRecord
from app.models.ceremony import Ceremony
from app.forms.mantra import MantraCreateForm, MantraEditForm
from app.forms.ceremony import CeremonyCreateForm, CeremonyEditForm
from app.forms.calendar import CalendarForm
from app.utils.calendar_generator import CalendarGenerator
from functools import wraps
from sqlalchemy import func
from datetime import datetime, timedelta
import os
import tempfile

bp = Blueprint('admin', __name__)

def admin_required(f):
    """管理員權限裝飾器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('您沒有權限訪問此頁面', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/')
@login_required
@admin_required
def index():
    """管理員首頁"""
    users = User.query.all()
    mantras = Mantra.query.all()
    
    # 計算總唸誦次數
    total_count = db.session.query(func.sum(MantraRecord.count)).scalar() or 0
    
    # 獲取用戶數量
    user_count = User.query.count()
    
    # 獲取咒語數量
    mantra_count = Mantra.query.count()
    
    # 獲取唸誦次數最多的前5名用戶
    top_users = db.session.query(
        User.id.label('user_id'),
        User.username.label('user_name'),
        func.sum(MantraRecord.count).label('count')
    ).join(MantraRecord, User.id == MantraRecord.user_id
    ).group_by(User.id, User.username
    ).order_by(db.desc('count')
    ).limit(5).all()
    
    return render_template('admin/index.html', 
                          users=users, 
                          mantras=mantras, 
                          total_count=total_count,
                          user_count=user_count,
                          mantra_count=mantra_count,
                          top_users=top_users,
                          enumerate=enumerate)

@bp.route('/users')
@login_required
@admin_required
def users():
    """用戶管理頁面"""
    page = request.args.get('page', 1, type=int)
    users = User.query.paginate(page=page, per_page=10)
    
    # 獲取每個用戶的唸誦總數
    user_stats = []
    for user in users.items:
        count = db.session.query(func.sum(MantraRecord.count)).filter_by(user_id=user.id).scalar() or 0
        user_stats.append({
            'user': user,
            'count': count
        })
    
    return render_template('admin/users.html', users=users, user_stats=user_stats)

@bp.route('/user/<int:id>')
@login_required
@admin_required
def user_detail(id):
    """用戶詳情頁面"""
    user = User.query.get_or_404(id)
    
    # 獲取用戶的唸誦統計
    stats = db.session.query(
        MantraRecord.mantra_id,
        Mantra,
        func.sum(MantraRecord.count).label('count')
    ).join(Mantra).filter(
        MantraRecord.user_id == user.id
    ).group_by(MantraRecord.mantra_id).all()
    
    # 獲取用戶總唸誦次數
    total_count = sum(stat.count for stat in stats)
    
    # 獲取用戶最近的唸誦記錄
    recent_records = MantraRecord.query.filter_by(user_id=user.id).order_by(MantraRecord.record_date.desc()).limit(10).all()
    
    return render_template('admin/user_detail.html', 
                          user=user, 
                          stats=stats, 
                          total_count=total_count,
                          recent_records=recent_records,
                          MantraRecord=MantraRecord)

@bp.route('/mantras')
@login_required
@admin_required
def mantras():
    """咒語管理頁面"""
    page = request.args.get('page', 1, type=int)
    mantras = Mantra.query.paginate(
        page=page, 
        per_page=current_app.config['RECORDS_PER_PAGE'],
        error_out=False
    )
    
    return render_template('admin/mantras.html',
                          title='咒語管理',
                          mantras=mantras)

@bp.route('/mantra/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_mantra():
    """創建咒語頁面"""
    form = MantraCreateForm()
    
    if form.validate_on_submit():
        # 如果設置為預設咒語，需要將其他咒語的預設狀態取消
        if form.is_default.data:
            default_mantras = Mantra.query.filter_by(is_default=True).all()
            for mantra in default_mantras:
                mantra.is_default = False
        
        mantra = Mantra(
            name=form.name.data,
            sanskrit=form.sanskrit.data,
            chinese=form.chinese.data,
            description=form.description.data,
            benefits=form.benefits.data,
            is_default=form.is_default.data
        )
        
        db.session.add(mantra)
        db.session.commit()
        
        flash(f'咒語 {mantra.name} 創建成功！', 'success')
        return redirect(url_for('admin.mantras'))
    
    return render_template('admin/create_mantra.html',
                          title='創建咒語',
                          form=form)

@bp.route('/mantra/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_mantra(id):
    """編輯咒語頁面"""
    mantra = Mantra.query.get_or_404(id)
    form = MantraEditForm()
    
    if form.validate_on_submit():
        # 如果設置為預設咒語，需要將其他咒語的預設狀態取消
        if form.is_default.data and not mantra.is_default:
            default_mantras = Mantra.query.filter_by(is_default=True).all()
            for m in default_mantras:
                m.is_default = False
        
        mantra.name = form.name.data
        mantra.sanskrit = form.sanskrit.data
        mantra.chinese = form.chinese.data
        mantra.description = form.description.data
        mantra.benefits = form.benefits.data
        mantra.is_default = form.is_default.data
        
        db.session.commit()
        
        flash(f'咒語 {mantra.name} 更新成功！', 'success')
        return redirect(url_for('admin.mantras'))
    
    # 預填表單數據
    form.name.data = mantra.name
    form.sanskrit.data = mantra.sanskrit
    form.chinese.data = mantra.chinese
    form.description.data = mantra.description
    form.benefits.data = mantra.benefits
    form.is_default.data = mantra.is_default
    
    return render_template('admin/edit_mantra.html',
                          title=f'編輯咒語 - {mantra.name}',
                          form=form,
                          mantra=mantra)

@bp.route('/mantra/<int:id>/delete')
@login_required
@admin_required
def delete_mantra(id):
    """刪除咒語"""
    mantra = Mantra.query.get_or_404(id)
    
    # 不允許刪除預設咒語
    if mantra.is_default:
        flash('不能刪除預設咒語', 'danger')
        return redirect(url_for('admin.mantras'))
    
    name = mantra.name
    
    # 刪除相關的記錄
    MantraRecord.query.filter_by(mantra_id=id).delete()
    
    # 刪除咒語
    db.session.delete(mantra)
    db.session.commit()
    
    flash(f'咒語 {name} 已刪除', 'success')
    return redirect(url_for('admin.mantras'))

@bp.route('/statistics')
@login_required
@admin_required
def statistics():
    """統計數據頁面"""
    # 獲取全球總唸誦次數
    total_count = MantraRecord.get_total_count()
    
    # 獲取咒語統計
    mantra_stats = db.session.query(
        Mantra,
        func.sum(MantraRecord.count).label('count')
    ).join(MantraRecord).group_by(Mantra.id).all()
    
    # 獲取用戶統計（按唸誦次數排序）
    user_stats = db.session.query(
        User,
        func.sum(MantraRecord.count).label('count')
    ).join(MantraRecord).group_by(User.id).order_by(func.sum(MantraRecord.count).desc()).all()
    
    # 獲取每日統計（最近30天）
    today = datetime.utcnow().date()
    start_date = today - timedelta(days=29)
    daily_stats = db.session.query(
        MantraRecord.record_date,
        func.sum(MantraRecord.count).label('count')
    ).filter(
        MantraRecord.record_date >= start_date,
        MantraRecord.record_date <= today
    ).group_by(MantraRecord.record_date).order_by(MantraRecord.record_date).all()
    
    return render_template('admin/statistics.html', 
                          total_count=total_count,
                          mantra_stats=mantra_stats,
                          user_stats=user_stats,
                          daily_stats=daily_stats)

@bp.route('/calendar', methods=['GET', 'POST'])
@login_required
@admin_required
def calendar():
    """行事曆生成頁面"""
    form = CalendarForm()
    
    if form.validate_on_submit():
        year = form.year.data
        
        # 創建臨時文件
        temp_dir = tempfile.gettempdir()
        docx_filename = os.path.join(temp_dir, f'行事曆_{year-1911}年.docx')
        
        # 生成行事曆文件
        result_filename = CalendarGenerator.create_calendar_docx(year, docx_filename)
        
        # 檢查返回的檔案類型
        if result_filename.endswith('.json'):
            # 如果是 JSON 檔案，設置相應的 MIME 類型
            mime_type = 'application/json'
            download_name = f'行事曆_{year-1911}年.json'
        else:
            # 如果是 DOCX 檔案，設置相應的 MIME 類型
            mime_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            download_name = f'行事曆_{year-1911}年.docx'
        
        # 發送文件
        return send_file(
            result_filename,
            as_attachment=True,
            download_name=download_name,
            mimetype=mime_type
        )
    
    return render_template('admin/calendar.html', form=form)

@bp.route('/ceremonies')
@login_required
@admin_required
def ceremonies():
    """法會管理頁面"""
    page = request.args.get('page', 1, type=int)
    ceremonies = Ceremony.query.order_by(Ceremony.created_at.desc()).paginate(
        page=page, 
        per_page=current_app.config['RECORDS_PER_PAGE'],
        error_out=False
    )
    
    return render_template('admin/ceremonies.html',
                          title='法會管理',
                          ceremonies=ceremonies)

@bp.route('/ceremony/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_ceremony():
    """創建法會頁面"""
    form = CeremonyCreateForm()
    
    if form.validate_on_submit():
        ceremony = Ceremony(
            name=form.name.data,
            description=form.description.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            is_active=form.is_active.data
        )
        
        db.session.add(ceremony)
        db.session.commit()
        
        flash(f'法會 {ceremony.name} 創建成功！', 'success')
        return redirect(url_for('admin.ceremonies'))
    
    return render_template('admin/create_ceremony.html',
                          title='創建法會',
                          form=form)

@bp.route('/ceremony/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_ceremony(id):
    """編輯法會頁面"""
    ceremony = Ceremony.query.get_or_404(id)
    form = CeremonyEditForm()
    
    if form.validate_on_submit():
        ceremony.name = form.name.data
        ceremony.description = form.description.data
        ceremony.start_date = form.start_date.data
        ceremony.end_date = form.end_date.data
        ceremony.is_active = form.is_active.data
        
        db.session.commit()
        
        flash(f'法會 {ceremony.name} 更新成功！', 'success')
        return redirect(url_for('admin.ceremonies'))
    
    # 預填表單數據
    form.name.data = ceremony.name
    form.description.data = ceremony.description
    form.start_date.data = ceremony.start_date
    form.end_date.data = ceremony.end_date
    form.is_active.data = ceremony.is_active
    
    return render_template('admin/edit_ceremony.html',
                          title=f'編輯法會 - {ceremony.name}',
                          form=form,
                          ceremony=ceremony)

@bp.route('/ceremony/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_ceremony(id):
    """刪除法會"""
    ceremony = Ceremony.query.get_or_404(id)
    
    # 檢查是否有相關的唸誦記錄
    if ceremony.records.count() > 0:
        flash(f'無法刪除法會 {ceremony.name}，因為已有相關的唸誦記錄', 'error')
        return redirect(url_for('admin.ceremonies'))
    
    ceremony_name = ceremony.name
    db.session.delete(ceremony)
    db.session.commit()
    
    flash(f'法會 {ceremony_name} 已刪除', 'success')
    return redirect(url_for('admin.ceremonies'))

@bp.route('/ceremony_calendar')
@login_required
@admin_required
def ceremony_calendar():
    """法會行事曆"""
    year = request.args.get('year', datetime.now().year, type=int)
    
    # 生成全年的法會安排
    yearly_schedule = {}
    
    for month in range(1, 13):
        assignments = Ceremony.assign_ceremonies_to_fridays(year, month)
        yearly_schedule[month] = assignments
    
    # 獲取所有法會
    ceremonies = Ceremony.query.filter_by(is_active=True).order_by(Ceremony.ceremony_order).all()
    
    return render_template('admin/ceremony_calendar_simple.html', 
                         yearly_schedule=yearly_schedule,
                         ceremonies=ceremonies,
                         year=year)
