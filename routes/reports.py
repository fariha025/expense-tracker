from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from models import db, Transaction, Category
from datetime import datetime
from sqlalchemy import func

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/reports')
@login_required
def index():
    today = datetime.today()
    month = int(request.args.get('month', today.month))
    year = int(request.args.get('year', today.year))

    # All expense transactions for selected month
    monthly_txns = Transaction.query.filter(
        Transaction.user_id == current_user.id,
        Transaction.type == 'expense',
        func.strftime('%m', Transaction.date) == f'{month:02d}',
        func.strftime('%Y', Transaction.date) == str(year)
    ).all()

    # Pie chart: expenses by category
    cat_data = {}
    cat_colors = {}
    for t in monthly_txns:
        cat = Category.query.get(t.category_id)
        name = cat.name if cat else 'Other'
        color = cat.color if cat else '#999999'
        cat_data[name] = cat_data.get(name, 0) + t.amount
        cat_colors[name] = color

    total_expenses = sum(cat_data.values())

    # Category breakdown table with percentages
    cat_breakdown = []
    for name, amount in cat_data.items():
        pct = round((amount / total_expenses) * 100, 1) if total_expenses > 0 else 0
        cat_breakdown.append({
            'name': name,
            'amount': round(amount, 2),
            'percentage': pct,
            'color': cat_colors.get(name, '#999999')
        })
    cat_breakdown.sort(key=lambda x: x['amount'], reverse=True)

    # Bar chart: income vs expenses for last 6 months
    months_labels = []
    income_data = []
    expense_data = []

    for i in range(5, -1, -1):
        m = month - i
        y = year
        while m <= 0:
            m += 12
            y -= 1
        label = datetime(y, m, 1).strftime('%b %Y')
        months_labels.append(label)

        inc = db.session.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == current_user.id,
            Transaction.type == 'income',
            func.strftime('%m', Transaction.date) == f'{m:02d}',
            func.strftime('%Y', Transaction.date) == str(y)
        ).scalar() or 0

        exp = db.session.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == current_user.id,
            Transaction.type == 'expense',
            func.strftime('%m', Transaction.date) == f'{m:02d}',
            func.strftime('%Y', Transaction.date) == str(y)
        ).scalar() or 0

        income_data.append(round(inc, 2))
        expense_data.append(round(exp, 2))

    # Line chart: spending trend over last 12 months
    trend_labels = []
    trend_data = []
    for i in range(11, -1, -1):
        m = month - i
        y = year
        while m <= 0:
            m += 12
            y -= 1
        label = datetime(y, m, 1).strftime('%b %Y')
        trend_labels.append(label)
        exp = db.session.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == current_user.id,
            Transaction.type == 'expense',
            func.strftime('%m', Transaction.date) == f'{m:02d}',
            func.strftime('%Y', Transaction.date) == str(y)
        ).scalar() or 0
        trend_data.append(round(exp, 2))

    # Month selector options
    month_options = []
    for i in range(11, -1, -1):
        m = today.month - i
        y = today.year
        while m <= 0:
            m += 12
            y -= 1
        month_options.append({
            'month': m,
            'year': y,
            'label': datetime(y, m, 1).strftime('%B %Y')
        })

    return render_template('reports.html',
                           cat_data=cat_data,
                           cat_colors=list(cat_colors.values()),
                           cat_breakdown=cat_breakdown,
                           total_expenses=round(total_expenses, 2),
                           months_labels=months_labels,
                           income_data=income_data,
                           expense_data=expense_data,
                           trend_labels=trend_labels,
                           trend_data=trend_data,
                           month_options=month_options,
                           selected_month=month,
                           selected_year=year)