import sqlalchemy as sa
from .db_session import SqlAlchemyBase
from datetime import datetime


class Friends(SqlAlchemyBase):
    __tablename__ = 'friends'
    id = sa.Column(sa.Integer, primary_key=True)
    sender_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    receiver_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    accept = sa.Column(sa.Boolean, default=False)