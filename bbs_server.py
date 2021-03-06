import socket
import threading
import os
import sys
import json
import argparse
from abc import ABCMeta, abstractmethod

from bbs_cmd_parser import BBS_Command_Parser
from bbs_db import BBS_DB
from constant import BBS_HOST, BBS_DEFAULT_PORT
from constant import DB_HOST, DB_PORT, DB_USERNAME, DB_PWD


parser = argparse.ArgumentParser()
parser.add_argument("port", nargs='?', default=BBS_DEFAULT_PORT)
args = parser.parse_args()

BBS_PORT = int(args.port)

class BBS_Server_Socket(threading.Thread, metaclass=ABCMeta):
    def __init__(self, socket):
        threading.Thread.__init__(self)
        self.socket = socket

    def run(self):
        print(f"New Connection.")
        welcome_msg = b"********************************\n** Welcome to the BBS server. **\n********************************\n"
        self.socket.send(welcome_msg)

        try:
            while True:
                cmd = self.socket.recv(1024).decode()
                if cmd == " ":  # client check connection
                    pass
                else:
                    self.execute(cmd)
        except BrokenPipeError:
            print("Client exit")
        except ConnectionResetError:
            print("Client exit")

        self.socket.close()

    @abstractmethod
    def execute(self, cmd):
        pass


