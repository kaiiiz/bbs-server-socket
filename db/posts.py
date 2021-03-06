from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import BIGINT, VARCHAR, TEXT, TIMESTAMP
from dataclasses import dataclass
import datetime

from .base import Base


@dataclass
class Posts(Base):
    __tablename__ = 'posts'

    id: int = Column(BIGINT(), primary_key=True, autoincrement=True)
    title: str = Column(TEXT)
    timestamp: datetime.datetime = Column(TIMESTAMP)
    object_name: str = Column(VARCHAR(255))

    # FK
    board_id = Column(BIGINT(), ForeignKey('boards.id'), nullable=False)
    author_id = Column(BIGINT(), ForeignKey('users.id'), nullable=False)
