from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, EmailField, IntegerField
from wtforms.validators import DataRequired


class SelectForm(FlaskForm):
    number = IntegerField('Номер викторины', validators=[DataRequired()])
    submit = SubmitField('Выбрать викторину')


class FindForm(FlaskForm):
    find_quiz = StringField('Поиск по названию викторины')
    find_user_name = StringField('Поиск по имени создателя')
    find_user_surname = StringField('Поиск по фамилии создателя')
    submit = SubmitField('Поиск викторины')


class MyQuiz(FlaskForm):
    find_quiz = StringField('Поиск по названию викторины')
    submit = SubmitField('Поиск викторины')
