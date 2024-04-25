import sqlalchemy

from .db_session import SqlAlchemyBase

from flask_login import UserMixin
from sqlalchemy import orm
# from sqlalchemy_serializer import SerializerMixin


class Composer(SqlAlchemyBase, UserMixin):  # UserMixin, SerializerMixin
    __tablename__ = 'composers'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    composition = orm.relationship("Composition", back_populates='composer')
