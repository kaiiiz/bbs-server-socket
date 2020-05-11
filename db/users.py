from sqlalchemy import Column
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import BIGINT, VARCHAR

from .base import Base

class Users(Base):
    __tablename__ = 'users'

    id = Column(BIGINT(), primary_key=True, autoincrement=True)
    username = Column(VARCHAR(255), nullable=False, unique=True)
    email = Column(VARCHAR(255), nullable=False)
    password = Column(VARCHAR(255), nullable=False)

    # 1-N relationship
    posts = relationship('Posts', cascade="all,delete", backref="author")
    comments = relationship('PostComments', cascade="all,delete", backref="user")
    boards = relationship('Boards', cascade="all,delete", backref="moderator")
