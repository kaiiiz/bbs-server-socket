#! /usr/bin/env python3

import socket
import threading
import argparse
import queue
import os
import signal

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

    def socket_protector(func):
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
                # self.check_connection()
                continue

        self.socket.close()
        os.kill(os.getpid(), signal.SIGINT)

    @abstractmethod
    def execute(self, cmd):
        pass


class BBS_Client(BBS_Client_Socket, BBS_Command_Parser):
    def __init__(self, cmd_q, reply_q, alive):
        BBS_Client_Socket.__init__(self, cmd_q, reply_q, alive)

    def execute(self, cmd):
        self.socket.send(cmd.encode())
        return self.socket.recv(1024).decode()


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
                cmd_q.put(cmd)
                res = reply_q.get()
                print(res, end='')
    except:
        pass


if __name__ == '__main__':
    main()
