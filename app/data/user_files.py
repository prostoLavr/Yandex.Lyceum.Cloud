import sqlalchemy as sa
from .db_session import SqlAlchemyBase
from datetime import datetime
from . import db_session


class UserFiles(SqlAlchemyBase):
    __tablename__ = 'user_files'
    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    file_id = sa.Column(sa.Integer, sa.ForeignKey('files.id'))
