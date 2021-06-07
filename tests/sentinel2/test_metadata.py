import unittest

from shapely.geometry import box, mapping, shape

from stactools.core.projection import reproject_geom
from stactools.sentinel2.safe_manifest import SafeManifest
from stactools.sentinel2.product_metadata import ProductMetadata
from stactools.sentinel2.granule_metadata import GranuleMetadata

from tests.utils import TestData


class Sentinel2MetadataTest(unittest.TestCase):
    def test_parses_product_metadata_properties(self):
        manifest_path = TestData.get_path(
            'data-files/sentinel2/S2A_MSIL2A_20190212T192651_N0212_R013_T07HFE_20201007T160857.SAFE'
        )

        manifest = SafeManifest(manifest_path)

        product_metadata = ProductMetadata(manifest.product_metadata_href)
        granule_metadata = GranuleMetadata(manifest.granule_metadata_href)

        s2_props = product_metadata.metadata_dict
        s2_props.update(granule_metadata.metadata_dict)

        expected = {
            # From product metadata
            's2:product_uri':
            'S2A_MSIL2A_20190212T192651_N0212_R013_T07HFE_20201007T160857.SAFE',
            's2:generation_time': '2020-10-07T16:08:57.135Z',
            's2:processing_baseline': '02.12',
            's2:product_type': 'S2MSI2A',
            's2:datatake_id': 'GS2A_20190212T192651_019029_N02.12',
            's2:datatake_type': 'INS-NOBS',
            's2:datastrip_id':
            'S2A_OPER_MSI_L2A_DS_ESRI_20201007T160858_S20190212T192646_N02.12',
            's2:granule_id':
            'S2A_OPER_MSI_L2A_TL_ESRI_20201007T160858_A019029_T07HFE_N02.12',
            's2:mgrs_tile': '07HFE',
            's2:reflectance_conversion_factor': 1.02763689829235,

            # From granule metadata
            's2:degraded_msi_data_percentage': 0.0,
            's2:nodata_pixel_percentage': 96.769553,
            's2:saturated_defective_pixel_percentage': 0.0,
            's2:dark_features_percentage': 0.0,
            's2:cloud_shadow_percentage': 0.0,
            's2:vegetation_percentage': 0.000308,
            's2:not_vegetated_percentage': 0.069531,
            's2:water_percentage': 48.349833,
            's2:unclassified_percentage': 0.0,
            's2:medium_proba_clouds_percentage': 14.61311,
            's2:high_proba_clouds_percentage': 24.183494,
            's2:thin_cirrus_percentage': 12.783723,
            's2:snow_ice_percentage': 0.0,
            's2:mean_solar_zenith': 32.707073851362,
            's2:mean_solar_azimuth': 62.3286549448294
        }

        for k, v in expected.items():
            self.assertIn(k, s2_props)
            self.assertEqual(s2_props[k], v)

        self.assertEqual(granule_metadata.cloudiness_percentage, 51.580326)

    def test_footprint_containing_geom_with_z_dimension(self):
        product_md_path = TestData.get_path(
            'data-files/sentinel2/S2A_MSIL2A_20150826T185436_N0212_R070'
            '_T11SLT_20210412T023147/MTD_MSIL2A.xml')
        granule_md_path = TestData.get_path(
            'data-files/sentinel2/S2A_MSIL2A_20150826T185436_N0212_R070'
            '_T11SLT_20210412T023147/MTD_TL.xml')
        product_metadata = ProductMetadata(product_md_path)
        granule_metadata = GranuleMetadata(granule_md_path)

        footprint = shape(product_metadata.geometry)

        proj_bbox = granule_metadata.proj_bbox
        epsg = granule_metadata.epsg

        proj_box = box(*proj_bbox)
        ll_proj_box = shape(
            reproject_geom(f"epsg:{epsg}", "epsg:4326", mapping(proj_box)))

        # Test that the bboxes roughly match by ensuring the difference
        # is less than 5% of total area of the reprojected proj bbox.
        self.assertTrue(
            footprint.envelope.difference(ll_proj_box).area < (
                ll_proj_box.area * 0.05))
