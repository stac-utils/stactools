from typing import Callable, Optional

from lxml import etree


def map_type(typ: Callable, v: Optional[str]) -> Optional[int]:
    return v if v is None else typ(v)


def band_index_to_name(index):
    raw_band_id = index + 1
    if raw_band_id == 9:
        band_id = '8A'
    elif raw_band_id > 9:
        band_id = str(raw_band_id - 1)
    else:
        band_id = str(raw_band_id)
    return f'B{band_id.rjust(2, "0")}'


def extract_gsd(image_path: str) -> float:
    return float(image_path[-7:-5])
