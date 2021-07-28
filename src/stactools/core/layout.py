import os

from pystac import Catalog
from pystac.layout import TemplateLayoutStrategy

from stactools.core import move_all_assets


def layout_catalog(catalog: Catalog,
                   item_path_template: str,
                   create_subcatalogs: bool = False,
                   remove_existing_subcatalogs: bool = False,
                   move_assets: bool = False) -> Catalog:
    """Modify the layout of a STAC.

    Given a catalog and a layout template, modify the layout of the STAC
    to either generate subcatalogs based on item properties, or create subdirectories
    to organize item properties. Both of these are based on the template string
    provided. See the ``LayoutTemplate`` PySTAC API docs for more information on
    template strings.

    Args:
        catalog (Catalog or Collection): The Catalog or Collection to change the layout of.
        item_path_template (str): A string that represents a path of item properties,
            e.g. "${year}/${month}"
        create_subcatalogs (bool): If True, create subcatalogs for each of the
            template directory levels using the item properties to determine which
            catalog it belongs to.
        remove_existing_subcatalogs (bool): If True, apply the subcatalogs to all
            items throughout the catalog and clear any child catalogs, using
            the newly generated subcatalogs or item paths.
        move_assets (bool): If True, the assets of the Items will be moved alongside
            of the Items. Otherwise the asset will remain in place, with the moved
            Item's asset HREFs reflecting the existing location.

    Returns:
        Catalog or Collection: The passed in Catalog. This operation mutates the catalog.
    """

    if remove_existing_subcatalogs:
        items = catalog.get_all_items()
        for item in items:
            parent = item.get_parent()
            assert parent is not None
            parent.remove_item(item.id)
            catalog.add_item(item)

        catalog.clear_children()

    if create_subcatalogs:
        catalog.generate_subcatalogs(template=item_path_template)
        catalog.normalize_hrefs(os.path.dirname(catalog.self_href))
    else:
        strategy = TemplateLayoutStrategy(item_template=item_path_template)
        catalog.normalize_hrefs(os.path.dirname(catalog.self_href),
                                strategy=strategy)

    if move_assets:
        move_all_assets(catalog, ignore_conflicts=True)

    return catalog
