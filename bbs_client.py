#! /usr/bin/env python3

import socket
import threading
import argparse
import queue
import os
import signal
import boto3
import uuid

from abc import ABCMeta, abstractmethod
from bbs_cmd_parser import BBS_Command_Parser

parser = argparse.ArgumentParser()
parser.add_argument("host")
parser.add_argument("port")
args = parser.parse_args()

HOST = args.host
PORT = int(args.port)


class BBS_Client_Socket(threading.Thread, metaclass=ABCMeta):
    def __init__(self, cmd_q, reply_q, alive):
        threading.Thread.__init__(self)

        self.cmd_q = cmd_q
        self.reply_q = reply_q
        self.alive = alive

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((HOST, PORT))

    def run(self):
        welcome_msg = self.socket.recv(1024).decode()
        print(welcome_msg, end='')
        self.alive.set()

        while self.alive.is_set():
            try:
                cmd = self.cmd_q.get(block=True, timeout=0.1)
                res = self.execute(cmd)
                self.reply_q.put(res)

            except queue.Empty:
                self.check_connection()
                continue

        self.socket.close()
        os.kill(os.getpid(), signal.SIGINT)

    @abstractmethod
    def check_connection(self):
        pass

    @abstractmethod
    def execute(self, cmd):
        pass


class BBS_Client(BBS_Client_Socket, BBS_Command_Parser):
    def __init__(self, cmd_q, reply_q, alive):
        BBS_Client_Socket.__init__(self, cmd_q, reply_q, alive)
        self.s3 = boto3.resource("s3")
        self.bucket = None

    def socket_err_handler(func):
        def wrapped_func(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)

            except ConnectionResetError:
                print("\nConnection Reset Error!")
                self.alive.clear()

            except BrokenPipeError:
                print("\nBroken Pipe Error!")
                self.alive.clear()

            except Exception as e:
                print(f"\n{e}")
                self.alive.clear()

        return wrapped_func

    @socket_err_handler
    def check_connection(self):
        self.socket.send(b" ")

    @socket_err_handler
    def execute(self, cmd):
        self.socket.send(cmd.encode())

        try:
            cmd = cmd.strip('\r\n')
            cmd_type, parse_status, cmd_list = self.parse(cmd)
        except:
            return self.socket.recv(1024).decode()

        if not parse_status:
            return self.socket.recv(1024).decode()

        # dispatch handler
        if cmd_type == "register":
            return self.register_handler(username=cmd_list[1], email=cmd_list[2], password=cmd_list[3])

        elif cmd_type == "login":
            return self.login_handler(username=cmd_list[1], password=cmd_list[2])

        elif cmd_type == "logout":
            return self.logout_handler()

        elif cmd_type == "whoami":
            return self.whoami_handler()

        elif cmd_type == "create-board":
            return self.create_board_handler(board_name=cmd_list[1])

        elif cmd_type == "create-post":
            return self.create_post_handler(board_name=cmd_list[1], title=cmd_list[2], content=cmd_list[3])

        elif cmd_type == "list-board":
            condition = None if len(cmd_list) == 1 else cmd_list[1]
            return self.list_board_handler(condition=condition)

        elif cmd_type == "list-post":
            condition = None if len(cmd_list) == 2 else cmd_list[2]
            return self.list_post_handler(board_name=cmd_list[1], condition=condition)

        elif cmd_type == "read":
            return self.read_post_handler(post_id=cmd_list[1])

        elif cmd_type == "delete-post":
            return self.delete_post_handler(post_id=cmd_list[1])

        elif cmd_type == "update-post":
            return self.update_post_handler(post_id=cmd_list[1], specifier=cmd_list[2], value=cmd_list[3])

        elif cmd_type == "comment":
            return self.comment_handler(post_id=cmd_list[1], comment=cmd_list[2])

        elif cmd_type == "mail-to":
            return self.mail_to_handler(username=cmd_list[1], subject=cmd_list[2], content=cmd_list[3])

        elif cmd_type == "list-mail":
            return self.list_mail_handler()

        elif cmd_type == "retr-mail":
            return self.retr_mail_handler(mail_id=cmd_list[1])

        elif cmd_type == "delete-mail":
            return self.delete_mail_handler(mail_id=cmd_list[1])

        elif cmd_type == "exit":
            return self.exit_handler()


    def register_handler(self, username, email, password):
        valid_check = self.socket.recv(1024).decode()
        if valid_check == "User is already used.":
            return "User is already used.\n"

        # valid username, create bucket
        bucket_name = str(uuid.uuid4())
        self.s3.create_bucket(Bucket=bucket_name)

        # store metadata
        self.socket.sendall(bucket_name.encode())
        return self.socket.recv(1024).decode() + '\n'

    def login_handler(self, username, password):
        valid_check = self.socket.recv(1024).decode()
        if valid_check == "Client already logged in.":
            return "Please logout first.\n"
        if valid_check == "Username or password is incorrect.":
            return "Login failed.\n"

        # retrieve bucket name from server
        bucket_name = valid_check
        self.bucket = self.s3.Bucket(bucket_name)
        return f"Welcome, {username}.\n"

    def logout_handler(self):
        return self.socket.recv(1024).decode() + '\n'

    def whoami_handler(self):
        return self.socket.recv(1024).decode() + '\n'

    def create_board_handler(self, board_name):
        valid_check = self.socket.recv(1024).decode()
        if valid_check == "Client doesn't log in.":
            return "Please login first.\n"
        if valid_check == "Board is already exist.":
            return "Board is already exist.\n"
        return valid_check + '\n'

    def create_post_handler(self, board_name, title, content):
        valid_check = self.socket.recv(1024).decode()
        if valid_check == "Client doesn't log in.":
            return "Please login first.\n"
        if valid_check == "Board doesn't exist.":
            return "Board is not exist.\n"

        tmp_file = f"./tmp/{title}"
        os.makedirs(os.path.dirname(tmp_file), exist_ok=True)
        with open(tmp_file, "w") as tmp:
            tmp.write(content)

        post_obj_name = str(uuid.uuid4())
        self.bucket.upload_file(tmp_file, post_obj_name)
        os.remove(tmp_file)

        # store metadata of post
        self.socket.sendall(post_obj_name.encode())
        return self.socket.recv(1024).decode() + '\n'

    def list_board_handler(self, condition):
        return self.socket.recv(1024).decode()

    def list_post_handler(self, board_name, condition):
        valid_check = self.socket.recv(1024).decode()
        if valid_check == "Board doesn't exist.":
            return "Board is not exist.\n"
        return valid_check

    def read_post_handler(self, post_id):
        print(post_id)

    def delete_post_handler(self, post_id):
        return self.socket.recv(1024).decode() + '\n'

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
        self.alive.clear()
        return "Good Bye!\n"


def main():
    cmd_q = queue.Queue()
    reply_q = queue.Queue()
    alive = threading.Event()

    client = BBS_Client(cmd_q, reply_q, alive)
    client.start()

    try:
        while True:
            if alive.is_set():  # after welcome message
                cmd = input('% ')
                if len(cmd.strip()) > 0:
                    cmd_q.put(cmd)
                    res = reply_q.get()
                    print(res, end='')
    except:
        pass


if __name__ == '__main__':
    main()
