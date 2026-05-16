from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, Category, Transaction
from forms import CategoryForm

categories_bp = Blueprint('categories', __name__)

@categories_bp.route('/categories')
@login_required
def index():
    from forms import DeleteForm
    categories = Category.query.filter_by(user_id=current_user.id).all()
    form = CategoryForm()
    delete_form = DeleteForm()
    return render_template('categories.html',
                           categories=categories,
                           form=form,
                           delete_form=delete_form)

@categories_bp.route('/categories/add', methods=['POST'])
@login_required
def add_category():
    form = CategoryForm()
    if form.validate_on_submit():
        cat = Category(
            user_id=current_user.id,
            name=form.name.data,
            color=form.color.data,
            is_default=False
        )
        db.session.add(cat)
        db.session.commit()
        flash('Category added!', 'success')
    return redirect(url_for('categories.index'))

@categories_bp.route('/categories/edit/<int:id>', methods=['POST'])
@login_required
def edit_category(id):
    cat = Category.query.get_or_404(id)
    if cat.user_id != current_user.id or cat.is_default:
        flash('Cannot edit this category.', 'error')
        return redirect(url_for('categories.index'))
    cat.name = request.form.get('name', cat.name)
    cat.color = request.form.get('color', cat.color)
    db.session.commit()
    flash('Category updated!', 'success')
    return redirect(url_for('categories.index'))

@categories_bp.route('/categories/delete/<int:id>', methods=['POST'])
@login_required
def delete_category(id):
    cat = Category.query.get_or_404(id)
    if cat.user_id != current_user.id or cat.is_default:
        flash('Cannot delete this category.', 'error')
        return redirect(url_for('categories.index'))
    if Transaction.query.filter_by(category_id=id).count() > 0:
        flash('Cannot delete — transactions exist with this category.', 'error')
        return redirect(url_for('categories.index'))
    db.session.delete(cat)
    db.session.commit()
    flash('Category deleted.', 'success')
    return redirect(url_for('categories.index'))