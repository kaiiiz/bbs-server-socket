import socket
import threading
import os
import sys
from dotenv import load_dotenv
from bbs_db import BBS_DB

load_dotenv()

if len(sys.argv) == 2:
    BBS_PORT = int(sys.argv[1])
else:
    BBS_PORT = int(os.getenv("BBS_SERVER_DEFAULT_PORT"))

BBS_HOST = os.getenv("BBS_SERVER_IP")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USERNAME = os.getenv("DB_ROOT_USERNAME")
DB_PWD = os.getenv("DB_ROOT_PWD")


class Controller():
    def __init__(self):
        self.db = BBS_DB(DB_HOST, DB_PORT, DB_USERNAME, DB_PWD)
        self.user = None

    def execute(self, cmd):
        try:
            cmd = cmd.strip().decode()
        except:
            return ""

        if len(cmd) == 0:
            return ""
        else:
            cmd_list = cmd.split()

        return self.parse(cmd, cmd_list)

    def parse(self, cmd, cmd_list):
        if cmd_list[0] == "register":
            return self.register_handler(cmd_list)

        elif cmd_list[0] == "login":
            return self.login_handler(cmd_list)

        elif cmd_list[0] == "logout":
            return self.logout_handler()

        elif cmd_list[0] == "whoami":
            return self.whoami_handler()

        elif cmd_list[0] == "exit":
            return -1

        else:
            return f"command not found: {cmd}\n"

    def register_handler(self, cmd_list):
        if len(cmd_list) != 4:
            return "Usage: register <username> <email> <password>\n"

        username = cmd_list[1]
        email = cmd_list[2]
        password = cmd_list[3]

        res = self.db.create_user(username, email, password)
        if res == 0:
            return "Register successfull.\n"
        elif res == 1:
            return "Username is already use.\n"

    def login_handler(self, cmd_list):
        if len(cmd_list) != 3:
            return "Usage: login <username> <password>\n"

        username = cmd_list[1]
        password = cmd_list[2]

        if self.user != None:
            return "Please logout first.\n"

        res = self.db.login(username, password)
        if res == 0:
            self.user = username
            return f"Welcome, {username}.\n"
        elif res == 1:
            return "Login failed.\n"

    def logout_handler(self):
        if self.user:
            res = f"Bye, {self.user}.\n"
            self.user = None
            return res
        else:
            return "Please login first.\n"

    def whoami_handler(self):
        if self.user:
            return f"{self.user}\n"
        else:
            return "Please login first.\n"


class BBS(threading.Thread):
    def __init__(self, socket, address):
        threading.Thread.__init__(self)
        self.socket = socket
        self.address = address
        self.controller = Controller()

    def run(self):
        print(f"New Connection.")
        self.socket.send(b"********************************\n")
        self.socket.send(b"** Welcome to the BBS server. **\n")
        self.socket.send(b"********************************\n")

        while True:
            self.socket.send(b"% ")
            cmd = self.socket.recv(1024)
            ret = self.controller.execute(cmd)
            if ret == -1:
                break
            if len(ret) > 0:
                self.socket.send(ret.encode())

        self.socket.close()


def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((BBS_HOST, BBS_PORT))
    s.listen()

    while True:
        client_socket, client_addr = s.accept()
        BBS(client_socket, client_addr).start()


if __name__ == "__main__":
    main()
