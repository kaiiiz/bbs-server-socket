from bbs_db import BBS_DB
from constant import DB_HOST, DB_PORT, DB_USERNAME, DB_PWD
import re


class BBS_Controller():
    def __init__(self):
        self.db = BBS_DB(DB_HOST, DB_PORT, DB_USERNAME, DB_PWD)
        self.user = None
        self.uid = None

    def execute(self, cmd):
        try:
            cmd = cmd.strip().decode()
        except:
            return ""

        if len(cmd) == 0:
            return ""

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

        elif cmd_list[0] == "create-board":
            return self.create_board_handler(cmd_list)

        elif cmd_list[0] == "create-post":
            return self.create_post_handler(cmd)

        elif cmd_list[0] == "exit":
            return -1

        else:
            return f"command not found: {cmd}\n"

    def create_post_handler(self, cmd):
        regex = r'(create-post)\s*([^\s]+)\s*--title(.+)--content(.+)'
        try:
            search = re.search(regex, cmd)
            board_name = search.group(2)
            post_title = search.group(3).strip()
            post_content = search.group(4).strip()
        except AttributeError:
            return "Usage: create-post <board-name> --title <title> --content <content>\n"

        if not self.user:
            return "Please login first.\n"

        res = self.db.create_post(self.uid, board_name, post_title, post_content)
        return res.message

    def create_board_handler(self, cmd_list):
        if len(cmd_list) != 2:
            return "Usage: create-board <name>\n"

        if not self.user:
            return "Please login first.\n"

        boardname = cmd_list[1]

        res = self.db.create_board(boardname)
        return res.message

    def register_handler(self, cmd_list):
        if len(cmd_list) != 4:
            return "Usage: register <username> <email> <password>\n"

        username = cmd_list[1]
        email = cmd_list[2]
        password = cmd_list[3]

        res = self.db.create_user(username, email, password)
        return res.message

    def login_handler(self, cmd_list):
        if len(cmd_list) != 3:
            return "Usage: login <username> <password>\n"

        username = cmd_list[1]
        password = cmd_list[2]

        if self.user:
            return "Please logout first.\n"

        else:
            res = self.db.login(username, password)
            if res.success:
                self.user = username
                self.uid = res.data['uid']
            return res.message

    def logout_handler(self):
        if not self.user:
            return "Please login first.\n"

        else:
            res = f"Bye, {self.user}.\n"
            self.user = None
            self.uid = None
            return res

    def whoami_handler(self):
        if not self.user:
            return "Please login first.\n"

        else:
            return f"{self.user}\n"
