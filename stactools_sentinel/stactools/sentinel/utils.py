import os
import re
from lxml import etree


def mtd_asset_key_from_path(path):
    filename = os.path.split(path)[1]
    mapping = {
        'MTD_MSIL2A.xml': 'product-metadata',
        'INSPIRE.xml': 'inspire-metadata',
        'MTD_DS.xml': 'datastrip-metadata',
        'MTD_TL.xml': 'granule-metadata',
        'manifest.safe': 'safe-manifest'
    }
    key = mapping[filename]
    if key is None:
        raise ValueError(f'unexpected metadata file: {filename}')
    return key


def band_index_to_name(index):
    raw_band_id = index + 1
    if raw_band_id == 9:
        band_id = '8A'
    elif raw_band_id > 9:
        band_id = str(raw_band_id - 1)
    else:
        band_id = str(raw_band_id)
    return f'B{band_id.rjust(2, "0")}'


def mgrs_from_path(path):
    results = re.search(r'_T(\d{2}[a-zA-Z]{3})_', path)
    if results is not None:
        return results.group(1)
    return results


def clean_path(path, extension=None):
    # remove all superfluous dots and slashes
    cleaned = os.path.normpath(path)
    # if the path should have an extension, ensure it does
    if extension is not None:
        cleaned = f'{os.path.splitext(cleaned)[0]}.{extension}'
    return cleaned


def open_xml_file_root(path):
    return etree.parse(path).getroot()


def get_xml_node(root, xpath):
    return root.find(xpath, root.nsmap)


def list_xml_node(root, xpath):
    return root.findall(xpath, root.nsmap)


def get_xml_node_text(root, xpath):
    node = root.find(xpath, root.nsmap)
    if node is not None:
        return node.text
    return None


def get_xml_node_attr(root, attr, xpath=None):
    node = root
    if xpath is not None:
        node = root.find(xpath, root.nsmap)

    if node is not None:
        return node.get(attr)

    return None
