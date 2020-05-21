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
    def create(self, model, data):
        row = model(**data)
        self.session.add(row)
        self.session.commit()
        return asdict(row)

    @save_transaction
    def get(self, model, id):
        row = self.session.query(model).get(id)
        return asdict(row)

    @save_transaction
    def get_filter(self, model, filter):
        rows = self.session.query(model).filter(filter).all()
        for idx, r in enumerate(rows):
            rows[idx] = asdict(r)
        return rows

    @save_transaction
    def update(self, model, id, data):
        row = self.session.query(model).get(id)
        for k, v in data.items():
            setattr(row, k, v)
        self.session.commit()
        return asdict(row)

    @save_transaction
    def update_filter(self, model, filter, data):
        rows = self.session.query(model).filter(filter).all()
        for idx, r in enumerate(rows):
            for k, v in data.items():
                setattr(r, k, v)
            rows[idx] = asdict(r)
        self.session.commit()
        return rows

    @save_transaction
    def delete(self, model, id):
        row = self.session.query(model).get(id)
        self.session.delete(row)
        self.session.commit()
        return None


class BBS_DB(BBS_DB_API):
    def __init__(self, host, port, username, pwd):
        super().__init__(host, port, username, pwd)

    def check_username_valid(self, username):
        users = self.get_filter(Users, Users.username == username)
        if len(users) > 0:
            return False
        return True

    def create_user(self, username, email, password, bucket_name):
        try:
            new_user = self.create(Users, {
                'username': username,
                'email': email,
                'password': password,
                'bucket_name': bucket_name,
            })
            return True
        except:
            return False

    def login(self, username, password):
        users = self.get_filter(Users, Users.username == username)
        if len(users) != 1 or users[0]['password'] != password:
            return False, None
        return True, users[0]['id']

    def get_bucket_name(self, uid):
        user = self.get(Users, uid)
        return user['bucket_name']

    def check_board_exist(self, board_name):
        boards = self.get_filter(Boards, Boards.name == board_name)
        if len(boards) == 0:
            return False
        return True

    def get_board_id(self, board_name):
        boards = self.get_filter(Boards, Boards.name == board_name)
        return boards[0]['id']

    def create_post(self, uid, board_name, title, post_obj_name):
        board_id = self.get_board_id(board_name)
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

    def create_board(self, uid, board_name):
        try:
            self.create(Boards, {
                'name': board_name,
                'moderator_id': uid,
            })
            return True
        except:
            return False


# class BBS_DB_Return:
#     def __init__(self, success, message, data=None):
#         self.success = success
#         self.data = data
#         self.message = message + '\n'


# class BBS_DB(BBS_DB_BASE):
#     def save_transaction(func):
#         def wrapper(self, *args, **kwargs):
#             self.session = self.scoped_session_factory()  # Thread-local session
#             try:
#                 return func(self, *args, **kwargs)
#             except:
#                 self.session.rollback()
#                 raise
#             finally:
#                 self.session.close()
#         return wrapper

#     @save_transaction
#     def create_user(self, username, email, password):
#         user = self.session.query(Users).filter_by(username=username).one_or_none()

#         if user:
#             return BBS_DB_Return(False, "Username is already use.")

#         new_user = Users(
#             username=username,
#             email=email,
#             password=password,
#         )
#         self.session.add(new_user)
#         self.session.commit()
#         return BBS_DB_Return(True, "Register successfull.")

#     @save_transaction
#     def login(self, username, password):
#         user = self.session.query(Users).filter_by(username=username).one_or_none()

#         if user is None or user.password != password:
#             return BBS_DB_Return(False, "Login failed.")
#         else:
#             return BBS_DB_Return(True, f"Welcome, {username}.", {'uid': user.id})

#     @save_transaction
#     def create_board(self, board_name, cur_uid):
#         board = self.session.query(Boards).filter_by(name=board_name).one_or_none()

#         if board:
#             return BBS_DB_Return(False, "Board is already exist.")

#         new_board = Boards(
#             name=board_name,
#             moderator_id=cur_uid,
#         )
#         self.session.add(new_board)
#         self.session.commit()
#         return BBS_DB_Return(True, "Create board successfully.")

#     @save_transaction
#     def create_post(self, cur_uid, board_name, post_title, post_content):
#         board = self.session.query(Boards).filter_by(name=board_name).one_or_none()

#         if not board:
#             return BBS_DB_Return(False, "Board is not exist.")

#         new_post = Posts(
#             title=post_title,
#             content=post_content,
#             timestamp=datetime.now(),
#             board_id=board.id,
#             author_id=cur_uid,
#         )
#         self.session.add(new_post)
#         self.session.commit()
#         return BBS_DB_Return(True, "Create post successfully.")

#     @save_transaction
#     def list_board(self, condition):
#         boards_row = self.session.query(Boards).filter(Boards.name.contains(condition)).all()
#         boards = []
#         for row in boards_row:
#             boards.append({
#                 'id': row.id,
#                 'name': row.name,
#                 'moderator': row.moderator.username,
#             })
#         return BBS_DB_Return(True, "", boards)

#     @save_transaction
#     def list_post(self, board_name, condition):
#         board = self.session.query(Boards).filter_by(name=board_name).one_or_none()

#         if not board:
#             return BBS_DB_Return(False, "Board is not exist.")

#         posts = []
#         for p in board.posts:
#             if condition in p.title:
#                 posts.append({
#                     'id': p.id,
#                     'title': p.title,
#                     'author': p.author.username,
#                     'timestamp': p.timestamp,
#                 })

#         return BBS_DB_Return(True, "", posts)

#     @save_transaction
#     def read_post(self, post_id):
#         post_row = self.session.query(Posts).get(post_id)
#         if not post_row:
#             return BBS_DB_Return(False, "Post is not exist.")

#         comments = []
#         for c in post_row.comments:
#             comments.append({
#                 'user': c.user.username,
#                 'content': c.content,
#             })

#         post = {
#             'author': post_row.author.username,
#             'title': post_row.title,
#             'timestamp': post_row.timestamp,
#             'content': post_row.content,
#             'comments': comments,
#         }

#         return BBS_DB_Return(True, "", post)

#     @save_transaction
#     def delete_post(self, post_id, cur_uid):
#         post = self.session.query(Posts).get(post_id)

#         if not post:
#             return BBS_DB_Return(False, "Post is not exist.")

#         if post.author.id != cur_uid:
#             return BBS_DB_Return(False, "Not the post owner.")

#         self.session.delete(post)
#         self.session.commit()
#         return BBS_DB_Return(True, "Delete successfully.")

#     @save_transaction
#     def update_post(self, post_id, specifier, value, cur_uid):
#         post = self.session.query(Posts).get(post_id)

#         if not post:
#             return BBS_DB_Return(False, "Post is not exist.")

#         if post.author.id != cur_uid:
#             return BBS_DB_Return(False, "Not the post owner.")

#         if specifier == "content":
#             post.content = value
#         elif specifier == "title":
#             post.title = value

#         self.session.commit()
#         return BBS_DB_Return(True, "Update successfully.")

#     @save_transaction
#     def comment(self, post_id, comment_content, cur_uid):
#         post = self.session.query(Posts).get(post_id)

#         if not post:
#             return BBS_DB_Return(False, "Post is not exist.")

#         new_comment = PostComments(
#             content=comment_content,
#             post_id=post_id,
#             user_id=cur_uid,
#         )
#         self.session.add(new_comment)
#         self.session.commit()
#         return BBS_DB_Return(True, "Comment successfully.")
