import os
import random
import getpass
from robobrowser import RoboBrowser

from . import cf_io_utils

root = '7'
cache_loc = os.path.join(os.environ['HOME'], '.cache', 'cf_submit')
config_loc = os.path.join(cache_loc, "config.json")
config = cf_io_utils.read_data_from_file(config_loc)
if config is None:
    config = dict()


# converter

def decode(s):
    global root
    res = ""
    length = len(s)
    i = 0
    while i < length:
        rng = ord(s[i]) - ord(root)
        jump = ord(s[i + 1]) - ord(root)
        temp = 0
        for j in range(0, rng):
            temp += ord(s[i + j + 2]) - ord(root) - jump
        res += str(chr(temp))
        i += rng + 2
    return res


def encode(s):
    global root
    res = ""
    length = len(s)
    for i in range(0, length):
        rng = random.randint(1, 20)
        res += str(chr(rng + ord(root)))
        jump = random.randint(1, 10)
        res += str(chr(jump + ord(root)))
        curr = ord(s[i])
        for j in range(0, rng - 1):
            temp = random.randint(0, min(curr, 2 + int(curr / (rng - j))))
            res += str(chr(temp + ord(root) + jump))
            curr -= temp
        res += str(chr(curr + ord(root) + jump))
    return res


# set login

def set_login(handle=None):
    if handle is None:
        handle = input("Handle: ")
    password = getpass.getpass("Password: ")

    browser = RoboBrowser(parser="lxml")
    browser.open("http://codeforces.com/enter")
    enter_form = browser.get_form("enterForm")
    enter_form["handleOrEmail"] = handle
    enter_form["password"] = password
    browser.submit_form(enter_form)

    checks = list(map(lambda x: x.getText()[1:].strip(),
                      browser.select("div.caption.titled")))
    if handle not in checks:
        print("Login Failed.")
        return
    else:
        config["handle"] = handle
        config["password"] = encode(password)
        cf_io_utils.write_data_in_file(config, config_loc)
        print("Successfully logged in as " + handle)


# login

def login():
    handle = config["handle"]
    password = decode(config.get("password", None))

    browser = RoboBrowser(parser="lxml")
    browser.open("http://codeforces.com/enter")
    enter_form = browser.get_form("enterForm")
    enter_form["handleOrEmail"] = handle
    enter_form["password"] = password
    browser.submit_form(enter_form)

    checks = list(map(lambda x: x.getText()[
                  1:].strip(), browser.select("div.caption.titled")))
    if handle not in checks:
        print("Login Corrupted.")
        return None
    else:
        return browser
