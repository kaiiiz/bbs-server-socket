import threading
import re


class BBS_Command_Parser(threading.Thread):
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
            regex = r"(update-post)\s+(\d+)\s+--(title|content)\s+(.+)"
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

        elif cmd_type == "exit":
            if len(cmd_list) == 1:
                parse_list = cmd_list
            else:
                parse_status = False
                parse_list = ()

        else:
            raise Exception("Parse Error: Command not found!")

        return cmd_type, parse_status, tuple(parse_list)
