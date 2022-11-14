from typing import Any, Dict

import click
import pystac
from pystac import Catalog, Collection


def format_summary(summary: Dict[str, Any], indent: int = 4) -> str:
    out = ""
    for var in summary:
        if type(summary[var]) == dict:
            out += var + ": \n" + " " * indent + str(summary[var]) + "\n"
        else:
            out += var + ": " + str(summary[var]) + "\n"
    return out


def print_summaries(collection_path: str, force_resummary: bool = False) -> None:
    col = pystac.read_file(collection_path)
    if isinstance(col, Collection):
        orig_summaries = col.summaries.to_dict()
        if force_resummary or len(orig_summaries) == 0:
            new_summaries = pystac.summaries.Summarizer().summarize(col).to_dict()
            if len(orig_summaries) == 0:
                print(
                    "Collection's summaries were empty. Printing recalculated summaries:"
                )
            print(format_summary(new_summaries))
        else:
            print(format_summary(orig_summaries))
    elif isinstance(col, Catalog):
        print("Input is a catalog, not a collection.")
        print(
            "Run 'stac describe -h {}' to discover collections in this catalog".format(
                collection_path
            )
        )
        return
    else:
        print("{} is not a collection".format(collection_path))
        return


def create_summary_command(cli: click.Group) -> click.Command:
    @cli.command("summary", short_help="Summarize a STAC collection's contents.")
    @click.option(
        "-f",
        "--force_resummary",
        is_flag=True,
        default=False,
        help="Ignore existing summaries in the collection and print recalculated summaries",
    )
    @click.argument("collection_path")
    def summary_command(collection_path: str, force_resummary: bool) -> None:
        print_summaries(collection_path, force_resummary)

    return summary_command
