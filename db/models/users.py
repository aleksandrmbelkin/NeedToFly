from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from ..db_session import SqlAlchemyBase
import datetime
import sqlalchemy
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    # Создание таблицы users для БД
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String,
                              index=True, unique=True, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    favorites = orm.relationship("Favorites", back_populates='user')  # user - колонка отношений в таблице

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)
    # Хэширование/проверка пароля

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
