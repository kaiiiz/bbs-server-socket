from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import BIGINT, VARCHAR
from dataclasses import dataclass

from .base import Base

@dataclass
class Boards(Base):
    __tablename__ = 'boards'

    id: int = Column(BIGINT(), primary_key=True, autoincrement=True)
    name: str = Column(VARCHAR(255), nullable=False, unique=True)

    # 1-N relationship
    posts: list = relationship('Posts', cascade="all,delete", backref='board')

    # FK
    moderator_id: int = Column(BIGINT(), ForeignKey('users.id'), nullable=False)
