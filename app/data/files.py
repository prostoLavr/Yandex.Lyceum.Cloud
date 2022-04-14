import sqlalchemy as sa
from .db_session import SqlAlchemyBase


class File(SqlAlchemyBase):
    __tablename__ = 'files'
    id = sa.Column(sa.Integer, sa.Sequence('seq_reg_id', start=1, increment=1), primary_key=True)
    date = sa.Column(sa.DateTime)
    is_open = sa.Column(sa.Boolean, default=False)
    name = sa.Column(sa.String, nullable=False)
    desc = sa.Column(sa.Text, default='')
    path = sa.Column(sa.String, nullable=False)

    def __repr__(self):
        return f'<File {self.id} {self.name}>'

