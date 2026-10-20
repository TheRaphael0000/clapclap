from __future__ import annotations
import os
import argparse
from argparse import _SubParsersAction, ArgumentParser
from clapclap.utils.log import logger
from typing import get_args
from clapclap.utils.types import DataSource


def add_subparser(subparsers: _SubParsersAction[ArgumentParser]):
    subparser = subparsers.add_parser(
        "update",
        help="Update operations",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    subparser.add_argument("--source", "-s", type=str, choices=get_args(
        DataSource), default="fs", help="Data source origin")
    subparser.add_argument("--force", action="store_true",
                           help="Process all files yield by the source and override result in DB")
    subparser.add_argument("--full-scan", action="store_true",
                           help="Perform full-scan for the 'fs' source. Will ignore the current quickscan state file, but still update it for next scans")
    subparser.add_argument("--ignore-existing-fingerprint", action="store_true",
                           help="To ignore fingerprint stored in the file tags")
    subparser.add_argument("--batch", "-b", type=int, default=8,
                           help="Number of files processed at the same time, larger numbers take more memory but can be faster")
    subparser.add_argument("--prefetch", "-p", type=int, default=2,
                           help="The number of prefetched batches in memory")
    subparser.add_argument("--workers", "-w", type=int, default=os.process_cpu_count(),
                           help="The maximum number of workers used in a batch")

    subparser.set_defaults(func=command)


def command(args):
    # dynamically load the updater to avoid loading all the torch libs on other commands
    from .updater import Updater
    logger.debug("command update")
    updater = Updater(batch_size=args.batch, max_workers=args.workers, force_process=args.force, full_scan=args.full_scan,
                      prefetch_factor=args.prefetch, ignore_existing_fingerprint=args.ignore_existing_fingerprint, source=args.source)
    updater.start()
