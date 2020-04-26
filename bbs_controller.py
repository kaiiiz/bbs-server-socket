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
            cmd = cmd.decode().strip('\r\n')
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

        elif cmd_list[0] == "list-board":
            return self.list_board_handler(cmd)

        elif cmd_list[0] == "list-post":
            return self.list_post_handler(cmd, cmd_list)

        elif cmd_list[0] == "read":
            return self.read_post_handler(cmd_list)

        elif cmd_list[0] == "delete-post":
            return self.delete_post_handler(cmd_list)

        elif cmd_list[0] == "update-post":
            return self.update_post_handler(cmd)

        elif cmd_list[0] == "comment":
            return self.comment_handler(cmd)

        elif cmd_list[0] == "exit":
            return -1

        else:
            return f"command not found: {cmd}\n"

    def comment_handler(self, cmd):
        regex = r'comment\s+(\d+)\s+(.+)'
        try:
            search = re.search(regex, cmd)
            post_id = search.group(1)
            comment = search.group(2)
        except AttributeError:
            return "Usage: comment <post-id> <comment>\n"

        if not self.user:
            return "Please login first.\n"

        res = self.db.comment(post_id, comment, self.uid)
        return res.message

    def update_post_handler(self, cmd):
        regex = r'(update-post)\s+(\d+)\s+--(title|content)\s+(.+)'
        try:
            search = re.search(regex, cmd)
            post_id = search.group(2)
            specifier = search.group(3)
            value = search.group(4)
        except AttributeError:
            return "Usage: update-post <post-id> --title/content <new>\n"

        if not self.user:
            return "Please login first.\n"

        res = self.db.update_post(post_id, specifier, value, self.uid)
        return res.message

    def delete_post_handler(self, cmd_list):
        if len(cmd_list) != 2:
            return "Usage: delete-post <post-id>\n"

        if not self.user:
            return "Please login first.\n"

        post_id = cmd_list[1]

        res = self.db.delete_post(post_id, self.uid)
        return res.message

    def read_post_handler(self, cmd_list):
        if len(cmd_list) != 2:
            return "Usage: read <post-id>\n"

        post_id = cmd_list[1]

        res = self.db.read_post(post_id)

        if not res.success:
            return res.message

        def format_meta(field, msg): return f"\t{field:10}: {msg}\n"
        output = ""
        output += format_meta("Author", res.data.author.username)
        output += format_meta("Title", res.data.title)
        output += format_meta("Date", res.data.timestamp.strftime(r'%Y-%m-%d'))
        output += "\t--\n"
        output += "\t" + res.data.content.replace("<br>", "\n\t") + '\n'
        output += "\t--\n"
        for c in res.data.comments:
            output += f"\t{c.user.username}: {c.content}\n"
        return output

    def list_post_handler(self, cmd, cmd_list):
        if len(cmd_list) == 2:
            condition = ""
            board_name = cmd_list[1]

        elif len(cmd_list) > 2:
            regex = r'list-post\s+(\S+)\s+##(.+)'
            try:
                search = re.search(regex, cmd)
                board_name = search.group(1)
                condition = search.group(2)
            except AttributeError:
                return "Usage: list-post <board-name> ##<key>\n"

        else:
            return "Usage: list-post <board-name> ##<key>\n"

        res = self.db.list_post(board_name, condition)

        if not res.success:
            return res.message

        max_title_len = 5  # len("Title")
        max_author_len = 6  # len("Author")
        for p in res.data:
            max_title_len = max(max_title_len, len(p.title))
            max_author_len = max(max_author_len, len(p.author.username))

        def format_msg(id, title, author, date):
            return f"\t{id:<10}{title:<{max_title_len + 5}}{author:<{max_author_len + 5}}{date}\n"

        output = format_msg("ID", "Title", "Author", "Date")
        for p in res.data:
            output += format_msg(p.id, p.title, p.author.username, p.timestamp.strftime(r'%m/%d'))
        return output

    def list_board_handler(self, cmd):
        if cmd.strip() == 'list-board':
            condition = ""
        else:
            regex = r'list-board\s+##(.+)'
            try:
                condition = re.search(regex, cmd).group(1)
            except AttributeError:
                return "Usage: list-board ##<key>\n"

        res = self.db.list_board(condition)

        max_name_len = 4  # len("Name")
        for b in res.data:
            max_name_len = max(max_name_len, len(b.name))

        def format_msg(index, name, moderator):
            return f"\t{index:<10}{name:<{max_name_len + 5}}{moderator}\n"

        output = format_msg("Index", "Name", "Moderator")
        for b in res.data:
            output += format_msg(b.id, b.name, b.moderator.username)
        return output

    def create_post_handler(self, cmd):
        regex = r'(create-post)\s+(\S+)\s+--title\s+(.+)\s+--content\s+(.+)'
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

        res = self.db.create_board(boardname, self.uid)
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
