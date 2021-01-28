def asset_key_from_path(path):
    if "_PVI" in path:
        return "thumbnail"
    elif "MTD_MSIL2A" in path:
        return "product-metadata"
    elif "INSPIRE" in path:
        return "inspire-metadata"
    elif "MTD_TL" in path:
        return "granule-metadata"
    elif "MTD_DS" in path:
        return "datastrip-metadata"
    elif "_TCI_" in path:
        return f"overview-{path[-3:]}"
    return path[-7:].replace("_", "-")

def asset_item_from_path(path):
    if 