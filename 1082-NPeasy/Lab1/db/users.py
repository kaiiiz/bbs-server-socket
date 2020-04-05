from sqlalchemy import Column
from sqlalchemy.dialects.mysql import BIGINT, TEXT

from .base import Base

class Users(Base):
    __tablename__ = 'users'

    uid = Column(BIGINT(), primary_key=True, autoincrement=True)
    username = Column(TEXT(), nullable=False, unique=True)
    email = Column(TEXT(), nullable=False)
    password = Column(TEXT(), nullable=False)
