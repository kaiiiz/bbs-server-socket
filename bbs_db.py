from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.users import Users
from db.boards import Boards
from db.posts import Posts, PostComments

from constant import DB_HOST, DB_PORT, DB_USERNAME, DB_PWD

from datetime import datetime

Session = sessionmaker()


class BBS_DB_BASE:
    def __init__(self, host, port, username, pwd):
        self.engine = self.get_engine(host, port, username, pwd)
        self.create_table(self.engine)
        self.session = Session(bind=self.engine)

    def get_engine(self, host, port, username, pwd):
        engine = create_engine(f"mysql://{username}:{pwd}@{host}:{port}")
        engine.execute('CREATE DATABASE IF NOT EXISTS bbs;')
        return create_engine(f"mysql://{username}:{pwd}@{host}:{port}/bbs")

    def create_table(self, engine):
        Users.__table__.create(bind=engine, checkfirst=True)
        Boards.__table__.create(bind=engine, checkfirst=True)
        Posts.__table__.create(bind=engine, checkfirst=True)
        PostComments.__table__.create(bind=engine, checkfirst=True)


class BBS_DB_Return:
    def __init__(self, success, message, data=None):
        self.success = success
        self.data = data
        self.message = message + '\n'


class BBS_DB(BBS_DB_BASE):
    def create_user(self, username, email, password):
        user = self.session.query(Users).filter_by(username=username).one_or_none()

        if user:
            return BBS_DB_Return(False, "Username is already use.")

        new_user = Users(
            username=username,
            email=email,
            password=password,
        )
        self.session.add(new_user)
        self.session.commit()
        return BBS_DB_Return(True, "Register successfull.")

    def login(self, username, password):
        user = self.session.query(Users).filter_by(username=username).one_or_none()

        if user is None or user.password != password:
            return BBS_DB_Return(False, "Login failed.")
        else:
            return BBS_DB_Return(True, f"Welcome, {username}.", {'uid': user.id})

    def create_board(self, board_name, cur_uid):
        board = self.session.query(Boards).filter_by(name=board_name).one_or_none()

        if board:
            return BBS_DB_Return(False, "Board is already exist.")

        new_board = Boards(
            name=board_name,
            moderator_id=cur_uid,
        )
        self.session.add(new_board)
        self.session.commit()
        return BBS_DB_Return(True, "Create board successfully.")

    def create_post(self, cur_uid, board_name, post_title, post_content):
        board = self.session.query(Boards).filter_by(name=board_name).one_or_none()

        if not board:
            return BBS_DB_Return(False, "Board is not exist.")

        new_post = Posts(
            title=post_title,
            content=post_content,
            timestamp=datetime.now(),
            board_id=board.id,
            author_id=cur_uid,
        )
        self.session.add(new_post)
        self.session.commit()
        return BBS_DB_Return(True, "Create post successfully.")

    def list_board(self, condition):
        boards = self.session.query(Boards).filter(Boards.name.contains(condition)).all()
        return BBS_DB_Return(True, "", boards)

    def list_post(self, board_name, condition):
        board = self.session.query(Boards).filter_by(name=board_name).one_or_none()

        if not board:
            return BBS_DB_Return(False, "Board is not exist.")

        posts = self.session.query(Posts).join(Boards).filter(
            Boards.name == board_name,
            Posts.title.contains(condition),
        ).all()
        return BBS_DB_Return(True, "", posts)

    def read_post(self, post_id):
        post = self.session.query(Posts).get(post_id)

        if not post:
            return BBS_DB_Return(False, "Post is not exist.")

        return BBS_DB_Return(True, "", post)

    def delete_post(self, post_id, cur_uid):
        post = self.session.query(Posts).get(post_id)

        if not post:
            return BBS_DB_Return(False, "Post is not exist.")

        if post.author.id != cur_uid:
            return BBS_DB_Return(False, "Not the post owner.")

        self.session.delete(post)
        self.session.commit()
        return BBS_DB_Return(True, "Delete successfully.")

    def update_post(self, post_id, specifier, value, cur_uid):
        post = self.session.query(Posts).get(post_id)

        if not post:
            return BBS_DB_Return(False, "Post is not exist.")

        if post.author.id != cur_uid:
            return BBS_DB_Return(False, "Not the post owner.")

        if specifier == "content":
            post.content = value

        elif specifier == "title":
            post.title = value

        return BBS_DB_Return(True, "Update successfully.")
