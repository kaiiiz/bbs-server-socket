from db.users import Users
from db.boards import Boards
from db.posts import Posts
from db.mails import Mails

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from datetime import datetime
from dataclasses import asdict


class BBS_DB_BASE:
    def __init__(self, host, port, username, pwd):
        engine = create_engine(f"mysql://{username}:{pwd}@{host}:{port}/bbs")
        session_factory = sessionmaker(bind=engine)
        self.scoped_session_factory = scoped_session(session_factory)


class BBS_DB_API(BBS_DB_BASE):
    def create(self, model, data):
        row = model(**data)
        self.session.add(row)
        self.session.commit()
        return row

    def get(self, model, id):
        return self.session.query(model).get(id)

    def get_filter(self, model, filter):
        return self.session.query(model).filter(filter).all()

    def update(self, model, id, data):
        row = self.session.query(model).get(id)
        for k, v in data.items():
            setattr(row, k, v)
        self.session.commit()
        return row

    def update_filter(self, model, filter, data):
        rows = self.session.query(model).filter(filter).all()
        for idx, r in enumerate(rows):
            for k, v in data.items():
                setattr(r, k, v)
            rows[idx] = asdict(r)
        self.session.commit()
        return rows

    def delete(self, model, id):
        row = self.session.query(model).get(id)
        self.session.delete(row)
        self.session.commit()
        return None


class BBS_DB(BBS_DB_API):
    def __init__(self, host, port, username, pwd):
        super().__init__(host, port, username, pwd)

    def save_transaction(func):
        def wrapper(self, *args, **kwargs):
            self.session = self.scoped_session_factory()  # Thread-local session
            try:
                return func(self, *args, **kwargs)
            except:
                self.session.rollback()
                raise
            finally:
                self.session.close()
        return wrapper

    @save_transaction
    def check_username_valid(self, username):
        users = self.get_filter(Users, Users.username == username)
        if len(users) > 0:
            return False
        return True

    @save_transaction
    def create_user(self, username, email, password, bucket_name):
        try:
            self.create(Users, {
                'username': username,
                'email': email,
                'password': password,
                'bucket_name': bucket_name,
            })
            return True
        except:
            return False

    @save_transaction
    def login(self, username, password):
        user = self.get_filter(Users, Users.username == username)
        if len(user) == 0:
            return False, None
        if user[0].password != password:
            return False, None
        return True, user[0].id

    @save_transaction
    def get_bucket_name(self, username):
        user = self.get_filter(Users, Users.username == username)[0]
        return user.bucket_name

    @save_transaction
    def check_board_exist(self, board_name):
        boards = self.get_filter(Boards, Boards.name == board_name)
        if len(boards) == 0:
            return False
        return True

    @save_transaction
    def create_post(self, uid, board_name, title, post_obj_name):
        board_id = self.get_filter(Boards, Boards.name == board_name)[0].id
        try:
            self.create(Posts, {
                'title': title,
                'timestamp': datetime.now(),
                'object_name': post_obj_name,
                'board_id': board_id,
                'author_id': uid,
            })
            return True
        except:
            return False

    @save_transaction
    def create_board(self, uid, board_name):
        try:
            self.create(Boards, {
                'name': board_name,
                'moderator_id': uid,
            })
            return True
        except:
            return False

    @save_transaction
    def list_board(self, condition):
        if condition == None:
            condition = ""

        boards_rows = self.get_filter(Boards, Boards.name.contains(condition))
        boards = []
        for idx, br in enumerate(boards_rows):
            b = asdict(br)
            b['moderator'] = br.moderator.username
            boards.append(b)
        return boards

    @save_transaction
    def list_post(self, board_name, condition):
        board = self.get_filter(Boards, Boards.name == board_name)[0]

        if condition == None:
            condition = ""

        posts = []
        for p in board.posts:
            if condition in p.title:
                posts.append({
                    'id': p.id,
                    'title': p.title,
                    'author': p.author.username,
                    'date': p.timestamp.strftime(r'%m/%d'),
                })
        return posts

    @save_transaction
    def check_post_exist(self, post_id):
        post = self.get(Posts, post_id)
        if post:
            return True
        return False

    @save_transaction
    def check_is_post_owner(self, post_id, uid):
        post = self.get(Posts, post_id)
        if post.author.id != uid:
            return False
        return True

    @save_transaction
    def delete_post(self, post_id):
        self.delete(Posts, post_id)

    @save_transaction
    def get_post_meta(self, post_id):
        post = self.get(Posts, post_id)
        return {
            "title": post.title,
            "date": post.timestamp.strftime(r'%Y-%m-%d'),
            "author": post.author.username,
            "bucket_name": post.author.bucket_name,
            "post_obj_name": post.object_name,
        }

    @save_transaction
    def update_post_title(self, post_id, title):
        self.update(Posts, post_id, {
            "title": title,
        })

    @save_transaction
    def check_user_exist(self, username):
        users = self.get_filter(Users, Users.username == username)
        if len(users) != 0:
            return True
        return False

    @save_transaction
    def create_mail(self, subject, receiver_name, sender_id, mail_obj_name):
        receiver_id = self.get_filter(Users, Users.username == receiver_name)[0].id
        try:
            self.create(Mails, {
                "subject": subject,
                "object_name": mail_obj_name,
                "receiver_id": receiver_id,
                "sender_id": sender_id,
                "timestamp": datetime.now(),
            })
            return True
        except:
            return False

    @save_transaction
    def list_mail(self, uid):
        user = self.get(Users, uid)
        mail_meta = []

        for m in user.receive_mails:
            mail_meta.append({
                "id": m.id,
                "subject": m.subject,
                "from": m.sender.username,
                "date": m.timestamp,
                "mail_obj_name": m.object_name,
            })

        return mail_meta

    @save_transaction
    def delete_mail(self, mail_id):
        self.delete(Mails, mail_id)
