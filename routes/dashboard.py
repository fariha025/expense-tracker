from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import db, Transaction, Budget, Category
from datetime import date
from sqlalchemy import func
import calendar

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    today = date.today()
    month = today.month
    year = today.year

    # All transactions this month for this user
    monthly_txns = Transaction.query.filter(
        Transaction.user_id == current_user.id,
        func.strftime('%m', Transaction.date) == f'{month:02d}',
        func.strftime('%Y', Transaction.date) == str(year)
    ).all()

    total_income = sum(t.amount for t in monthly_txns if t.type == 'income')
    total_expenses = sum(t.amount for t in monthly_txns if t.type == 'expense')
    net_balance = total_income - total_expenses

    # Pie chart: expenses by category
    cat_data = {}
    cat_colors = {}
    for t in monthly_txns:
        if t.type == 'expense':
            cat = Category.query.get(t.category_id)
            name = cat.name if cat else 'Other'
            color = cat.color if cat else '#999999'
            cat_data[name] = cat_data.get(name, 0) + t.amount
            cat_colors[name] = color

    # Bar chart: daily spending
    days_in_month = calendar.monthrange(year, month)[1]
    daily_data = {d: 0 for d in range(1, days_in_month + 1)}
    for t in monthly_txns:
        if t.type == 'expense':
            daily_data[t.date.day] += t.amount

    # Budget progress
    budget = Budget.query.filter_by(
        user_id=current_user.id,
        month=month,
        year=year,
        category_id=None
    ).first()

    budget_pct = 0
    if budget and budget.amount > 0:
        budget_pct = round((total_expenses / budget.amount) * 100, 1)

    # 5 most recent transactions
    recent = Transaction.query.filter_by(user_id=current_user.id)\
        .order_by(Transaction.date.desc()).limit(5).all()

    return render_template('dashboard.html',
        total_income=round(total_income, 2),
        total_expenses=round(total_expenses, 2),
        net_balance=round(net_balance, 2),
        cat_data=cat_data,
        cat_colors=list(cat_colors.values()),
        daily_data=daily_data,
        budget=budget,
        budget_pct=budget_pct,
        recent=recent,
        month=month,
        year=year
    )