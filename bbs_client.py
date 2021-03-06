#! /usr/bin/env python3

import socket
import threading
import argparse
import queue
import os
import signal
import boto3
import string
import random
import json
import time
import re
import uuid
from kafka import KafkaProducer, KafkaConsumer
from abc import ABCMeta, abstractmethod
from collections import defaultdict

from bbs_cmd_parser import BBS_Command_Parser
from constant import KAFKA_SERVER, KAFKA_PORT

parser = argparse.ArgumentParser()
parser.add_argument("host")
parser.add_argument("port")
args = parser.parse_args()

HOST = args.host
PORT = int(args.port)

def gen_random_bucker_name(prefix):
    prefix = prefix.replace(" ", "-").replace("_", "-")
    fill_size = 62 - len(prefix)
    suffix = ''.join([random.choice(string.ascii_lowercase + string.digits) for n in range(fill_size)])
    return (prefix + '.' + suffix).lower()

def gen_random_name(prefix):
    prefix = prefix.replace(" ", "_")
    fill_size = 62 - len(prefix)
    suffix = ''.join([random.choice(string.ascii_lowercase + string.digits) for n in range(fill_size)])
    return prefix + '.' + suffix

class BBS_Notifier:
    def __init__(self):
        self.producer = KafkaProducer(bootstrap_servers=[f"{KAFKA_SERVER}:{KAFKA_PORT}"],
                                      value_serializer=lambda m: json.dumps(m).encode())

    def publish(self, board_name, post_title, post_author):
        data = {
            "board_name": board_name,
            "post_title": post_title,
            "post_author": post_author,
        }
        self.producer.send(f"board_{board_name}", data)
        self.producer.send(f"author_{post_author}", data)

