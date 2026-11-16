from __future__ import annotations
import argparse
from argparse import _SubParsersAction, ArgumentParser
from clapclap.utils.logger import logger


def add_subparser(subparsers: _SubParsersAction[ArgumentParser]):
    subparser = subparsers.add_parser(
        "tools",
        help="Tools operations",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    tools_subparsers = subparser.add_subparsers(required=True)

    metadata_subparser = tools_subparsers.add_parser(
        "metadata",
        help="Query metadata on files",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    metadata_subparser.add_argument(
        "--no-fingerprint",
        "-f",
        action="store_true",
        help="Don't look for non-fingerprinted files"
    )
    metadata_subparser.add_argument(
        "--no-replay-gain",
        "-r",
        action="store_true",
        help="Don't look for no replay-gain files"
    )

    metadata_subparser.set_defaults(func=command_metadata)


def command_metadata(args):
    from .metadata import Metadata
    logger.debug("command tool")
    print("Starting metadata checker")
    metadata_ = Metadata(
        no_fingerprint=args.no_fingerprint,
        no_replaygain=args.no_replay_gain
    )
    metadata_.run()
    print("Metadata checker completed")
