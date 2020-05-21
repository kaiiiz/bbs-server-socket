from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import BIGINT, VARCHAR, TEXT, TIMESTAMP
from dataclasses import dataclass
import datetime

from .base import Base


@dataclass
class Mails(Base):
    __tablename__ = 'mails'

    id: int = Column(BIGINT(), primary_key=True, autoincrement=True)
    subject: str = Column(TEXT)
    timestamp: datetime.datetime = Column(TIMESTAMP)
    object_name: str = Column(VARCHAR(255))

    # FK
    receiver_id = Column(BIGINT(), ForeignKey('users.id'), nullable=False)
    sender_id = Column(BIGINT(), ForeignKey('users.id'), nullable=False)
