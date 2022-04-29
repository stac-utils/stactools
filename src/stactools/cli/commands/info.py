import click
import pystac
from pystac import Catalog, STACObject


def print_info(
    catalog_path: str, skip_items: bool = False, print_progress: bool = False
) -> None:
    cat_count, col_count, item_count = 0, 0, 0
    cat_ext, col_ext, item_ext = set([]), set([]), set([])

    cat = pystac.read_file(catalog_path)
    if not isinstance(cat, Catalog):
        print("{} is not a catalog".format(catalog_path))
        return

    cat_id_info = "Catalog ID: {}".format(cat.id)

    max_line_length = 0

    def progress_print(root: STACObject) -> None:
        nonlocal max_line_length
        line = (
            f"\rCatalogs={cat_count}, Collections={col_count}, "
            f"Items={item_count}: Reading {root}"
        )
        if len(line) > max_line_length:
            max_line_length = len(line)
        print("\r" + " " * max_line_length, end="")
        print(line, end="")

    for root, _, items in cat.walk():
        if root.STAC_OBJECT_TYPE == pystac.STACObjectType.COLLECTION:
            col_count += 1
            if root.stac_extensions is not None:
                for ext in root.stac_extensions:
                    col_ext.add(ext)
        else:
            cat_count += 1
            if root.stac_extensions is not None:
                for ext in root.stac_extensions:
                    cat_ext.add(ext)
        if not skip_items:
            for item in items:
                item_count += 1
                if item.stac_extensions is not None:
                    for ext in item.stac_extensions:
                        item_ext.add(ext)
        if print_progress:
            progress_print(root)

    cat_ext_info = "(extensions: {})".format(",".join(cat_ext)) if cat_ext else ""
    col_ext_info = "(extensions: {})".format(",".join(col_ext)) if col_ext else ""
    item_ext_info = "(extensions: {})".format(",".join(item_ext)) if item_ext else ""

    cat_text = "   CATALOGS: {} {}".format(cat_count, cat_ext_info)
    col_text = "COLLECTIONS: {} {}".format(col_count, col_ext_info)
    item_text = "      ITEMS: {} {}".format(item_count, item_ext_info)

    lines = [cat_id_info, "-" * len(cat_id_info), cat_text, col_text]
    if not skip_items:
        lines.append(item_text)

    print("\r" + " " * max_line_length, end="")
    output = "\n".join(lines)
    print(f"\r{output}")


def create_info_command(cli: click.Group) -> click.Command:
    @cli.command("info", short_help="Display info about a static STAC catalog.")
    @click.argument("catalog_path")
    @click.option("-s", "--skip_items", is_flag=True, help="Skip counting items")
    @click.option(
        "--progress/--no-progress",
        default=True,
        help="Display and update the output info while reading the catalog.",
    )
    def info_command(catalog_path: str, skip_items: bool, progress: bool) -> None:
        print_info(catalog_path, skip_items, progress)

    return info_command


def create_describe_command(cli: click.Group) -> click.Command:
    @cli.command(
        "describe",
        short_help="Prints out a list of all catalogs, collections and items "
        "in this STAC.",
    )
    @click.argument("catalog_path")
    @click.option(
        "-h", "--include-hrefs", is_flag=True, help="Include HREFs in description."
    )
    def describe_command(catalog_path: str, include_hrefs: bool) -> None:
        cat = pystac.read_file(catalog_path)
        if not isinstance(cat, pystac.Catalog):
            print("{} is not a catalog".format(catalog_path))
            return
        cat.describe(include_hrefs=include_hrefs)

    return describe_command
