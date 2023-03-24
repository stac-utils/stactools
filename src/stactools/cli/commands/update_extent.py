import json

import click
from pystac import Collection


def create_update_extent_command(cli: click.Group) -> click.Command:
    @cli.command("update-extent", short_help="Update a STAC collection's extent.")
    @click.argument("href")
    @click.option(
        "-i",
        "--inplace",
        is_flag=True,
        default=False,
        help="Update the collection in-place, instead of printing it to stdout.",
    )
    def update_extent_command(href: str, inplace: bool) -> None:
        collection = Collection.from_file(href)
        collection.update_extent_from_items()
        if inplace:
            collection.save_object(include_self_link=False, dest_href=href)
        else:
            print(json.dumps(collection.to_dict(include_self_link=False), indent=2))

    return update_extent_command
