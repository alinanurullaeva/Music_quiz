from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, TextAreaField, BooleanField
# from wtforms.validators import DataRequired


class StartForm(FlaskForm):
    submit = SubmitField('Начать')


class TestForm(FlaskForm):
    composer = StringField('Композитор')
    composition = StringField('Название произведения')
    submit = SubmitField('Начать')