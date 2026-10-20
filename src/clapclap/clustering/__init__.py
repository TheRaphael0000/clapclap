from __future__ import annotations
import argparse
from argparse import _SubParsersAction, ArgumentParser
from typing import get_args

from clapclap.clustering.clustering import Clustering
from clapclap.utils.types import GenresList


def add_subparser(subparsers: _SubParsersAction[ArgumentParser]):
    clustering_subparser = subparsers.add_parser(
        "clustering",
        help="Clustering operations / Playlists creations",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    # clustering_subparser.add_argument("--json", "-j", action="store_true", help="Return a json formatted string")
    clustering_subparser.add_argument(
        "--limit", "-l", type=int, default=100, help="Number of results per clusters")
    clustering_subparser.add_argument(
        "--save", "-s", action="store_true", help="Save to navidrome playlist")
    clustering_subparser.add_argument(
        "--no-smart-naming", action="store_true", help="Disable playlist smart-naming")
    clustering_subparser.add_argument(
        "--smart-naming-no-macro-genre", action="store_true", help="Disable macro genre names")
    clustering_subparser.add_argument(
        "--smart-naming-size", type=int, default=2, help="Number of genres for the smart-naming")
    clustering_subparser.add_argument(
        "--smart-naming-sep", type=str, default=",", help="Smart naming separator")
    clustering_subparser.add_argument(
        "--smart-naming-list", type=str, choices=get_args(GenresList), default="musicbrainz", help="Genres List")
    clustering_subparser.add_argument(
        "--prefix", "-p", default="cc/", type=str, help="Playlist name prefix")
    clustering_subparser.add_argument(
        "--no-merge", action="store_true", help="Don't merge clusters with same names")

    clustering_subparsers = clustering_subparser.add_subparsers(required=True)

    clustering_kmeans_parser = clustering_subparsers.add_parser(
        "kmeans",
        help="K-Means",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    clustering_kmeans_parser.add_argument(
        "--no_reduction", "-n", action="store_true", help="Disable UMAP reduction")
    clustering_kmeans_parser.add_argument(
        "--n_clusters", "-k", type=int, default=20, help="The number of clusters to form as well as the number of centroids to generate.")
    clustering_kmeans_parser.add_argument(
        "--max_iter", type=int, default=300, help="Maximum number of iterations of the k-means algorithm for a single run.")
    clustering_kmeans_parser.add_argument(
        "--n_init", default="auto", help="Number of times the k-means algorithm is run with different centroid seeds.")
    clustering_kmeans_parser.set_defaults(func=kmean_command)

    clustering_agglomerative_parser = clustering_subparsers.add_parser(
        "agglomerative",
        help="Agglomerative Clustering",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    clustering_agglomerative_parser.add_argument(
        "--n_clusters", "-k", type=int, default=20, help="Number of clusters")
    clustering_agglomerative_parser.set_defaults(func=agglomerative_command)

    clustering_dbscan_parser = clustering_subparsers.add_parser(
        "dbscan",
        help="DBSCAN Clustering",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    clustering_dbscan_parser.add_argument(
        "--eps", "-e", type=float, default=0.5, help="The maximum distance between two samples for one to be considered as in the neighborhood of the other.")
    clustering_dbscan_parser.add_argument(
        "--min_samples", type=int, default=10, help="The number of samples (or total weight) in a neighborhood for a point to be considered as a core point.")
    clustering_dbscan_parser.set_defaults(func=dbscan_command)

    clustering_hdbscan_parser = clustering_subparsers.add_parser(
        "hdbscan",
        help="HDBSCAN Clustering",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    clustering_hdbscan_parser.set_defaults(func=hdbscan_command)


def get_common_args(args):
    return {
        "limit": args.limit,
        "save": args.save,
        "smart_naming": not args.no_smart_naming,
        "smart_naming_size": args.smart_naming_size,
        "smart_naming_sep": args.smart_naming_sep,
        "prefix": args.prefix,
        "smart_naming_macro_genre": not args.smart_naming_no_macro_genre,
        "genres_list": args.smart_naming_list,
        "no_merge": args.no_merge,
    }


def kmean_command(args):
    from clapclap.clustering.kmeans import KMeansMethod
    clustering = Clustering(**get_common_args(args),
                            method=KMeansMethod(k=args.n_clusters, no_reduction=args.no_reduction))
    clustering.process()


def agglomerative_command(args):
    from clapclap.clustering.agglomerative import AgglomerativeClusteringMethod
    clustering = Clustering(
        **get_common_args(args), method=AgglomerativeClusteringMethod(k=args.n_clusters))
    clustering.process()


def dbscan_command(args):
    from clapclap.clustering.dbscan import DBScanMethod
    clustering = Clustering(
        **get_common_args(args), method=DBScanMethod(eps=args.eps, min_samples=args.min_samples))
    clustering.process()


def hdbscan_command(args):
    from clapclap.clustering.hdbscan import HDBScanMethod
    clustering = Clustering(
        **get_common_args(args), method=HDBScanMethod())
    clustering.process()
