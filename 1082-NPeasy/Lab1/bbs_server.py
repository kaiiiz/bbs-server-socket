import socket
import threading
import os
from dotenv import load_dotenv
from bbs_db import BBS_DB

load_dotenv()

BBS_HOST = os.getenv('BBS_SERVER_IP')
BBS_PORT = int(os.getenv('BBS_SERVER_PORT'))
BBS_MAX_CLIENT = int(os.getenv('BBS_MAX_CLIENT'))
DB_USERNAME = os.getenv('DB_ROOT_USERNAME')
DB_PWD = os.getenv('DB_ROOT_PWD')


class Shell():
    def __init__(self, db):
        self.db = db
        self.user = None

    def parse(self, cmd):
        try:
            cmd = cmd.strip().decode()
        except:
            return ''

        if len(cmd) == 0:
            return ''
        else:
            cmd_list = cmd.split()

        return self.handle(cmd_list)

    def handle(self, cmd_list):
        if cmd_list[0] == 'register':
            return self.register_handler(cmd_list)

        elif cmd_list[0] == 'login':
            return self.login_handler(cmd_list)

        else:
            return f'command not found: {cmd}\n'

    def register_handler(self, cmd_list):
        if len(cmd_list) != 4:
            return 'usage: register <username> <email> <password>\n'

        username = cmd_list[1]
        email = cmd_list[2]
        password = cmd_list[3]

        return self.db.create_user(username, email, password)


class BBS(threading.Thread):
    def __init__(self, socket, address, db):
        threading.Thread.__init__(self)
        self.socket = socket
        self.address = address
        self.shell = Shell(db)

    def run(self):
        print(f'New Connection.')

        while True:
            self.socket.send(b'% ')
            cmd = self.socket.recv(1024)
            ret = self.shell.parse(cmd)
            if len(ret) > 0:
                self.socket.send(ret.encode())

        self.socket.close()


def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((BBS_HOST, BBS_PORT))
    s.listen(BBS_MAX_CLIENT)

    db = BBS_DB(DB_USERNAME, DB_PWD)

    while True:
        client_socket, client_addr = s.accept()
        BBS(client_socket, client_addr, db).start()


if __name__ == '__main__':
    main()
