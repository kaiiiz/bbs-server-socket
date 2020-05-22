from db.base import Base
from db.users import Users
from db.boards import Boards
from db.posts import Posts
from db.mails import Mails
import boto3

from constant import DB_HOST, DB_PORT, DB_USERNAME, DB_PWD
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

class SCHEMA_CREATOR:
    def __init__(self, host, port, username, pwd):
        self.engine = self.get_engine(host, port, username, pwd)
        self.session_factory = sessionmaker(bind=self.engine)

    def get_engine(self, host, port, username, pwd):
        engine = create_engine(f"mysql://{username}:{pwd}@{host}:{port}")
        engine.execute('CREATE DATABASE IF NOT EXISTS bbs;')
        return create_engine(f"mysql://{username}:{pwd}@{host}:{port}/bbs")

    def create_table(self):
        Users.__table__.create(bind=self.engine, checkfirst=True)
        Boards.__table__.create(bind=self.engine, checkfirst=True)
        Posts.__table__.create(bind=self.engine, checkfirst=True)
        Mails.__table__.create(bind=self.engine, checkfirst=True)

    def clear_table(self):
        session = self.session_factory()
        session.execute('SET FOREIGN_KEY_CHECKS = 0')
        for table in Base.metadata.tables:
            session.execute(f'DROP TABLE {table};')
        session.execute('SET FOREIGN_KEY_CHECKS = 1')
        session.commit()
        session.close()

def s3_clear():
    s3 = boto3.resource("s3")
    for bucket in s3.buckets.all():
        for obj in bucket.objects.all():
            obj.delete()
        bucket.delete()

if __name__ == '__main__':
    creator = SCHEMA_CREATOR(DB_HOST, DB_PORT, DB_USERNAME, DB_PWD)
    creator.clear_table()
    creator.create_table()
    s3_clear()
