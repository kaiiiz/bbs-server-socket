from db.users import Users
from db.boards import Boards
from db.posts import Posts
from db.mails import Mails

from constant import DB_HOST, DB_PORT, DB_USERNAME, DB_PWD
from sqlalchemy import create_engine

class SCHEMA_CREATOR:
    def __init__(self, host, port, username, pwd):
        self.engine = self.get_engine(host, port, username, pwd)

    def get_engine(self, host, port, username, pwd):
        engine = create_engine(f"mysql://{username}:{pwd}@{host}:{port}")
        engine.execute('CREATE DATABASE IF NOT EXISTS bbs;')
        return create_engine(f"mysql://{username}:{pwd}@{host}:{port}/bbs")

    def create_table(self):
        Users.__table__.create(bind=self.engine, checkfirst=True)
        Boards.__table__.create(bind=self.engine, checkfirst=True)
        Posts.__table__.create(bind=self.engine, checkfirst=True)
        Mails.__table__.create(bind=self.engine, checkfirst=True)

if __name__ == '__main__':
    creator = SCHEMA_CREATOR(DB_HOST, DB_PORT, DB_USERNAME, DB_PWD)
    creator.create_table()
