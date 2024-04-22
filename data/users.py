import datetime
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase

from flask_login import UserMixin
'''from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin'''

from werkzeug.security import generate_password_hash, check_password_hash


class User(SqlAlchemyBase, UserMixin): # UserMixin, SerializerMixin
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    position = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)

    quiz = orm.relationship("Quiz", back_populates='user')

    def __repr__(self):
        return f'<User> {self.id} {self.surname} {self.name}'

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)