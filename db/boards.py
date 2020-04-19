from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import BIGINT, VARCHAR

from .base import Base


class Boards(Base):
    __tablename__ = 'boards'

    id = Column(BIGINT(), primary_key=True, autoincrement=True)
    name = Column(VARCHAR(255), nullable=False, unique=True)

    # relation
    moderator_id = Column(BIGINT(), ForeignKey('users.id'))
    moderator = relationship('Users')
