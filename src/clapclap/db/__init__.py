from __future__ import annotations
from .Embedding import Embedding
from .DB import DB
from .Base import Base
import argparse
from argparse import _SubParsersAction, ArgumentParser
from clapclap.utils.logger import logger


def add_subparser(subparsers: _SubParsersAction[ArgumentParser]):
    subparser = subparsers.add_parser(
        "db",
        help="DB operations",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    group = subparser.add_mutually_exclusive_group(required=True)
    group.add_argument("--create", action="store_true",
                       help="Create the database")
    group.add_argument("--drop", action="store_true", help="Drop the database")

    subparser.set_defaults(func=command)


def command(args):
    logger.debug("command update")
    db = DB()
    if args.drop:
        print("Dropping database")
        db.drop()
        print("Database dropped")
    if args.create:
        print("Creating database")
        db.create()
        print("Database created")
