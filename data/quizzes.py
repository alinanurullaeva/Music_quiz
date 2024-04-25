import datetime
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Quiz(SqlAlchemyBase):
    __tablename__ = 'quizzes'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    is_private = sqlalchemy.Column(sqlalchemy.Boolean, default=True)

    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    time_limit = sqlalchemy.Column(sqlalchemy.Integer)  # считаться и вводиться будет в минутах
    user = orm.relationship('User')
