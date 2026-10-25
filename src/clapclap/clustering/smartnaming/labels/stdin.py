import sys


def get_stdin_labels():
    return set(sys.stdin.read().replace("\r", "").split("\n")) - set([""])
