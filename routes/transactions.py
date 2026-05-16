from flask import Blueprint, render_template, redirect, url_for, flash, request, make_response
from flask_login import login_required, current_user
from models import db, Transaction, Category
from forms import TransactionForm
from datetime import datetime
import csv
import io

transactions_bp = Blueprint('transactions', __name__)

@transactions_bp.route('/transactions')
@login_required
def list_transactions():
    from forms import DeleteForm
    page = request.args.get('page', 1, type=int)
    query = Transaction.query.filter_by(user_id=current_user.id)

    category_id = request.args.get('category')
    txn_type = request.args.get('type')
    search = request.args.get('search', '')
    sort = request.args.get('sort', 'date')

    if category_id:
        query = query.filter_by(category_id=int(category_id))
    if txn_type:
        query = query.filter_by(type=txn_type)
    if search:
        query = query.filter(Transaction.description.ilike(f'%{search}%'))

    sort_map = {
        'date': Transaction.date.desc(),
        'amount': Transaction.amount.desc(),
        'category': Transaction.category_id.asc()
    }
    query = query.order_by(sort_map.get(sort, Transaction.date.desc()))
    transactions = query.paginate(page=page, per_page=20)
    categories = Category.query.filter_by(user_id=current_user.id).all()
    delete_form = DeleteForm()

    return render_template('transactions/list.html',
                           transactions=transactions,
                           categories=categories,
                           search=search,
                           sort=sort,
                           delete_form=delete_form)

@transactions_bp.route('/transactions/add', methods=['GET', 'POST'])
@login_required
def add_transaction():
    form = TransactionForm()
    form.category_id.choices = [(c.id, c.name) for c in
                                 Category.query.filter_by(user_id=current_user.id).all()]
    if form.validate_on_submit():
        txn = Transaction(
            user_id=current_user.id,
            amount=form.amount.data,
            description=form.description.data,
            category_id=form.category_id.data,
            date=form.date.data,
            type=form.type.data
        )
        db.session.add(txn)
        db.session.commit()
        flash('Transaction added!', 'success')
        return redirect(url_for('transactions.list_transactions'))
    return render_template('transactions/add.html', form=form)

@transactions_bp.route('/transactions/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_transaction(id):
    txn = Transaction.query.get_or_404(id)
    if txn.user_id != current_user.id:
        flash('Not allowed.', 'error')
        return redirect(url_for('transactions.list_transactions'))
    form = TransactionForm(obj=txn)
    form.category_id.choices = [(c.id, c.name) for c in
                                 Category.query.filter_by(user_id=current_user.id).all()]
    if form.validate_on_submit():
        txn.amount = form.amount.data
        txn.description = form.description.data
        txn.category_id = form.category_id.data
        txn.date = form.date.data
        txn.type = form.type.data
        db.session.commit()
        flash('Transaction updated!', 'success')
        return redirect(url_for('transactions.list_transactions'))
    return render_template('transactions/edit.html', form=form, txn=txn)

@transactions_bp.route('/transactions/delete/<int:id>', methods=['POST'])
@login_required
def delete_transaction(id):
    txn = Transaction.query.get_or_404(id)
    if txn.user_id != current_user.id:
        flash('Not allowed.', 'error')
        return redirect(url_for('transactions.list_transactions'))
    db.session.delete(txn)
    db.session.commit()
    flash('Transaction deleted.', 'success')
    return redirect(url_for('transactions.list_transactions'))

@transactions_bp.route('/transactions/export')
@login_required
def export_csv():
    query = Transaction.query.filter_by(user_id=current_user.id)
    start = request.args.get('start')
    end = request.args.get('end')
    category_id = request.args.get('category')

    if start:
        query = query.filter(Transaction.date >= start)
    if end:
        query = query.filter(Transaction.date <= end)
    if category_id:
        query = query.filter_by(category_id=int(category_id))

    transactions = query.order_by(Transaction.date.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Date', 'Description', 'Category', 'Type', 'Amount'])
    for t in transactions:
        cat = Category.query.get(t.category_id)
        writer.writerow([t.date, t.description,
                         cat.name if cat else '', t.type, t.amount])

    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=transactions.csv'
    response.headers['Content-Type'] = 'text/csv'
    return response