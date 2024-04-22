from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, EmailField
from wtforms.validators import DataRequired


class ChangeForm(FlaskForm):
    name = StringField('Имя')
    surname = StringField('Фамилия')
    submit = SubmitField('Изменить')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Введите старый пароль', validators=[DataRequired()])
    new_password = PasswordField('Введите новый пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    submit = SubmitField('Изменить пароль')