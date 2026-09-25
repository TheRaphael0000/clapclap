from __future__ import annotations
import argparse
from argparse import _SubParsersAction, ArgumentParser

from clapclap.utils.log import logger

def add_subparser(subparsers: _SubParsersAction[ArgumentParser]):
    navidrome_parser = subparsers.add_parser(
        "navidrome", 
        help="Navidrome operations",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    navidrome_subparsers = navidrome_parser.add_subparsers(required=True)

    update_parser = navidrome_subparsers.add_parser(
        "update", 
        help="Update ids using navidrome",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    update_parser.add_argument("--limit", "-l", type=int, default=-1, help="Only fetch the N last albums, intead of fetching the whole database")
    update_parser.set_defaults(func=command_update)

    scan_parser = navidrome_subparsers.add_parser(
        "scan", 
        help="Call the navidrome scanner",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    scan_parser.add_argument("--wait", "-w", action="store_true", help="Don't start a scan, just wait for a scan to end, detach will be ignored.")
    scan_parser.add_argument("--detach", "-d", action="store_true", help="Don't wait for the scan to end, just send the command")
    scan_parser.add_argument("--full-scan", "-f", action="store_true", help="Full-scan, quick scan by default")
    scan_parser.set_defaults(func=command_scan)

    playlist_parser = navidrome_subparsers.add_parser(
        "playlist", 
        help="Update playlists",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    playlist_parser.add_argument("--regex", "-r", default=".*", help="Regex playlists selection")
    playlist_parser.add_argument("--delete", "-d", action="store_true", help="Delete the selected playlists")
    playlist_parser.add_argument("--stats", "-s", action="store_true", help="Print playlist stats")
    playlist_parser.set_defaults(func=command_playlist)


def command_update(args):
    logger.debug("command navidrome update")
    from .navidrome import Navidrome
    navidrome = Navidrome()
    navidrome.update_ids(limit=args.limit)


def command_scan(args):
    logger.debug("command navidrome scan")
    from .navidrome import Navidrome
    navidrome = Navidrome()
    if not args.wait:
        navidrome.start_scan(args.full_scan)
    if not args.detach or args.wait:
        navidrome.scan_progress()


def command_playlist(args):
    logger.debug("command navidrome playlist")
    from .playlistsManager import PlaylistsManager
    playlistsManager = PlaylistsManager(regex=args.regex, delete=args.delete, stats=args.stats)
    playlistsManager.run()
