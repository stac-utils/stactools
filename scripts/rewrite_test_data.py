#!/usr/bin/env python3

import os
from typing import cast

import pystac
from dateutil.tz import UTC
from pystac import Collection, Item

root = os.path.dirname(os.path.dirname(__file__))
directory = os.path.join(root, "tests", "data-files")

invalid_file_names = ["area-1-1-imagery-invalid.json"]


def remap_property(item: Item, before: str, after: str) -> None:
    value = item.properties.pop(before, None)
    if value:
        item.properties[after] = value


collection_id = None
for directory, _, file_names in os.walk(directory):
    for file_name in file_names:
        if os.path.splitext(file_name)[1] != ".json":
            continue
        path = os.path.join(directory, file_name)
        try:
            object = pystac.read_file(path)
        except Exception as e:
            print(f"FIX REQUIRED: {path}")
            raise e

        if object.STAC_OBJECT_TYPE == "Collection":
            collection = cast(Collection, object)
            collection_id = collection.id
            for i, interval in enumerate(collection.extent.temporal.intervals):
                for j, datetime in enumerate(interval):
                    if datetime:
                        collection.extent.temporal.intervals[i][j] = (
                            datetime.astimezone(UTC)
                        )

        if object.STAC_OBJECT_TYPE == "Feature":
            item = cast(Item, object)
            remap_property(item, "label:property", "label:properties")
            remap_property(item, "label:method", "label:methods")
            remap_property(item, "label:task", "label:tasks")
            remap_property(item, "proj:epsg_code", "proj:epsg")
            remap_property(item, "eo:epsg", "proj:epsg")
            remap_property(item, "eo:off_nadir", "view:off_nadir")
            remap_property(item, "eo:sun_azimuth", "view:sun_azimuth")
            remap_property(item, "eo:sun_elevation", "view:sun_elevation")

            if item.collection_id is None and item.get_single_link("collection"):
                item.collection_id = collection_id

            for key, asset in item.assets.items():
                bands = asset.extra_fields.pop("eo:bands", None)
                if bands:
                    item.assets[key].extra_fields["eo:bands"] = [
                        {"name": str(band)} for band in bands
                    ]

        if file_name not in invalid_file_names:
            try:
                object.validate()
            except Exception as e:
                print(f"FIX REQUIRED: {path}")
                raise e
        object.save_object(include_self_link=False, dest_href=path)
