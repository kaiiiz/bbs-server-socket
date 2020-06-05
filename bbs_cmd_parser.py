import threading
import re


class BBS_Command_Parser:
    def parse(self, cmd):
        try:
            cmd = cmd.strip()
        except:
            return ()

        if len(cmd) == 0:
            return ()

        cmd_list = cmd.split()

        # return value
        cmd_type = cmd_list[0]
        parse_status = True

        if cmd_type == "register":
            if len(cmd_list) == 4:
                parse_list = cmd_list
            else:
                parse_status = False
                parse_list = ()

        elif cmd_type == "login":
            if len(cmd_list) == 3:
                parse_list = cmd_list
            else:
                parse_status = False
                parse_list = ()

        elif cmd_type == "logout":
            if len(cmd_list) == 1:
                parse_list = cmd_list
            else:
                parse_status = False
                parse_list = ()

        elif cmd_type == "whoami":
            if len(cmd_list) == 1:
                parse_list = cmd_list
            else:
                parse_status = False
                parse_list = ()

        elif cmd_type == "create-board":
            if len(cmd_list) == 2:
                parse_list = cmd_list
            else:
                parse_status = False
                parse_list = ()

        elif cmd_type == "create-post":
            regex = r"(create-post)\s+(\S+)\s+--title\s+(.+)\s+--content\s+(.+)"
            try:
                search = re.search(regex, cmd)
                board_name = search.group(2)
                post_title = search.group(3).strip()
                post_content = search.group(4).strip()
                parse_list = ("create-post", board_name, post_title, post_content)
            except:
                parse_status = False
                parse_list = ()

        elif cmd_type == "list-board":
            if len(cmd_list) == 1:
                parse_list = cmd_list
            else:
                regex = r"list-board\s+##(.+)"
                try:
                    condition = re.search(regex, cmd).group(1)
                    parse_list = ("list-board", condition)
                except:
                    parse_status = False
                    parse_list = ()

        elif cmd_type == "list-post":
            if len(cmd_list) == 2:
                parse_list = cmd_list
            else:
                regex = r"list-post\s+(\S+)\s+##(.+)"
                try:
                    search = re.search(regex, cmd)
                    board_name = search.group(1)
                    condition = search.group(2)
                    parse_list = ("list-post", board_name, condition)
                except:
                    parse_status = False
                    parse_list = ()

        elif cmd_type == "read":
            if len(cmd_list) == 2:
                parse_list = cmd_list
            else:
                parse_status = False
                parse_list = ()

        elif cmd_type == "delete-post":
            if len(cmd_list) == 2:
                parse_list = cmd_list
            else:
                parse_status = False
                parse_list = ()

        elif cmd_type == "update-post":
            regex = r"(update-post)\s+(\S+)\s+--(title|content)\s+(.+)"
            try:
                search = re.search(regex, cmd)
                post_id = search.group(2)
                specifier = search.group(3)
                value = search.group(4)
                parse_list = ("update-post", post_id, specifier, value)
            except:
                parse_status = False
                parse_list = ()

        elif cmd_type == "comment":
            regex = r'comment\s+(\d+)\s+(.+)'
            try:
                search = re.search(regex, cmd)
                post_id = search.group(1)
                comment = search.group(2)
                parse_list = ("comment", post_id, comment)
            except:
                parse_status = False
                parse_list = ()

        elif cmd_type == "mail-to":
            regex = r'mail-to\s+(\S+)\s+--subject\s+(.+)\s+--content\s+(.+)'
            try:
                search = re.search(regex, cmd)
                username = search.group(1)
                subject = search.group(2).strip()
                content = search.group(3).strip()
                parse_list = ("mail-to", username, subject, content)
            except:
                parse_status = False
                parse_list = ()

        elif cmd_type == "list-mail":
            if len(cmd_list) == 1:
                parse_list = cmd_list
            else:
                parse_status = False
                parse_list = ()

        elif cmd_type == "retr-mail":
            if len(cmd_list) == 2:
                parse_list = cmd_list
            else:
                parse_status = False
                parse_list = ()

        elif cmd_type == "delete-mail":
            if len(cmd_list) == 2:
                parse_list = cmd_list
            else:
                parse_status = False
                parse_list = ()

        elif cmd_type == "subscribe":
            sub_board_regex = r"subscribe\s+--board\s+(.+)\s+--keyword\s+(.+)"
            try:
                search = re.search(sub_board_regex, cmd)
                board_name = search.group(1)
                keyword = search.group(2)
                parse_list = ("subscribe-board", board_name, keyword)
            except:
                sub_author_regex = r"subscribe\s+--author\s+(.+)\s+--keyword\s+(.+)"
                try:
                    search = re.search(sub_author_regex, cmd)
                    author_name = search.group(1)
                    keyword = search.group(2)
                    parse_list = ("subscribe-author", author_name, keyword)
                except:
                    parse_status = False
                    parse_list = ()

        elif cmd_type == "unsubscribe":
            sub_board_regex = r"unsubscribe\s+--board\s+(.+)"
            try:
                search = re.search(sub_board_regex, cmd)
                board_name = search.group(1)
                parse_list = ("unsubscribe-board", board_name)
            except:
                sub_author_regex = r"unsubscribe\s+--author\s+(.+)"
                try:
                    search = re.search(sub_author_regex, cmd)
                    author_name = search.group(1)
                    parse_list = ("unsubscribe-author", author_name)
                except:
                    parse_status = False
                    parse_list = ()

        elif cmd_type == "list-sub":
            if len(cmd_list) == 1:
                parse_list = cmd_list
            else:
                parse_status = False
                parse_list = ()

        elif cmd_type == "exit":
            if len(cmd_list) == 1:
                parse_list = cmd_list
            else:
                parse_status = False
                parse_list = ()

        else:
            raise Exception("Parse Error: Command not found!")

        return cmd_type, parse_status, tuple(parse_list)

    def usage(self, cmd_type):
        if cmd_type == "register":
            return "Usage: register <username> <email> <password>"

        elif cmd_type == "login":
            return "Usage: login <username> <password>"

        elif cmd_type == "logout":
            return "Usage: logout"

        elif cmd_type == "whoami":
            return "Usage: whoami"

        elif cmd_type == "create-board":
            return "Usage: create-board <name>"

        elif cmd_type == "create-post":
            return "Usage: create-post <board-name> --title <title> --content <content>"

        elif cmd_type == "list-board":
            return "Usage: list-board ##<key>"

        elif cmd_type == "list-post":
            return "Usage: list-post <board-name> ##<key>"

        elif cmd_type == "read":
            return "Usage: read <post-id>"

        elif cmd_type == "delete-post":
            return "Usage: delete-post <post-id>"

        elif cmd_type == "update-post":
            return "Usage: update-post <post-id> --title/content <new>"

        elif cmd_type == "comment":
            return "Usage: comment <post-id> <comment>"

        elif cmd_type == "mail-to":
            return "Usage: mail-to <username> --subject <subject> --content <content>"

        elif cmd_type == "list-mail":
            return "Usage: list-mail"

        elif cmd_type == "retr-mail":
            return "Usage: retr-mail <mail#>"

        elif cmd_type == "delete-mail":
            return "Usage: delete-mail <mail#>"

        elif cmd_type == "subscribe":
            return "Usage: subscribe --board/author <board-name>/<author-name> --keyword <keyword>"

        elif cmd_type == "unsubscribe":
            return "Usage: unsubscribe --board/author <board-name>/<author-name>"

        elif cmd_type == "list-sub":
            return "Usage: list-sub"

        elif cmd_type == "exit":
            return "Usage: exit"

        else:
            raise Exception("Parse Error: Command not found!")
