import os
import traceback


def log(*args):
    message = " ".join(map(lambda x: str(x), args))
    os.system("logger -p 6 -t automation \""+message+"\"")
    print('\x1b[1;36m' + message + '\x1b[0m')


def warn(*args):
    message = " ".join(map(lambda x: str(x), args))
    os.system("logger -p 4 -t automation \""+message+"\"")
    print('\x1b[1;33m' + message + '\x1b[0m')


def error(e: Exception):
    try:
        message = "Exception {}: <{}>".format(str(e.errno), e.strerror)
    except AttributeError:
        message = "Exception: <{}>".format(str(e))
    os.system("logger -p 3 -t automation \""+message+"\"")
    print('\x1b[1;31m' + message + '\x1b[0m')
    print('\x1b[31m' + "".join(traceback.format_exc()) + '\x1b[0m\n')