class BBS_Server(BBS_Server_Socket, BBS_Command_Parser):
    def __init__(self, socket):
        BBS_Server_Socket.__init__(self, socket)
        self.db = BBS_DB(DB_HOST, DB_PORT, DB_USERNAME, DB_PWD)
        self.username = None
        self.uid = None

    def execute(self, cmd):
        try:
            cmd = cmd.strip('\r\n')
            cmd_type, parse_status, cmd_list = self.parse(cmd)
        except:
            self.socket.send(f"command not found: {cmd}\n".encode())
            return

        if not parse_status:
            self.socket.send(f"{self.usage(cmd_type)}\n".encode())
            return

        # dispatch handler
        if cmd_type == "register":
            self.register_handler(username=cmd_list[1], email=cmd_list[2], password=cmd_list[3])

        elif cmd_type == "login":
            self.login_handler(username=cmd_list[1], password=cmd_list[2])

        elif cmd_type == "logout":
            self.logout_handler()

        elif cmd_type == "whoami":
            self.whoami_handler()

        elif cmd_type == "create-board":
            self.create_board_handler(board_name=cmd_list[1])

        elif cmd_type == "create-post":
            self.create_post_handler(board_name=cmd_list[1], title=cmd_list[2], content=cmd_list[3])

        elif cmd_type == "list-board":
            condition = None if len(cmd_list) == 1 else cmd_list[1]
            self.list_board_handler(condition=condition)

        elif cmd_type == "list-post":
            condition = None if len(cmd_list) == 2 else cmd_list[2]
            self.list_post_handler(board_name=cmd_list[1], condition=condition)

        elif cmd_type == "read":
            self.read_post_handler(post_id=cmd_list[1])

        elif cmd_type == "delete-post":
            self.delete_post_handler(post_id=cmd_list[1])

        elif cmd_type == "update-post":
            self.update_post_handler(post_id=cmd_list[1], specifier=cmd_list[2], value=cmd_list[3])

        elif cmd_type == "comment":
            self.comment_handler(post_id=cmd_list[1], comment=cmd_list[2])

        elif cmd_type == "mail-to":
            self.mail_to_handler(receiver=cmd_list[1], subject=cmd_list[2], content=cmd_list[3])

        elif cmd_type == "list-mail":
            self.list_mail_handler()

        elif cmd_type == "retr-mail":
            self.retr_mail_handler(mail_id=cmd_list[1])

        elif cmd_type == "delete-mail":
            self.delete_mail_handler(mail_id=cmd_list[1])

        elif cmd_type == "subscribe":
            if cmd_list[0] == "subscribe-board":
                return self.subscribe_board_handler(board_name=cmd_list[1], keyword=cmd_list[2])
            if cmd_list[0] == "subscribe-author":
                return self.subscribe_author_handler(author_name=cmd_list[1], keyword=cmd_list[2])

        elif cmd_type == "unsubscribe":
            if cmd_list[0] == "unsubscribe-board":
                return self.unsubscribe_board_handler(board_name=cmd_list[1])
            if cmd_list[0] == "unsubscribe-author":
                return self.unsubscribe_author_handler(author_name=cmd_list[1])

        elif cmd_type == "list-sub":
            return self.list_sub_handler()

        elif cmd_type == "exit":
            self.exit_handler()

    def register_handler(self, username, email, password):
        valid = self.db.check_username_valid(username)
        if valid:
            self.socket.sendall(b"Valid username.")
        else:
            self.socket.sendall(b"Username is already used.")
            return

        bucket_name = self.socket.recv(1024).decode()
        if self.db.create_user(username, email, password, bucket_name):
            self.socket.sendall(b"Register successfully.")
        else:
            self.socket.send(b"Create user meta failed.")

    def login_handler(self, username, password):
        if self.username:
            self.socket.sendall(b"Client already logged in.")
            return

        valid, uid = self.db.login(username, password)
        if not valid:
            self.socket.sendall(b"Username or password is incorrect.")
            return

        self.username = username
        self.uid = uid

        bucket_name = self.db.get_bucket_name(username)
        self.socket.sendall(bucket_name.encode())

    def logout_handler(self):
        if not self.username:
            self.socket.sendall(b"Please login first.")

        else:
            res = f"Bye, {self.username}."
            self.username = None
            self.uid = None
            self.socket.sendall(res.encode())

    def whoami_handler(self):
        if not self.username:
            self.socket.sendall(b"Please login first.")

        else:
            self.socket.sendall(self.username.encode())

    def create_board_handler(self, board_name):
        if self.db.check_board_exist(board_name):
            self.socket.sendall(b"Board already exist.")
            return
        if not self.username:
            self.socket.sendall(b"Client doesn't log in.")
            return

        if self.db.create_board(self.uid, board_name):
            self.socket.sendall(b"Create board successfully.")
        else:
            self.socket.sendall(b"Create board failed.")

    def create_post_handler(self, board_name, title, content):
        if not self.db.check_board_exist(board_name):
            self.socket.sendall(b"Board does not exist.")
            return
        if not self.username:
            self.socket.sendall(b"Client doesn't log in.")
            return

        self.socket.sendall(b"Valid action.")

        post_obj_name = self.socket.recv(1024).decode()
        if self.db.create_post(self.uid, board_name, title, post_obj_name):
            self.socket.sendall(b"Create post successfully.")
        else:
            self.socket.sendall(b"Create post meta failed.")

    def list_board_handler(self, condition):
        boards = self.db.list_board(condition)

        max_name_len = 4  # len("Name")
        for b in boards:
            max_name_len = max(max_name_len, len(b['name']))

        def format_msg(index, name, moderator):
            return f"\t{index:<10}{name:<{max_name_len + 5}}{moderator}\n"

        output = format_msg("Index", "Name", "Moderator")
        for idx, b in enumerate(boards, start=1):
            output += format_msg(idx, b['name'], b['moderator'])
        self.socket.sendall(output.encode())

    def list_post_handler(self, board_name, condition):
        if not self.db.check_board_exist(board_name):
            self.socket.sendall(b"Board does not exist.")
            return

        posts = self.db.list_post(board_name, condition)

        max_title_len = 5  # len("Title")
        max_author_len = 6  # len("Author")
        for p in posts:
            max_title_len = max(max_title_len, len(p['title']))
            max_author_len = max(max_author_len, len(p['author']))

        def format_msg(id, title, author, date):
            return f"\t{id:<10}{title:<{max_title_len + 5}}{author:<{max_author_len + 5}}{date}\n"

        output = format_msg("ID", "Title", "Author", "Date")
        for p in posts:
            output += format_msg(p['id'], p['title'], p['author'], p['date'])
        self.socket.sendall(output.encode())

    def read_post_handler(self, post_id):
        if not self.db.check_post_exist(post_id):
            self.socket.sendall(b"Post does not exist.")
            return

        post_meta = self.db.get_post_meta(post_id)
        self.socket.sendall(json.dumps(post_meta).encode())

    def delete_post_handler(self, post_id):
        if not self.username:
            self.socket.sendall(b"Client doesn't log in.")
            return
        if not self.db.check_post_exist(post_id):
            self.socket.sendall(b"Post does not exist.")
            return
        if not self.db.check_is_post_owner(post_id, self.uid):
            self.socket.sendall(b"Not the post owner.")
            return

        post_meta = self.db.get_post_meta(post_id)
        self.db.delete_post(post_id)
        self.socket.sendall(post_meta['post_obj_name'].encode())

    def update_post_handler(self, post_id, specifier, value):
        if not self.username:
            self.socket.sendall(b"Client doesn't log in.")
            return
        if not self.db.check_post_exist(post_id):
            self.socket.sendall(b"Post does not exist.")
            return
        if not self.db.check_is_post_owner(post_id, self.uid):
            self.socket.sendall(b"Not the post owner.")
            return

        if specifier == "content":
            post_obj_name = self.db.get_post_meta(post_id)['post_obj_name']
            self.socket.sendall(post_obj_name.encode())

        elif specifier == "title":
            self.db.update_post_title(post_id, value)
            self.socket.sendall(b"Update successfully.")

    def comment_handler(self, post_id, comment):
        if not self.username:
            self.socket.sendall(b"Client doesn't log in.")
            return
        if not self.db.check_post_exist(post_id):
            self.socket.sendall(b"Post does not exist.")
            return

        post_meta = self.db.get_post_meta(post_id)
        self.socket.sendall(json.dumps(post_meta).encode())

    def mail_to_handler(self, receiver, subject, content):
        if not self.username:
            self.socket.sendall(b"Client doesn't log in.")
            return
        if not self.db.check_user_exist(receiver):
            self.socket.sendall(b"Receiver doesn't exist.")
            return

        receiver_bucket_name = self.db.get_bucket_name(receiver)
        self.socket.sendall(receiver_bucket_name.encode())

        mail_obj_name = self.socket.recv(1024).decode()

        if self.db.create_mail(subject, receiver, self.uid, mail_obj_name):
            self.socket.sendall(b"Sent successfully.")
        else:
            self.socket.send(b"Create mail meta failed.")

    def list_mail_handler(self):
        if not self.username:
            self.socket.sendall(b"Client doesn't log in.")
            return

        mails = self.db.list_mail(self.uid)

        max_subject_len = 7  # len("Subject")
        max_sender_len = 4  # len("From")
        for m in mails:
            max_subject_len = max(max_subject_len, len(m['subject']))
            max_sender_len = max(max_sender_len, len(m['from']))

        def format_msg(id, subject, sender, date):
            return f"\t{id:<10}{subject:<{max_subject_len + 5}}{sender:<{max_sender_len + 5}}{date}\n"

        output = format_msg("ID", "Subject", "From", "Date")
        for idx, m in enumerate(mails, start=1):
            output += format_msg(idx, m['subject'], m['from'], m['date'].strftime(r'%m/%d'))
        self.socket.sendall(output.encode())

    def retr_mail_handler(self, mail_id):
        if not self.username:
            self.socket.sendall(b"Client doesn't log in.")
            return

        mails = self.db.list_mail(self.uid)
        mail_idx = int(mail_id) - 1 # 1-based id
        if mail_idx >= len(mails) or mail_idx < 0:
            self.socket.sendall(b"Mail doesn't exist.")
            return

        mail = mails[mail_idx]
        mail['date'] = mail['date'].strftime(r'%Y-%m-%d')
        self.socket.sendall(json.dumps(mail).encode())

    def delete_mail_handler(self, mail_id):
        if not self.username:
            self.socket.sendall(b"Client doesn't log in.")
            return

        mails = self.db.list_mail(self.uid)
        mail_idx = int(mail_id) - 1 # 1-based id
        if mail_idx >= len(mails) or mail_idx < 0:
            self.socket.sendall(b"Mail doesn't exist.")
            return

        mail_meta = mails[mail_idx]
        self.db.delete_mail(mail_meta['id'])
        self.socket.sendall(mail_meta['mail_obj_name'].encode())

    def subscribe_board_handler(self, board_name, keyword):
        if not self.username:
            self.socket.sendall(b"Client doesn't log in.")
            return
        self.socket.sendall(b"Valid action")

    def subscribe_author_handler(self, author_name, keyword):
        if not self.username:
            self.socket.sendall(b"Client doesn't log in.")
            return
        self.socket.sendall(b"Valid action")

    def unsubscribe_board_handler(self, board_name):
        if not self.username:
            self.socket.sendall(b"Client doesn't log in.")
            return
        self.socket.sendall(b"Valid action")

    def unsubscribe_author_handler(self, author_name):
        if not self.username:
            self.socket.sendall(b"Client doesn't log in.")
            return
        self.socket.sendall(b"Valid action")

    def list_sub_handler(self):
        if not self.username:
            self.socket.sendall(b"Client doesn't log in.")
            return
        self.socket.sendall(b"Valid action")

    def exit_handler(self):
        pass


def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((BBS_HOST, BBS_PORT))
    s.listen()

    while True:
        client_socket, client_addr = s.accept()
        BBS_Server(client_socket).start()


if __name__ == "__main__":
    main()
