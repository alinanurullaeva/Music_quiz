import datetime
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Composition(SqlAlchemyBase):
    __tablename__ = 'compositions'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                                primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    composer_id = sqlalchemy.Column(sqlalchemy.Integer,
                                    sqlalchemy.ForeignKey("composers.id"))
    composer = orm.relationship('Composer')