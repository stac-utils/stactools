import json
from typing import Any, Dict, Optional

import click
from pystac import Collection
from pystac.summaries import Summarizer


def format_summary(summary: Dict[str, Any], indent: int = 4) -> str:
    out = ""
    for var in summary:
        if type(summary[var]) == dict:
            out += var + ": \n" + " " * indent + str(summary[var]) + "\n"
        else:
            out += var + ": " + str(summary[var]) + "\n"
    return out


def create_summary_command(cli: click.Group) -> click.Command:
    @cli.command("summary", short_help="Summarize a STAC collection's contents.")
    @click.argument("href")
    @click.option(
        "-f",
        "--fields",
        help=(
            "the path to the json file with field descriptions. "
            "If no file is passed, a default one will be used."
        ),
    )
    @click.option(
        "-u",
        "--update",
        is_flag=True,
        default=False,
        help=(
            "Instead of printing the summary information, "
            "update the collection itself, then print it to stdout."
        ),
    )
    @click.option(
        "-i",
        "--inplace",
        is_flag=True,
        default=False,
        help=(
            "If updating, update the collection in-place, "
            "instead of printing it to stdout."
        ),
    )
    def summary_command(
        href: str, fields: Optional[str], update: bool, inplace: bool
    ) -> None:
        collection = Collection.from_file(href)
        summaries = Summarizer(fields).summarize(collection)
        if update:
            collection.summaries = summaries
            if inplace:
                collection.save_object(include_self_link=False, dest_href=href)
            else:
                print(json.dumps(collection.to_dict(include_self_link=False), indent=2))
        else:
            print(format_summary(summaries.to_dict()))

    return summary_command
