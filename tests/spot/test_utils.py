from collections import OrderedDict
import unittest
import fiona

from tests.utils import TestData

# Test cases, file names to keys and values that should exist.
schema = {
    'properties': OrderedDict([('NAME', 'str:50')]), 
    'geometry': 'Polygon'}

src0 = {
    'type': 'Feature',
    'id': '0',
    'properties': OrderedDict([('NAME', 'S5_09537_5435_20070531')]),
    'geometry': {'type': 'Polygon',
    'coordinates': [[
        (-78528.00240865147, 598573.004153735),
        (-58279.99927707571, 653731.9967474313),
        (-181.00179570007555, 632649.0025307061),
        (-20390.002998122636, 577274.0012620063),
        (-78528.00240865147, 598573.004153735)]]}}

crs = {
    'proj': 'lcc',
    'lat_0': 49,
    'lon_0': -95,
    'lat_1': 77,
    'lat_2': 49,
    'x_0': 0,
    'y_0': 0,
    'datum': 'NAD83',
    'units': 'm',
    'no_defs': True}

def write_test_index(test_index_path):

    with fiona.open(
        test_index_path, mode='w', driver='ESRI Shapefile', schema=schema, crs=crs
        ) as output:
        output.write(src0)
