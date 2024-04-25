import datetime
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Result(SqlAlchemyBase):
    __tablename__ = 'results'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    quiz_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("quizzes.id"))
    student_answers = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    right_answers = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    taking_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                    default=datetime.datetime.now)
    scores = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    total_score = sqlalchemy.Column(sqlalchemy.Integer)

    user = orm.relationship('User')
    quiz = orm.relationship('Quiz')
