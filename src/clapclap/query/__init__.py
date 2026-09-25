from __future__ import annotations
import argparse
from argparse import _SubParsersAction, ArgumentParser

from .similarity_query import SimilarityQuery
from clapclap.utils.log import logger


def add_subparser(subparsers: _SubParsersAction[ArgumentParser]):
    query_subparser = subparsers.add_parser(
        "query", 
        help="DB Query operations",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    group = query_subparser.add_mutually_exclusive_group(required=True)
    group.add_argument("--json", "-j", action="store_true", help="Return a json formatted string")
    group.add_argument("--quiet", "-q", action="store_true", help="Don't print the playlist")
    query_subparser.add_argument("--limit", "-l", type=int, default=20, help="Number of results")
    query_subparser.add_argument("--temperature", "-t", type=float, default=0, help="Standard deviation of the noise to add to the centroid [0,1]")
    query_subparser.add_argument("--save", "-s", action="store_true", help="Save to navidrome playlist")
    query_subparser.add_argument("--name", "-n", type=str, help="Name of the playlist")
    query_subparser.add_argument("--interactive-save", "-i", action="store_true", help="Prompt for save after print")

    query_subparsers = query_subparser.add_subparsers(required=True)

    query_similarity_parser = query_subparsers.add_parser(
        "similarity", 
        help="Similarity query",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    group = query_similarity_parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--path", "-p", type=str, help="The relative path to a file in the DB")
    group.add_argument("--songId", "-s", type=str, help="Query by songId")
    group.add_argument("--albumId", "-a", type=str, help="Query by albumId")
    group.add_argument("--artistId", "-r", type=str, help="Query by artistId")
    query_similarity_parser.add_argument("--json", "-j", action="store_true", help="Return a json formatted string")
    query_similarity_parser.set_defaults(func=similarity_command)

    query_text_parser = query_subparsers.add_parser(
        "text", 
        help="Text query",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    query_text_parser.add_argument("text", type=str, help="Text to query")
    query_text_parser.set_defaults(func=query_text_command)


def process_query(query, args, name):
    if not args.quiet:
        if args.json:
            print(query.get_json())
        else:
            print(query.get_text())
    
    save = args.save
    name = name or "unnamed"

    if args.interactive_save:
        result = input(f"Save playlist '{name}'? (y/N): ")
        save = result.lower() == "y"

    if save:
        query.save_to_playlist(name)

def similarity_command(args):
    logger.debug("command query simlilarity")
    query = SimilarityQuery(limit=args.limit, temperature=args.temperature, path=args.path, songId=args.songId, albumId=args.albumId, artistId=args.artistId)
    process_query(query, args, args.name)


def query_text_command(args):
    logger.debug("command query text")
    from .text_query import TextQuery
    query = TextQuery(limit=args.limit, temperature=args.temperature, text=args.text)
    process_query(query, args, args.name or args.text)

