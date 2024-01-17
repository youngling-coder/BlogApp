import re


PWD_MAX_LENGTH = 64
UNAME_MAX_LENGTH = 32
TITLE_MAX_LENGTH = 100
CONTENT_MAX_LENGTH = 500

def check_post_validity(title: str, content: str):
    if not title:
        return "Field 'title' is required!"
    if not content:
        return "Field 'content' is required!"

    if len(title) > TITLE_MAX_LENGTH:
        return "Title can be up to 100 symbols long"
    if len(content) > CONTENT_MAX_LENGTH:
        return "Content can be up to 500 symbols long"
    return 0

def check_password_validity(psw: str):

    if len(psw) > PWD_MAX_LENGTH:
        return "Password is too long!"
    if len(psw) < 8:
        return "Password must be at least 8 symbols long!"
    if not bool(re.search(r'\d', psw)):
        return "Password must contain numbers!"
    if not bool(re.search(r'[a-zA-Z]', psw)):
        return "Password must contain any letters!"
    return 0

def check_username_validity(username: str):

    if len(username) > UNAME_MAX_LENGTH:
        return "Username is too long!"
    if len(username) < 4:
        return "Username must be at least 4 symbols long!"
    if not bool(re.match(r'^[0-9A-Za-z_.-]+$', username)):
        return "Username must contain only nubers, uppercase and lowercase letters and '-', '_' signs!"
    if not bool(re.search(r'[a-zA-Z]', username)):
        return "Username must contain any letters!"

    return 0
