import os
import signal
import logging
from clapclap.utils.config import config
from clapclap.utils.argument_parser import parse


def exit_all(sig, frame):
    os._exit(0)


def main():
    args = parse()
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
        logging.getLogger("httpx").setLevel(logging.ERROR)
        logging.getLogger("urllib3").setLevel(logging.ERROR)
        logging.getLogger("huggingface_hub.utils._http").setLevel(logging.ERROR)
        os.environ["TRANSFORMERS_VERBOSITY"] = "error"
        os.environ["HF_HUB_VERBOSITY"] = "error"

    config.init(args.config)

    signal.signal(signal.SIGINT, exit_all)
    args.func(args)