class BBS_Subsciber(threading.Thread):
    def __init__(self, alive):
        threading.Thread.__init__(self)
        self.alive = alive
        self.board_sub = defaultdict(set)
        self.author_sub = defaultdict(set)
        self.consumer = None

    def subscribe_board(self, board_name, keyword):
        if keyword in self.board_sub[board_name]:
            return "Already subscribed\n"
        else:
            self.board_sub[board_name].add(keyword)
            self.renew_consumer()
            return "Subscribe successfully\n"

    def subscribe_author(self, author_name, keyword):
        if keyword in self.author_sub[author_name]:
            return "Already subscribed\n"
        else:
            self.author_sub[author_name].add(keyword)
            self.renew_consumer()
            return "Subscribe successfully\n"

    def unsubscribe_board(self, board_name):
        if board_name not in self.board_sub:
            return f"You haven't subscribed {board_name}\n"
        else:
            self.board_sub.pop(board_name)
            self.renew_consumer()
            return "Unsubscribe successfully\n"

    def unsubscribe_author(self, author_name):
        if author_name not in self.author_sub:
            return f"You haven't subscribed {author_name}\n"
        else:
            self.author_sub.pop(author_name)
            self.renew_consumer()
            return "Unsubscribe successfully\n"

    def list_sub(self):
        board_output = []
        for board_name, kws in self.board_sub.items():
            kw_str = ", ".join(kws)
            board_output.append(f"{board_name}: {kw_str}")
        if len(board_output):
            print("Board: " + "; ".join(board_output))

        author_output = []
        for author_name, kws in self.author_sub.items():
            kw_str = ", ".join(kws)
            author_output.append(f"{author_name}: {kw_str}")
        if len(author_output):
            print("Author: " + "; ".join(author_output))

    def renew_consumer(self):
        sub_list = []
        for k in self.board_sub:
            sub_list.append(f"board_{k}")
        for k in self.author_sub:
            sub_list.append(f"author_{k}")

        if self.consumer is not None:
            self.consumer.close()

        if len(sub_list) > 0:
            self.consumer = KafkaConsumer(*sub_list,
                                          group_id=str(uuid.uuid4()),
                                          bootstrap_servers=[f"{KAFKA_SERVER}:{KAFKA_PORT}"],
                                          value_deserializer=lambda m: json.loads(m.decode()))
        else:
            self.consumer = None

    def print_record(self, topic, board_name, post_title, post_author):
        # get keyword
        try:
            board_regex = r"board_(.+)"
            search = re.search(board_regex, topic)
            board_name = search.group(1)
            kws = self.board_sub[board_name]
        except:
            try:
                author_regex = r"author_(.+)"
                search = re.search(author_regex, topic)
                author_name = search.group(1)
                kws = self.author_sub[author_name]
            except:
                print("Invalid topic")
                return

        # filter post by keyword
        for kw in kws:
            if kw in post_title:
                print(f"*[{board_name}] {post_title} - by {post_author}*")
                break

    def run(self):
        while self.alive.is_set():
            try:
                message = self.consumer.poll(timeout_ms=1000)
                for topic_partition, records in message.items():
                    topic = topic_partition.topic
                    for r in records:
                        board_name = r.value["board_name"]
                        post_title = r.value["post_title"]
                        post_author = r.value["post_author"]
                        self.print_record(topic, board_name, post_title, post_author)
            except:
                time.sleep(1)
                continue

        if self.consumer is not None:
            self.consumer.close()

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
        self.my_username = None
        self.notifier = None
        self.subscriber = None

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
            return self.mail_to_handler(receiver=cmd_list[1], subject=cmd_list[2], content=cmd_list[3])

        elif cmd_type == "list-mail":
            return self.list_mail_handler()

        elif cmd_type == "retr-mail":
            return self.retr_mail_handler(mail_id=cmd_list[1])

        elif cmd_type == "delete-mail":
            return self.delete_mail_handler(mail_id=cmd_list[1])

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
            return self.exit_handler()


    def register_handler(self, username, email, password):
        valid_check = self.socket.recv(1024).decode()
        if valid_check == "Username is already used.":
            return "Username is already used.\n"

        # valid username, create bucket
        bucket_name = gen_random_bucker_name(f"bbs.client.{username}")
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

        self.my_username = username
        self.notifier = BBS_Notifier()
        self.subscriber = BBS_Subsciber(self.alive)
        self.subscriber.start()
        # retrieve bucket name from server
        self.bucket_name = valid_check
        self.bucket = self.s3.Bucket(self.bucket_name)
        return f"Welcome, {username}.\n"

    def logout_handler(self):
        self.my_username = None
        self.notifier = None
        self.subscriber = None
        return self.socket.recv(1024).decode() + '\n'

    def whoami_handler(self):
        return self.socket.recv(1024).decode() + '\n'

    def create_board_handler(self, board_name):
        valid_check = self.socket.recv(1024).decode()
        if valid_check == "Client doesn't log in.":
            return "Please login first.\n"
        if valid_check == "Board already exist.":
            return "Board already exist.\n"
        return valid_check + '\n'

    def create_post_handler(self, board_name, title, content):
        valid_check = self.socket.recv(1024).decode()
        if valid_check == "Client doesn't log in.":
            return "Please login first.\n"
        if valid_check == "Board does not exist.":
            return "Board does not exist.\n"

        tmp_file = f"./tmp"
        post_obj = {
            "content": content,
            "comments": [],
        }
        with open(tmp_file, "w") as tmp:
            tmp.write(json.dumps(post_obj))

        post_obj_name = gen_random_name(f"bbs.post.{title}")
        self.bucket.upload_file(tmp_file, post_obj_name)
        os.remove(tmp_file)

        self.notifier.publish(board_name, title, self.my_username)

        # store metadata of post
        self.socket.sendall(post_obj_name.encode())
        return self.socket.recv(1024).decode() + '\n'

    def list_board_handler(self, condition):
        return self.socket.recv(1024).decode()

    def list_post_handler(self, board_name, condition):
        valid_check = self.socket.recv(1024).decode()
        if valid_check == "Board does not exist.":
            return "Board does not exist.\n"
        return valid_check

    def read_post_handler(self, post_id):
        valid_check = self.socket.recv(1024).decode()
        if valid_check == "Post does not exist.":
            return "Post does not exist.\n"

        post_meta = json.loads(valid_check)
        post_owner_bucket_name = post_meta["bucket_name"]
        post_obj_name = post_meta["post_obj_name"]

        post_owner_bucket = self.s3.Bucket(post_owner_bucket_name)
        post_obj = json.loads(post_owner_bucket.Object(post_obj_name).get()['Body'].read().decode())
        post_content = post_obj['content']
        post_comments = post_obj['comments']

        def format_meta(field, msg): return f"\t{field:10}:{msg}\n"
        output = ""
        output += format_meta("Author", post_meta['author'])
        output += format_meta("Title", post_meta['title'])
        output += format_meta("Date", post_meta['date'])
        output += "\t--\n"
        output += "\t" + post_content.replace("<br>", "\n\t") + '\n'
        output += "\t--\n"
        for c in post_comments:
            output += f"\t{c['user']}:{c['content']}\n"
        return output

    def delete_post_handler(self, post_id):
        valid_check = self.socket.recv(1024).decode()
        if valid_check == "Client doesn't log in.":
            return "Please login first.\n"
        if valid_check == "Post does not exist.":
            return "Post does not exist.\n"
        if valid_check == "Not the post owner.":
            return "Not the post owner.\n"

        post_obj_name = valid_check
        post_obj = self.bucket.Object(post_obj_name)
        post_obj.delete()
        return "Delete successfully.\n"

    def update_post_handler(self, post_id, specifier, value):
        valid_check = self.socket.recv(1024).decode()
        if valid_check == "Client doesn't log in.":
            return "Please login first.\n"
        if valid_check == "Post does not exist.":
            return "Post does not exist.\n"
        if valid_check == "Not the post owner.":
            return "Not the post owner.\n"

        if specifier == "content":
            post_obj_name = valid_check
            post_obj = json.loads(self.bucket.Object(post_obj_name).get()['Body'].read().decode())
            post_obj['content'] = value

            tmp_file = f"./tmp"
            with open(tmp_file, "w") as tmp:
                tmp.write(json.dumps(post_obj))
            self.bucket.upload_file(tmp_file, post_obj_name)
            os.remove(tmp_file)

        return "Update successfully.\n"

    def comment_handler(self, post_id, comment):
        valid_check = self.socket.recv(1024).decode()
        if valid_check == "Client doesn't log in.":
            return "Please login first.\n"
        if valid_check == "Post does not exist.":
            return "Post does not exist.\n"

        post_meta = json.loads(valid_check)
        post_owner_bucket_name = post_meta["bucket_name"]
        post_obj_name = post_meta["post_obj_name"]

        post_owner_bucket = self.s3.Bucket(post_owner_bucket_name)
        post_obj = json.loads(post_owner_bucket.Object(post_obj_name).get()['Body'].read().decode())
        post_obj["comments"].append({
            "user": self.my_username,
            "content": comment,
        })

        tmp_file = f"./tmp"
        with open(tmp_file, "w") as tmp:
            tmp.write(json.dumps(post_obj))
        post_owner_bucket.upload_file(tmp_file, post_obj_name)
        os.remove(tmp_file)

        return "Comment successfully.\n"

    def mail_to_handler(self, receiver, subject, content):
        valid_check = self.socket.recv(1024).decode()
        if valid_check == "Client doesn't log in.":
            return "Please login first.\n"
        if valid_check == "Receiver doesn't exist.":
            return f"{receiver} does not exist.\n"

        receiver_bucket_name = valid_check
        receiver_bucker = self.s3.Bucket(receiver_bucket_name)

        mail_obj_name = gen_random_name(f"bbs.mail.{subject}")

        tmp_file = f"./tmp"
        with open(tmp_file, "w") as tmp:
            tmp.write(content)
        receiver_bucker.upload_file(tmp_file, mail_obj_name)
        os.remove(tmp_file)

        self.socket.send(mail_obj_name.encode())
        return self.socket.recv(1024).decode() + '\n'

    def list_mail_handler(self):
        valid_check = self.socket.recv(1024).decode()
        if valid_check == "Client doesn't log in.":
            return "Please login first.\n"

        return valid_check

    def retr_mail_handler(self, mail_id):
        valid_check = self.socket.recv(1024).decode()
        if valid_check == "Client doesn't log in.":
            return "Please login first.\n"
        if valid_check == "Mail doesn't exist.":
            return f"No such mail.\n"

        mail_meta = json.loads(valid_check)
        mail_obj_name = mail_meta["mail_obj_name"]
        mail_content = self.bucket.Object(mail_obj_name).get()['Body'].read().decode()

        def format_meta(field, msg): return f"\t{field:10}:{msg}\n"
        output = ""
        output += format_meta("Subject", mail_meta['subject'])
        output += format_meta("From", mail_meta['from'])
        output += format_meta("Date", mail_meta['date'])
        output += "\t--\n"
        output += "\t" + mail_content.replace("<br>", "\n\t") + '\n'
        return output

    def delete_mail_handler(self, mail_id):
        valid_check = self.socket.recv(1024).decode()
        if valid_check == "Client doesn't log in.":
            return "Please login first.\n"
        if valid_check == "Mail doesn't exist.":
            return f"No such mail.\n"

        mail_obj_name = valid_check
        mail_obj = self.bucket.Object(mail_obj_name)
        mail_obj.delete()
        return "Mail deleted.\n"

    def subscribe_board_handler(self, board_name, keyword):
        valid_check = self.socket.recv(1024).decode()
        if valid_check == "Client doesn't log in.":
            return "Please login first.\n"
        return self.subscriber.subscribe_board(board_name, keyword)

    def subscribe_author_handler(self, author_name, keyword):
        valid_check = self.socket.recv(1024).decode()
        if valid_check == "Client doesn't log in.":
            return "Please login first.\n"
        return self.subscriber.subscribe_author(author_name, keyword)

    def unsubscribe_board_handler(self, board_name):
        valid_check = self.socket.recv(1024).decode()
        if valid_check == "Client doesn't log in.":
            return "Please login first.\n"
        return self.subscriber.unsubscribe_board(board_name)

    def unsubscribe_author_handler(self, author_name):
        valid_check = self.socket.recv(1024).decode()
        if valid_check == "Client doesn't log in.":
            return "Please login first.\n"
        return self.subscriber.unsubscribe_author(author_name)

    def list_sub_handler(self):
        valid_check = self.socket.recv(1024).decode()
        if valid_check == "Client doesn't log in.":
            return "Please login first.\n"
        self.subscriber.list_sub()
        return ""

    def exit_handler(self):
        self.alive.clear()
        return ""


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
        alive.clear()


if __name__ == '__main__':
    main()
