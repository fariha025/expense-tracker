# routes/auth.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Category
from forms import SignupForm, LoginForm

auth_bp = Blueprint('auth', __name__)

DEFAULT_CATEGORIES = [
    ('Food', '#FF6384'), ('Transport', '#36A2EB'), ('Housing', '#FFCE56'),
    ('Utilities', '#4BC0C0'), ('Entertainment', '#9966FF'), ('Shopping', '#FF9F40'),
    ('Health', '#FF6384'), ('Education', '#C9CBCF'), ('Other', '#999999')
]

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        # Check email not already used
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered.', 'error')
            return redirect(url_for('auth.signup'))
        user = User(
            email=form.email.data,
            display_name=form.display_name.data,
            password_hash=generate_password_hash(form.password.data)
        )
        db.session.add(user)
        db.session.flush()  # Get user.id before commit
        # Seed default categories for this user
        for name, color in DEFAULT_CATEGORIES:
            db.session.add(Category(user_id=user.id, name=name,
                                    color=color, is_default=True))
        db.session.commit()
        login_user(user)
        return redirect(url_for('dashboard.index'))
    return render_template('signup.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            return redirect(url_for('dashboard.index'))
        flash('Invalid email or password.', 'error')
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
