from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.users import Users

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


class BBS_DB(BBS_DB_BASE):
    def __init__(self, host, port, username, pwd):
        super().__init__(host, port, username, pwd)

    def create_user(self, username, email, password):
        """
        Returns:
            0: Register successfull
            1: Username is already use
        """
        user = self.session.query(Users).filter_by(
            username=username).one_or_none()
        if user:
            return 1

        new_user = Users(
            username=username,
            email=email,
            password=password,
        )
        self.session.add(new_user)
        self.session.commit()
        return 0

    def login(self, username, password):
        """
        Returns:
            0: Successfully login
            1: Login failed
        """
        user = self.session.query(Users).filter_by(
            username=username).one_or_none()

        if user is None or user.password != password:
            return 1
        else:
            return 0
