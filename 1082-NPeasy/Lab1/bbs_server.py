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


class BBS(threading.Thread):
    def __init__(self, socket, address, db):
        threading.Thread.__init__(self)
        self.socket = socket
        self.address = address
        self.db = db

    def run(self):
        print(f'New Connection.')

        while True:
            self.socket.send('% '.encode())
            cmd = self.socket.recv(1024).strip()
            ret = self.cmd_handler(cmd)

        self.socket.close()

    def cmd_handler(self, cmd):
        print(cmd)


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
