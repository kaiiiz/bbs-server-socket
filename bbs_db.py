from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.users import Users
from db.boards import Boards
from db.posts import Posts, PostComments

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

    def create_board(self, boardname):
        board = self.session.query(Boards).filter_by(name=boardname).one_or_none()

        if board:
            return BBS_DB_Return(False, "Board is already exist.")

        new_board = Boards(
            name=boardname
        )
        self.session.add(new_board)
        self.session.commit()
        return BBS_DB_Return(True, "Create board successfully.")
