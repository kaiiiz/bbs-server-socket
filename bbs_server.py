import socket
import threading
import os
import sys

from abc import ABCMeta, abstractmethod
from bbs_cmd_parser import BBS_Command_Parser
from constant import BBS_HOST, BBS_PORT


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
    def execute(self, cmd):
        try:
            cmd = cmd.decode().strip('\r\n')
            cmd_type, parse_status, cmd_status = self.parse(cmd)
        except:
            self.socket.send(f"command not found: {cmd}\n".encode())
            return

        if not parse_status:
            self.socket.send(f"{self.usage(cmd_type)}\n".encode())
            return


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
