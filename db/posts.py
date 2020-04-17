from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import BIGINT, VARCHAR, TEXT

from .base import Base


class Posts(Base):
    __tablename__ = 'posts'

    id = Column(BIGINT(), primary_key=True, autoincrement=True)
    name = Column(VARCHAR(255), nullable=False, unique=True)
    title = Column(TEXT)
    content = Column(TEXT)

    # relation
    board_id = Column(BIGINT(), ForeignKey('boards.id'))
    board = relationship('Boards')
    user_id = Column(BIGINT(), ForeignKey('users.id'))
    user = relationship('Users')


class PostComments(Base):
    __tablename__ = 'post_comments'

    id = Column(BIGINT(), primary_key=True, autoincrement=True)
    content = Column(TEXT)

    # relation
    post_id = Column(BIGINT(), ForeignKey('posts.id'))
    post = relationship('Posts')
    user_id = Column(BIGINT(), ForeignKey('users.id'))
    user = relationship('Users')
