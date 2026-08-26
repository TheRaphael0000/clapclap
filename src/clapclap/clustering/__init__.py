from __future__ import annotations
import logging
import argparse
from argparse import _SubParsersAction, ArgumentParser

from clapclap.clustering.clustering import Clustering


logger = logging.getLogger("CLI")


def add_subparser(subparsers: _SubParsersAction[ArgumentParser]):
    clustering_subparser = subparsers.add_parser(
        "clustering", 
        help="DB Query operations",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    # clustering_subparser.add_argument("--json", "-j", action="store_true", help="Return a json formatted string")
    clustering_subparser.add_argument("--limit", "-l", type=int, default=100, help="Number of results per clusters")
    clustering_subparser.add_argument("--save", "-s", action="store_true", help="Save to navidrome playlist")
    smart_naming_group = clustering_subparser.add_mutually_exclusive_group(required=False)
    smart_naming_group.add_argument("--no-smart-naming", action="store_true", help="Disable playlist smart-naming")
    smart_naming_group_arguments = smart_naming_group.add_mutually_exclusive_group(required=False)
    smart_naming_group_arguments.add_argument("--smart-naming-size", type=int, default=2, help="Number of genres for the smart-naming")
    smart_naming_group_arguments.add_argument("--smart-naming-sep", type=str, default="|", help="Smart naming separator")
    clustering_subparser.add_argument("--prefix", "-p", default="clusters/", type=str, help="Playlist name prefix")

    clustering_subparsers = clustering_subparser.add_subparsers(required=True)

    clustering_kmeans_parser = clustering_subparsers.add_parser(
        "kmeans", 
        help="K-Means",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    clustering_kmeans_parser.add_argument("--n_clusters", "-k", type=int, default=20, help="Number of clusters")
    clustering_kmeans_parser.set_defaults(func=kmean_command)


def kmean_command(args):
    from clapclap.clustering.kmeans import KMeansClustering
    clustering = Clustering(limit=args.limit, save=args.save, smart_naming=not args.no_smart_naming, smart_naming_size=args.smart_naming_size, smart_naming_sep=args.smart_naming_sep, prefix=args.prefix, method=KMeansClustering(k=args.n_clusters))
    clustering.process()

