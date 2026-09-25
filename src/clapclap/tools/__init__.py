from __future__ import annotations
import argparse
from argparse import _SubParsersAction, ArgumentParser
from clapclap.utils.log import logger

def add_subparser(subparsers: _SubParsersAction[ArgumentParser]):
    subparser = subparsers.add_parser(
        "tools", 
        help="Tools operations",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    subparser.add_argument("--fingerprint", "-f", action="store_true", help="Look for non-fingerprinted files")
    subparser.add_argument("--replay-gain", "-r", action="store_true", help="Look for no replay-gain files")

    subparser.set_defaults(func=command)


def command(args):
    from .metadata import Metadata
    logger.debug("command tool")
    metadata_ = Metadata(fingerprint=args.fingerprint, replaygain=args.replay_gain)
    metadata_.run()