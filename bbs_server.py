from constant import BBS_HOST, BBS_PORT
from constant import DB_HOST, DB_PORT, DB_USERNAME, DB_PWD
import socket
import threading
import os
import sys

from abc import ABCMeta, abstractmethod
from bbs_cmd_parser import BBS_Command_Parser
from bbs_db import BBS_DB


class BBS_Server_Socket(threading.Thread, metaclass=ABCMeta):
    def __init__(self, socket):
        threading.Thread.__init__(self)
        self.socket = socket

    def run(self):
        print(f"New Connection.")
        self.socket.send(b"********************************\n")
        self.socket.send(b"** Welcome to the BBS server. **\n")
        self.socket.send(b"********************************\n")

        while True:
            self.socket.send(b"% ")
            cmd = self.socket.recv(1024)
            self.execute(cmd)

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
            cmd = cmd.decode().strip('\r\n')
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
            self.mail_to_handler(username=cmd_list[1], subject=cmd_list[2], content=cmd_list[3])

        elif cmd_type == "list-mail":
            self.list_mail_handler()

        elif cmd_type == "retr-mail":
            self.retr_mail_handler(mail_id=cmd_list[1])

        elif cmd_type == "delete-mail":
            self.delete_mail_handler(mail_id=cmd_list[1])

        elif cmd_type == "exit":
            self.exit_handler()

    def register_handler(self, username, email, password):
        print(username, email, password)

    def login_handler(self, username, password):
        print(username, password)

    def logout_handler(self):
        print('logout')

    def whoami_handler(self):
        print('whoami')

    def create_board_handler(self, board_name):
        print(board_name)

    def create_post_handler(self, board_name, title, content):
        print(board_name, title, content)

    def list_board_handler(self, condition):
        print(condition)

    def list_post_handler(self, board_name, condition):
        print(board_name, condition)

    def read_post_handler(self, post_id):
        print(post_id)

    def delete_post_handler(self, post_id):
        print(post_id)

    def update_post_handler(self, post_id, specifier, value):
        print(post_id, specifier, value)

    def comment_handler(self, post_id, comment):
        print(post_id, comment)

    def mail_to_handler(self, username, subject, content):
        print(username, subject, content)

    def list_mail_handler(self):
        print('list-mail')

    def retr_mail_handler(self, mail_id):
        print(mail_id)

    def delete_mail_handler(self, mail_id):
        print(mail_id)

    def exit_handler(self):
        print('exit')


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
