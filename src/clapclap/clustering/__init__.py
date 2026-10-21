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
    clustering_subparser.add_argument(
        "--prefix", "-p", default="cc/", type=str, help="Playlist name prefix")
    clustering_subparser.add_argument(
        "--min-duration", "-m", type=int, default=20, help="Minimal duration [seconds] for a track to be included.")
    clustering_subparser.add_argument(
        "--reduction", "-r", action="store_true", help="Enable UMAP reduction, can improve the quality of clustering but take longer")
    clustering_subparser.add_argument(
        "--reduction_components", "-c", type=int, default=2**5, help="The number of components for the UMAP reduction")
    clustering_subparser.add_argument(
        "--no-save", action="store_true", help="Don't save to clusters as Navidrome playlists")
    clustering_subparser.add_argument(
        "--no-smart-naming", action="store_true", help="Disable playlist smart-naming")
    clustering_subparser.add_argument(
        "--smart-naming-no-macro-genre", action="store_true", help="Disable macro genre names")
    clustering_subparser.add_argument(
        "--smart-naming-size", type=int, default=1, help="Number of genres for the smart-naming")
    clustering_subparser.add_argument(
        "--smart-naming-sep", type=str, default=",", help="Smart naming separator")
    clustering_subparser.add_argument(
        "--smart-naming-list", type=str, choices=get_args(GenresList), default="musicbrainz", help="Genres List")
    clustering_subparser.add_argument(
        "--no-merge", action="store_true", help="Don't merge clusters with same labels. By default will merge clusters of same name to avoid having multiple playlists with the same name, but sometimes keeping them apart can be relevant")
    clustering_subparser.add_argument(
        "--oddities", type=int, default=0, help="If a cluster has a number of tracks less or equal to this value, tracks will be put inside a 'oddities' cluster. 0 to disable")

    clustering_subparsers = clustering_subparser.add_subparsers(required=True)

    clustering_kmeans_parser = clustering_subparsers.add_parser(
        "kmeans",
        help="K-Means",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    clustering_kmeans_parser.add_argument(
        "--n_clusters", "-k", type=int, default=100, help="The number of clusters to form as well as the number of centroids to generate. This depends on your collection size and number of genre. For large collections (>10000), using the square root of your collection size is a good start for this parameter, for smaller ones, keep the default value.")
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
        "min_duration": args.min_duration,
        "reduction": args.reduction,
        "reduction_components": args.reduction_components,
        "prefix": args.prefix,
        "no_smart_naming": args.no_smart_naming,
        "smart_naming_size": args.smart_naming_size,
        "smart_naming_sep": args.smart_naming_sep,
        "smart_naming_no_macro_genre": args.smart_naming_no_macro_genre,
        "genres_list": args.smart_naming_list,
        "no_merge": args.no_merge,
        "oddities": args.oddities,
        "no_save": args.no_save,
    }


def kmean_command(args):
    from clapclap.clustering.kmeans import KMeansMethod
    clustering = Clustering(**get_common_args(args),
                            method=KMeansMethod(k=args.n_clusters, max_iter=args.max_iter, n_init=args.n_init))
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
