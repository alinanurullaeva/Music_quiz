from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, TextAreaField
from wtforms.validators import DataRequired


class QuizForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    content = TextAreaField('Содержимое', validators=[DataRequired()])
    is_private = StringField('Статус', validators=[DataRequired()])
    time_limit = IntegerField('Временное ограничение (в минутах)', validators=[DataRequired()])
    submit = SubmitField('Создать')