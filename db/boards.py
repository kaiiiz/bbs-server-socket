from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import BIGINT, VARCHAR

from .base import Base


class Boards(Base):
    __tablename__ = 'boards'

    id = Column(BIGINT(), primary_key=True, autoincrement=True)
    name = Column(VARCHAR(255), nullable=False, unique=True)

    # 1-N relationship
    posts = relationship('Posts', cascade="all,delete", backref='board')

    # FK
    moderator_id = Column(BIGINT(), ForeignKey('users.id'), nullable=False)
