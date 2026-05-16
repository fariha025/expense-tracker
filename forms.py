# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FloatField, \
    SelectField, DateField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class SignupForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    display_name = StringField('Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm = PasswordField('Confirm', validators=[EqualTo('password')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

class TransactionForm(FlaskForm):
    amount = FloatField('Amount', validators=[DataRequired()])
    description = StringField('Description')
    category_id = SelectField('Category', coerce=int)
    date = DateField('Date', validators=[DataRequired()])
    type = SelectField('Type', choices=[('income','Income'),('expense','Expense')])
    submit = SubmitField('Save')

class BudgetForm(FlaskForm):
    amount = FloatField('Amount', validators=[DataRequired()])
    month = SelectField('Month', coerce=int, choices=[(i,i) for i in range(1,13)])
    year = SelectField('Year', coerce=int)
    category_id = SelectField('Category (optional)', coerce=int)
    submit = SubmitField('Set Budget')

class CategoryForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    color = StringField('Color', default='#2E75B6')
    submit = SubmitField('Save')

class SettingsForm(FlaskForm):
    display_name = StringField('Display Name')
    currency = SelectField('Currency',
        choices=[('BHD','BHD'),('USD','USD'),('SAR','SAR'),('EUR','EUR')])
    submit = SubmitField('Save Changes')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm = PasswordField('Confirm', validators=[EqualTo('new_password')])
    submit = SubmitField('Change Password')

class DeleteForm(FlaskForm):
    pass