import os
import signal
from clapclap.utils.config import config
from clapclap.utils.argument_parser import parse
from clapclap.utils.logger import setup_logger


def exit_all(sig, frame):
    os._exit(0)


def main():
    args = parse()
    setup_logger(args.verbose)
    config.init(args.config)
    signal.signal(signal.SIGINT, exit_all)
    args.func(args)
