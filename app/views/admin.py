@admin_required
def ceremony_calendar():
    """法會行事曆"""
    from datetime import datetime
    
    year = request.args.get('year', datetime.now().year, type=int)
    
    # 生成全年的法會安排
    yearly_schedule = {}
    
    for month in range(1, 13):
        assignments = Ceremony.assign_ceremonies_to_fridays(year, month)
        yearly_schedule[month] = assignments
    
    # 獲取所有法會
    ceremonies = Ceremony.query.filter_by(is_active=True).order_by(Ceremony.ceremony_order).all()
    
    return render_template('admin/ceremony_calendar.html', 
                         yearly_schedule=yearly_schedule,
                         ceremonies=ceremonies,
                         year=year) 