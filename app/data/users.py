import sqlalchemy as sa
from .db_session import SqlAlchemyBase
import hashlib
import os


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String, nullable=False)
    email = sa.Column(sa.String)
    salt = sa.Column(sa.LargeBinary, nullable=False)
    password = sa.Column(sa.LargeBinary, nullable=False)
    files = sa.Column(sa.Text)
    gives_files = sa.Column(sa.Text)

    def check_password(self, password):
        key_from_db, salt = self.password, self.salt
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000, dklen=128)
        return key_from_db == key

    def set_password(self, password):
        salt = os.urandom(32)
        self.salt = salt
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000, dklen=128)
        self.password = key

    def __repr__(self):
        return f'<User {self.id}>'
