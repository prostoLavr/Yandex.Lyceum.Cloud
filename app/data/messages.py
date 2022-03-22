import sqlalchemy as sa
from .db_session import SqlAlchemyBase
from datetime import datetime


class Message(SqlAlchemyBase):
    __tablename__ = 'messages'
    file_id = sa.Column(sa.Integer, primary_key=True)
    sent_date = sa.Column(sa.DateTime, default=datetime.utcnow)
    text = sa.Column(sa.Text, nullable=False)
    sender_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    receiver_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))


