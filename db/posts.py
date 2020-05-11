from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import BIGINT, VARCHAR, TEXT, TIMESTAMP

from .base import Base


class Posts(Base):
    __tablename__ = 'posts'

    id = Column(BIGINT(), primary_key=True, autoincrement=True)
    title = Column(TEXT)
    content = Column(TEXT)
    timestamp = Column(TIMESTAMP)

    # 1-N relationship
    comments = relationship('PostComments', cascade="all,delete", backref='post')

    # FK
    board_id = Column(BIGINT(), ForeignKey('boards.id'), nullable=False)
    author_id = Column(BIGINT(), ForeignKey('users.id'), nullable=False)


class PostComments(Base):
    __tablename__ = 'post_comments'

    id = Column(BIGINT(), primary_key=True, autoincrement=True)
    content = Column(TEXT)

    # FK
    post_id = Column(BIGINT(), ForeignKey('posts.id'), nullable=False)
    user_id = Column(BIGINT(), ForeignKey('users.id'), nullable=False)
