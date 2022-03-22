import sqlalchemy as sa
from flask_login import UserMixin
from .db_session import SqlAlchemyBase
import hashlib
import os


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True, index=True)
    name = sa.Column(sa.String, nullable=False, index=True)
    email = sa.Column(sa.String)
    salt = sa.Column(sa.LargeBinary, nullable=False)
    password = sa.Column(sa.LargeBinary, nullable=False)
    files = sa.Column(sa.Text, nullable=False, default='')  # User's files
    given_files = sa.Column(sa.Text)  # Files that was given by other users

    def check_password(self, password):
        key_from_db, salt = self.password, self.salt
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000, dklen=128)
        return key_from_db == key

    def with_password(self, password):
        salt = os.urandom(32)
        self.salt = salt
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000, dklen=128)
        self.password = key
        return self

    def get_files(self):
        if not self.files:
            return []
        return self.files[:-1].split(';')

    def get_given_files(self):
        if not self.given_files:
            return []
        return self.given_files[:-1].split(';')

    def add_file(self, file_id):
        self.files += (str(file_id) + ';')

    def add_given_file(self, file_id):
        self.given_files += (str(file_id) + ';')

    def remove_file(self, file_id):
        files = self.get_files()
        files.remove(str(file_id))
        ';'.join(files) + ';'

    def remove_given_file(self, file_id):
        given_files = self.get_given_files()
        given_files.remove(str(file_id))
        ';'.join(given_files) + ';'

    def __repr__(self):
        return f'<User {self.id}>'
