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
        user = self.get_filter(Users, Users.username == username)[0]
        if user.password != password:
            return False, None
        return True, user.id

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
        user = self.get_filter(Users, Users.username == username)[0]
        if user:
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
                "subject": m.subject,
                "from": m.sender.username,
                "date": m.timestamp.strftime(r'%m/%d'),
                "mail_obj_name": m.object_name,
            })

        return mail_meta

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
