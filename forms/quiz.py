from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, TextAreaField, BooleanField
from wtforms.validators import DataRequired


class QuizForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    content = TextAreaField('Введите номера произведений через ";" без пробелов. Пример: 1;2;3;4',
                            validators=[DataRequired()])
    is_private = BooleanField('Сделать приватной')
    time_limit = IntegerField('Временное ограничение (в минутах)', validators=[DataRequired()])
    submit = SubmitField('Создать')


class FindCompositionForm(FlaskForm):
    find_composition = StringField('Поиск по названию произведения')
    find_composer = StringField('Поиск по фамилии композитора')
    submit = SubmitField('Поиск викторины')