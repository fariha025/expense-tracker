from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from models import db, User, Transaction, Category, Budget
from forms import SettingsForm, ChangePasswordForm

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def index():
    settings_form = SettingsForm(obj=current_user)
    password_form = ChangePasswordForm()

    if 'save_settings' in request.form and settings_form.validate_on_submit():
        current_user.display_name = settings_form.display_name.data
        current_user.currency = settings_form.currency.data
        db.session.commit()
        flash('Settings updated!', 'success')
        return redirect(url_for('settings.index'))

    if 'change_password' in request.form and password_form.validate_on_submit():
        if check_password_hash(current_user.password_hash, password_form.current_password.data):
            current_user.password_hash = generate_password_hash(password_form.new_password.data)
            db.session.commit()
            flash('Password changed successfully!', 'success')
        else:
            flash('Current password is incorrect.', 'error')
        return redirect(url_for('settings.index'))

    return render_template('settings.html',
                           settings_form=settings_form,
                           password_form=password_form)

@settings_bp.route('/settings/delete', methods=['POST'])
@login_required
def delete_account():
    user_id = current_user.id
    Transaction.query.filter_by(user_id=user_id).delete()
    Budget.query.filter_by(user_id=user_id).delete()
    Category.query.filter_by(user_id=user_id).delete()
    user = User.query.get(user_id)
    logout_user()
    db.session.delete(user)
    db.session.commit()
    flash('Account deleted.', 'success')
    return redirect(url_for('auth.login'))