import socket
import threading

HOST = ''
PORT = 8000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))
s.listen(10)

clients = []
lock = threading.Lock()


class BBS(threading.Thread):
    def __init__(self, socket, address):
        threading.Thread.__init__(self)
        self.socket = socket
        self.address = address

    def run(self):
        lock.acquire()
        clients.append(self)
        lock.release()
        print(f'{self.address} connected')

        while True:
            cmd = self.socket.recv(1024).decode().strip()
            ret = self.cmd_handler(cmd)

    def cmd_handler(self, cmd):
        print(cmd)


def main():
    while True:
        client_socket, client_addr = s.accept()
        BBS(client_socket, client_addr).start()


if __name__ == '__main__':
    main()
