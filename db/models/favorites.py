from ..db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin
import datetime
import sqlalchemy
from sqlalchemy import orm


class Favorites(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'favorites'

    id = sqlalchemy.Column(sqlalchemy.Integer, 
                           primary_key=True, autoincrement=True)
    flight_number = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    date = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    user_id = sqlalchemy.Column(sqlalchemy.Integer, 
                                sqlalchemy.ForeignKey("users.id"))
    user = orm.relationship('User')