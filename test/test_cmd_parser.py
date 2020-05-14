from bbs_cmd_parser import BBS_Command_Parser

cmd_parser = BBS_Command_Parser()


def test_register():
    cmd = "register"
    assert cmd_parser.parse(cmd) == ("register", False, ())
    cmd = "register a"
    assert cmd_parser.parse(cmd) == ("register", False, ())
    cmd = "register a b"
    assert cmd_parser.parse(cmd) == ("register", False, ())
    cmd = "register a b c"
    assert cmd_parser.parse(cmd) == ("register", True, ("register", "a", "b", "c"))
    cmd = "register a b c d"
    assert cmd_parser.parse(cmd) == ("register", False, ())


def test_login():
    cmd = "login"
    assert cmd_parser.parse(cmd) == ("login", False, ())
    cmd = "login a"
    assert cmd_parser.parse(cmd) == ("login", False, ())
    cmd = "login a b"
    assert cmd_parser.parse(cmd) == ("login", True, ("login", "a", "b"))
    cmd = "login a b c"
    assert cmd_parser.parse(cmd) == ("login", False, ())


def test_logout():
    cmd = "logout"
    assert cmd_parser.parse(cmd) == ("logout", True, ('logout',))
    cmd = "logout a"
    assert cmd_parser.parse(cmd) == ("logout", False, ())


def test_whoami():
    cmd = "whoami"
    assert cmd_parser.parse(cmd) == ("whoami", True, ('whoami',))
    cmd = "whoami a"
    assert cmd_parser.parse(cmd) == ("whoami", False, ())


def test_create_board():
    cmd = "create-board"
    assert cmd_parser.parse(cmd) == ('create-board', False, ())
    cmd = "create-board a"
    assert cmd_parser.parse(cmd) == ('create-board', True, ('create-board', 'a'))
    cmd = "create-board a b"
    assert cmd_parser.parse(cmd) == ('create-board', False, ())


def test_create_post():
    cmd = "create-post"
    assert cmd_parser.parse(cmd) == ('create-post', False, ())
    cmd = "create-post a --title b"
    assert cmd_parser.parse(cmd) == ('create-post', False, ())
    cmd = "create-post a --content b"
    assert cmd_parser.parse(cmd) == ('create-post', False, ())
    cmd = "create-post a --title hello i'm title --content hello i'm content"
    assert cmd_parser.parse(cmd) == ('create-post', True, ('create-post', 'a', "hello i'm title", "hello i'm content"))
    cmd = "create-post a b"
    assert cmd_parser.parse(cmd) == ('create-post', False, ())


def test_list_board():
    cmd = "list-board"
    assert cmd_parser.parse(cmd) == ('list-board', True, ("list-board",))
    cmd = "list-board a"
    assert cmd_parser.parse(cmd) == ('list-board', False, ())
    cmd = "list-board ##a"
    assert cmd_parser.parse(cmd) == ('list-board', True, ('list-board', 'a'))
    cmd = "list-board ## condition"
    assert cmd_parser.parse(cmd) == ('list-board', True, ('list-board', ' condition'))


def test_list_post():
    cmd = "list-post"
    assert cmd_parser.parse(cmd) == ('list-post', False, ())
    cmd = "list-post a"
    assert cmd_parser.parse(cmd) == ('list-post', True, ('list-post', 'a'))
    cmd = "list-post a ## condition"
    assert cmd_parser.parse(cmd) == ('list-post', True, ('list-post', 'a', ' condition'))


def test_read():
    cmd = "read"
    assert cmd_parser.parse(cmd) == ('read', False, ())
    cmd = "read a"
    assert cmd_parser.parse(cmd) == ('read', True, ('read', 'a'))
    cmd = "read a b"
    assert cmd_parser.parse(cmd) == ('read', False, ())


def test_delete_post():
    cmd = "delete-post"
    assert cmd_parser.parse(cmd) == ('delete-post', False, ())
    cmd = "delete-post a"
    assert cmd_parser.parse(cmd) == ('delete-post', True, ('delete-post', 'a'))
    cmd = "delete-post a b"
    assert cmd_parser.parse(cmd) == ('delete-post', False, ())


def test_update_post():
    cmd = "update-post 10 --title abc"
    assert cmd_parser.parse(cmd) == ('update-post', True, ('update-post', '10', 'title', 'abc'))
    cmd = "update-post 10 --content abc"
    assert cmd_parser.parse(cmd) == ('update-post', True, ('update-post', '10', 'content', 'abc'))


def test_comment():
    cmd = "comment"
    assert cmd_parser.parse(cmd) == ('comment', False, ())
    cmd = "comment a"
    assert cmd_parser.parse(cmd) == ('comment', False, ())
    cmd = "comment 10 b"
    assert cmd_parser.parse(cmd) == ('comment', True, ('comment', '10', 'b'))
    cmd = "comment a b c"
    assert cmd_parser.parse(cmd) == ('comment', False, ())


def test_mail_to():
    cmd = "mail-to"
    assert cmd_parser.parse(cmd) == ('mail-to', False, ())
    cmd = "mail-to a --subject b"
    assert cmd_parser.parse(cmd) == ('mail-to', False, ())
    cmd = "mail-to a --content b"
    assert cmd_parser.parse(cmd) == ('mail-to', False, ())
    cmd = "mail-to a --subject hello i'm title --content hello i'm content"
    assert cmd_parser.parse(cmd) == ('mail-to', True, ('mail-to', 'a', "hello i'm title", "hello i'm content"))
    cmd = "mail-to a b"
    assert cmd_parser.parse(cmd) == ('mail-to', False, ())


def test_list_mail():
    cmd = "list-mail"
    assert cmd_parser.parse(cmd) == ("list-mail", True, ('list-mail',))
    cmd = "list-mail a"
    assert cmd_parser.parse(cmd) == ("list-mail", False, ())


def test_retr_mail():
    cmd = "retr-mail"
    assert cmd_parser.parse(cmd) == ('retr-mail', False, ())
    cmd = "retr-mail a"
    assert cmd_parser.parse(cmd) == ('retr-mail', True, ('retr-mail', 'a'))
    cmd = "retr-mail a b"
    assert cmd_parser.parse(cmd) == ('retr-mail', False, ())


def test_delete_mail():
    cmd = "delete-mail"
    assert cmd_parser.parse(cmd) == ('delete-mail', False, ())
    cmd = "delete-mail a"
    assert cmd_parser.parse(cmd) == ('delete-mail', True, ('delete-mail', 'a'))
    cmd = "delete-mail a b"
    assert cmd_parser.parse(cmd) == ('delete-mail', False, ())


def test_exit():
    cmd = "exit"
    assert cmd_parser.parse(cmd) == ("exit", True, ('exit',))
    cmd = "exit a"
    assert cmd_parser.parse(cmd) == ("exit", False, ())
