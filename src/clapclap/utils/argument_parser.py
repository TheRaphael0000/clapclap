import argparse
from importlib.metadata import version

from clapclap.update import add_subparser as add_subparser_update
from clapclap.clustering import add_subparser as add_subparser_clustering
from clapclap.navidrome import add_subparser as add_subparser_navidrome
from clapclap.db import add_subparser as add_subparser_db
from clapclap.query import add_subparser as add_subparser_query
from clapclap.serve import add_subparser as add_subparser_serve
from clapclap.tools import add_subparser as add_subparser_tools
from clapclap.utils.config import config


def parse():
    parser = argparse.ArgumentParser(
        prog="clapclap CLI",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
# This automatically adds a --version flag and prints the version
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {version('clapclap')}"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="count",
        default=0,
        help="Increase verbosity (-v for INFO, -vv for DEBUG)"
    )
    parser.add_argument("--config", type=str, help="Path to the config file",
                        default=config.default_config_path())

    subparsers = parser.add_subparsers(
        dest="command",
        title="subcommands",
        description="valid subcommands",
        required=True,
    )

    add_subparser_db(subparsers)
    add_subparser_clustering(subparsers)
    add_subparser_navidrome(subparsers)
    add_subparser_query(subparsers)
    add_subparser_serve(subparsers)
    add_subparser_update(subparsers)
    add_subparser_tools(subparsers)

    args = parser.parse_args()

    return args
