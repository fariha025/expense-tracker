from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, Budget, Category, Transaction
from forms import BudgetForm
from datetime import datetime

budgets_bp = Blueprint('budgets', __name__)

@budgets_bp.route('/budgets', methods=['GET', 'POST'])
@login_required
def index():
    today = datetime.today()
    month = int(request.args.get('month', today.month))
    year = int(request.args.get('year', today.year))

    categories = Category.query.filter_by(user_id=current_user.id).all()

    # Get overall budget
    overall_budget = Budget.query.filter_by(
        user_id=current_user.id,
        month=month, year=year,
        category_id=None
    ).first()

    # Get per-category budgets
    cat_budgets = Budget.query.filter(
        Budget.user_id == current_user.id,
        Budget.month == month,
        Budget.year == year,
        Budget.category_id != None
    ).all()

    # Calculate spending per category this month
    from sqlalchemy import func
    spending = {}
    for cat in categories:
        total = db.session.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == current_user.id,
            Transaction.category_id == cat.id,
            Transaction.type == 'expense',
            func.strftime('%m', Transaction.date) == f'{month:02d}',
            func.strftime('%Y', Transaction.date) == str(year)
        ).scalar() or 0
        spending[cat.id] = total

    # Total expenses this month
    total_expenses = sum(spending.values())
    overall_pct = 0
    if overall_budget and overall_budget.amount > 0:
        overall_pct = round((total_expenses / overall_budget.amount) * 100, 1)

    form = BudgetForm()
    form.category_id.choices = [(0, 'Overall (no category)')] + \
                                [(c.id, c.name) for c in categories]
    current_year = today.year
    form.year.choices = [(y, y) for y in range(current_year - 1, current_year + 3)]

    if form.validate_on_submit():
        cat_id = form.category_id.data if form.category_id.data != 0 else None
        # Upsert: update if exists, create if not
        existing = Budget.query.filter_by(
            user_id=current_user.id,
            month=form.month.data,
            year=form.year.data,
            category_id=cat_id
        ).first()
        if existing:
            existing.amount = form.amount.data
        else:
            new_budget = Budget(
                user_id=current_user.id,
                category_id=cat_id,
                amount=form.amount.data,
                month=form.month.data,
                year=form.year.data
            )
            db.session.add(new_budget)
        db.session.commit()
        flash('Budget saved!', 'success')
        return redirect(url_for('budgets.index'))

    return render_template('budgets.html',
                           form=form,
                           overall_budget=overall_budget,
                           overall_pct=overall_pct,
                           cat_budgets=cat_budgets,
                           categories=categories,
                           spending=spending,
                           total_expenses=total_expenses,
                           month=month,
                           year=year)