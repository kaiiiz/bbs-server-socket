from db.users import Users
from db.boards import Boards
from db.posts import Posts

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from datetime import datetime


class BBS_DB_BASE:
    def __init__(self, host, port, username, pwd):
        engine = create_engine(f"mysql://{username}:{pwd}@{host}:{port}/bbs")
        session_factory = sessionmaker(bind=engine)
        self.scoped_session_factory = scoped_session(session_factory)


class BBS_DB_Return:
    def __init__(self, success, message, data=None):
        self.success = success
        self.data = data
        self.message = message + '\n'


class BBS_DB(BBS_DB_BASE):
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

    @save_transaction
    def login(self, username, password):
        user = self.session.query(Users).filter_by(username=username).one_or_none()

        if user is None or user.password != password:
            return BBS_DB_Return(False, "Login failed.")
        else:
            return BBS_DB_Return(True, f"Welcome, {username}.", {'uid': user.id})

    @save_transaction
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

    @save_transaction
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

    @save_transaction
    def list_board(self, condition):
        boards_row = self.session.query(Boards).filter(Boards.name.contains(condition)).all()
        boards = []
        for row in boards_row:
            boards.append({
                'id': row.id,
                'name': row.name,
                'moderator': row.moderator.username,
            })
        return BBS_DB_Return(True, "", boards)

    @save_transaction
    def list_post(self, board_name, condition):
        board = self.session.query(Boards).filter_by(name=board_name).one_or_none()

        if not board:
            return BBS_DB_Return(False, "Board is not exist.")

        posts = []
        for p in board.posts:
            if condition in p.title:
                posts.append({
                    'id': p.id,
                    'title': p.title,
                    'author': p.author.username,
                    'timestamp': p.timestamp,
                })

        return BBS_DB_Return(True, "", posts)

    @save_transaction
    def read_post(self, post_id):
        post_row = self.session.query(Posts).get(post_id)
        if not post_row:
            return BBS_DB_Return(False, "Post is not exist.")

        comments = []
        for c in post_row.comments:
            comments.append({
                'user': c.user.username,
                'content': c.content,
            })

        post = {
            'author': post_row.author.username,
            'title': post_row.title,
            'timestamp': post_row.timestamp,
            'content': post_row.content,
            'comments': comments,
        }

        return BBS_DB_Return(True, "", post)

    @save_transaction
    def delete_post(self, post_id, cur_uid):
        post = self.session.query(Posts).get(post_id)

        if not post:
            return BBS_DB_Return(False, "Post is not exist.")

        if post.author.id != cur_uid:
            return BBS_DB_Return(False, "Not the post owner.")

        self.session.delete(post)
        self.session.commit()
        return BBS_DB_Return(True, "Delete successfully.")

    @save_transaction
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

        self.session.commit()
        return BBS_DB_Return(True, "Update successfully.")

    @save_transaction
    def comment(self, post_id, comment_content, cur_uid):
        post = self.session.query(Posts).get(post_id)

        if not post:
            return BBS_DB_Return(False, "Post is not exist.")

        new_comment = PostComments(
            content=comment_content,
            post_id=post_id,
            user_id=cur_uid,
        )
        self.session.add(new_comment)
        self.session.commit()
        return BBS_DB_Return(True, "Comment successfully.")
