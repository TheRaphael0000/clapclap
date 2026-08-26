import argparse

from clapclap.update import add_subparser as add_subparser_update
from clapclap.navidrome import add_subparser as add_subparser_navidrome
from clapclap.db import add_subparser as add_subparser_db
from clapclap.query import add_subparser as add_subparser_query
from clapclap.serve import add_subparser as add_subparser_serve
from clapclap.tools import add_subparser as add_subparser_tools
from clapclap.utils.config import config


def parse():
    parser = argparse.ArgumentParser(
        prog="Clapclap CLI",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--debug", action="store_true", help="Show debug logs")
    parser.add_argument("--config", type=str, help="Path to the config file", default=config.default_config_path())

    subparsers = parser.add_subparsers(
        dest="command",
        title="subcommands",
        description="valid subcommands",
        required=True,
    )

    add_subparser_db(subparsers)
    add_subparser_navidrome(subparsers)
    add_subparser_query(subparsers)
    add_subparser_serve(subparsers)
    add_subparser_update(subparsers)
    add_subparser_tools(subparsers)

    args = parser.parse_args()

    return args