from sqlalchemy import Column
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import BIGINT, VARCHAR
from dataclasses import dataclass

from .base import Base


@dataclass
class Users(Base):
    __tablename__ = 'users'

    id: int = Column(BIGINT(), primary_key=True, autoincrement=True)
    username: str = Column(VARCHAR(255), nullable=False, unique=True)
    email: str = Column(VARCHAR(255), nullable=False)
    password: str = Column(VARCHAR(255), nullable=False)
    bucket_name: str = Column(VARCHAR(255), nullable=False)

    # 1-N relationship
    posts: list = relationship('Posts', cascade="all,delete", backref="author")
    boards: list = relationship('Boards', cascade="all,delete", backref="moderator")
    receive_mails: list = relationship('Mails', foreign_keys='Mails.receiver_id', cascade="all,delete", backref="receiver")
    send_mails: list = relationship('Mails', foreign_keys='Mails.sender_id', cascade="all,delete", backref="sender")
