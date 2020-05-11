import socket
import threading
import os
import sys
from bbs_controller import BBS_Controller
from constant import BBS_HOST, BBS_PORT


class BBS(threading.Thread):
    def __init__(self, socket, address):
        threading.Thread.__init__(self)
        self.socket = socket
        self.address = address
        self.controller = BBS_Controller()

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
