from sqlalchemy import Column
from sqlalchemy.dialects.mysql import BIGINT, VARCHAR

from .base import Base

class Users(Base):
    __tablename__ = 'users'

    uid = Column(BIGINT(), primary_key=True, autoincrement=True)
    username = Column(VARCHAR(255), nullable=False, unique=True)
    email = Column(VARCHAR(255), nullable=False)
    password = Column(VARCHAR(255), nullable=False)
