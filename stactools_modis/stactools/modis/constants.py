import pystac
from pystac.extensions.eo import Band

ITEM_COG_IMAGE_NAME = 'cog_image'
ITEM_TIF_IMAGE_NAME = 'tif_image'
ITEM_METADATA_NAME = 'metadata'

MODIS_CATALOG_ELEMENTS = {
    'MODIS/006/MCD43A4': {
        'links': [
            pystac.Link(
                rel='item',
                target='https://www.umb.edu/spectralmass/terra_aqua_modis/v006',
                title='User Guide'),
            pystac.Link(rel='item',
                        target='https://doi.org/10.5067/MODIS/MCD43A2.006',
                        title='Data File')
        ],
        'title':
        'MCD43A4 v006 MODIS/Terra+Aqua Nadir BRDF-Adjusted Reflectance (NBAR)'
        ' Daily L3 Global 500 m SIN Grid',
        'description':
        """
            The Moderate Resolution Imaging Spectroradiometer (MODIS) MCD43A4
             Version 6 Nadir Bidirectional Reflectance Distribution Function
             (BRDF)-Adjusted Reflectance (NBAR) dataset is produced daily using
             16 days of Terra and Aqua MODIS data at 500 meter (m) resolution.
             The view angle effects are removed from the directional reflectances,
             resulting in a stable and consistent NBAR product. Data are temporally
             weighted to the ninth day which is reflected in the Julian date in the
             file name.
            """,
        'provider':
        pystac.Provider(name='NASA LP DAAC at the USGS EROS Center',
                        url=('https://lpdaac.usgs.gov/'),
                        roles=['producer', 'licensor'])
    },
    'MODIS/006/MOD10A1': {
        'links': [
            pystac.Link(rel='item',
                        target='https://doi.org/10.5067/MODIS/MOD10A1.006',
                        title='Documentation'),
            pystac.Link(
                rel='item',
                target='https://doi.org/10.5067/MODIS/MOD10A1.006',
                title=
                'Hall, D. K., V. V. Salomonson, and G. A. Riggs. 2016. MODIS/Terra '
                'Snow Cover Daily L3 Global 500m Grid. Version 6. Boulder, Colorado USA: '
                'NASA National Snow and Ice Data Center Distributed Active Archive Center.'
            )
        ],
        'title':
        'MODIS/Terra Snow Cover Daily L3 Global 500m SIN Grid, Version 6',
        'description':
        """
            This data set contains daily, gridded snow cover and albedo derived from
             radiance data acquired by the Moderate Resolution Imaging Spectroradiometer
             (MODIS) on board the Terra satellite. Snow cover is identified using the
             Normalized Difference Snow Index (NDSI) and a series of screens designed
             to alleviate errors and flag uncertain snow cover detections.
            """,
        'provider':
        pystac.Provider(name='NASA NSIDC DAAC at CIRES',
                        url=('https://doi.org/10.5067/MODIS/MOD10A1.006'),
                        roles=['producer', 'licensor'])
    },
    'MODIS/006/MOD11A1': {
        'links': [
            pystac.Link(
                rel='item',
                target=
                'https://lpdaac.usgs.gov/documents/118/MOD11_User_Guide_V6.pdf',
                title='User Guide'),
            pystac.Link(
                rel='item',
                target=
                'https://ladsweb.modaps.eosdis.nasa.gov/filespec/MODIS/6/MOD11A1',
                title='Data File')
        ],
        'title':
        'MODIS/Terra Land Surface Temperature/Emissivity Daily L3 Global 1 km SIN Grid',
        'description':
        """The MOD11A1 Version 6 product provides daily per-pixel Land Surface
                         Temperature and Emissivity (LST&E) with 1 kilometer (km) spatial
                         resolution in a 1,200 by 1,200 km grid. The pixel temperature value is
                         derived from the MOD11_L2 swath product. Above 30 degrees latitude, some
                         pixels may have multiple observations where the criteria for clear-sky
                         are met. When this occurs, the pixel value is a result of the average
                         of all qualifying observations. Provided along with the daytime and
                         nighttime surface temperature bands are associated quality control
                         assessments, observation times, view zenith angles, and clear-sky coverages
                         along with bands 31 and 32 emissivities from land cover types.""",
        'provider':
        pystac.Provider(name='NASA LP DAAC at the USGS EROS Center',
                        url=('https://doi.org/10.5067/MODIS/MOD11A1.006'),
                        roles=['producer', 'licensor'])
    },
    'MODIS/006/MOD11A2': {
        'links': [
            pystac.Link(
                rel='item',
                target=
                'https://lpdaac.usgs.gov/documents/118/MOD11_User_Guide_V6.pdf',
                title='User Guide'),
            pystac.Link(
                rel='item',
                target=
                'https://ladsweb.modaps.eosdis.nasa.gov/filespec/MODIS/6/MOD11A2',
                title='Data File')
        ],
        'title':
        'MODIS/Terra Land Surface Temperature/Emissivity 8-Day L3 Global 1 km SIN Grid',
        'description':
        """The MOD11A2 Version 6 product provides an average 8-day per-pixel
                         Land Surface Temperature and Emissivity (LST&E) with a 1 kilometer (km)
                         spatial resolution in a 1,200 by 1,200 km grid. Each pixel value in the
                         MOD11A2 is a simple average of all the corresponding MOD11A1 LST pixels
                         collected within that 8-day period. The 8-day compositing period was
                         chosen because twice that period is the exact ground track repeat period
                         of the Terra and Aqua platforms. Provided along with the daytime and
                         nighttime surface temperature bands are associated quality control
                         assessments, observation times, view zenith angles, and clear-sky
                         coverages along with bands 31 and 32 emissivities from land
                         cover types.""",
        'provider':
        pystac.Provider(name='NASA LP DAAC at the USGS EROS Center',
                        url=('https://doi.org/10.5067/MODIS/MOD11A2.006'),
                        roles=['producer', 'licensor'])
    },
    'MODIS/006/MOD21A2': {
        'links': [
            pystac.Link(
                rel='item',
                target=
                'https://lpdaac.usgs.gov/documents/108/MOD21_User_Guide_V6.pdf',
                title='User Guide'),
            pystac.Link(
                rel='item',
                target=
                'https://ladsweb.modaps.eosdis.nasa.gov/filespec/MODIS/6/MOD21A2',
                title='Data File')
        ],
        'title':
        'MODIS/Terra Land Surface Temperature/3-Band Emissivity 8-Day L3 Global 1 km SIN Grid',
        'description':
        """A new suite of Moderate Resolution Imaging Spectroradiometer (MODIS)
            Land Surface Temperature and Emissivity (LST&E) products are available in
            Collection 6. The MOD21 Land Surface Temperatuer (LST) algorithm differs from
            the algorithm of the MOD11 LST products, in that the MOD21 algorithm is based
            on the ASTER Temperature/Emissivity Separation (TES) technique, whereas the
            MOD11 uses the split-window technique. The MOD21 TES algorithm uses a
            physics-based algorithm to dynamically retrieve both the LST and spectral
            emissivity simultaneously from the MODIS thermal infrared bands 29, 31, and 32.
            The TES algorithm is combined with an improved Water Vapor Scaling (WVS)
            atmospheric correction scheme to stabilize the retrieval during very warm and
            humid conditions.

            The MOD21A2 dataset is an 8-day composite LST product that uses an algorithm
            based on a simple averaging method. The algorithm calculates the average from
            all the cloud free MOD21A1D and MOD21A1N daily acquisitions from the 8-day period.
            Unlike the MOD21A1 data sets where the daytime and nighttime acquisitions are
            separate products, the MOD21A2 contains both daytime and nighttime acquisitions as
            separate Science Dataset (SDS) layers within a single Hierarchical Data Format (HDF)
            file. The LST, Quality Control (QC), view zenith angle, and viewing time have separate
            day and night SDS layers, while the values for the MODIS emissivity bands 29, 31, and
            32 are the average of both the nighttime and daytime acquisitions. MOD21A2 products
            are available two months after acquisition due to latency of data inputs. Additional
            details regarding the method used to create this Level 3 (L3) product are available
            in the Algorithm Theoretical Basis Document (ATBD).""",
        'provider':
        pystac.Provider(name='NASA LP DAAC at the USGS EROS Center',
                        url=('https://doi.org/10.5067/MODIS/MOD21A2.006'),
                        roles=['producer', 'licensor'])
    },
    'MODIS/006/MOD13Q1': {
        'links': [
            pystac.Link(
                rel='item',
                target=
                'https://lpdaac.usgs.gov/documents/103/MOD13_User_Guide_V6.pdf',
                title='User Guide'),
            pystac.Link(
                rel='item',
                target=
                'https://ladsweb.modaps.eosdis.nasa.gov/filespec/MODIS/6/MOD13A2',
                title='Data File')
        ],
        'title':
        'MODIS/Terra Vegetation Indices 16-Day L3 Global 250 m SIN Grid',
        'description':
        """The Terra Moderate Resolution Imaging Spectroradiometer (MODIS) Vegetation Indices
    (MOD13Q1) Version 6 data are generated every 16 days at 250 meter (m) spatial resolution
    as a Level 3 product. The MOD13Q1 product provides two primary vegetation layers. The first
    is the Normalized Difference Vegetation Index (NDVI) which is referred to as the continuity
    index to the existing National Oceanic and Atmospheric Administration-Advanced Very High
    Resolution Radiometer (NOAA-AVHRR) derived NDVI. The second vegetation layer is the Enhanced
    Vegetation Index (EVI), which has improved sensitivity over high biomass regions. The algorithm
    chooses the best available pixel value from all the acquisitions from the 16 day period. The
    criteria used is low clouds, low view angle, and the highest NDVI/EVI value.

    Along with the vegetation layers and the two quality layers, the HDF file will have MODIS
    reflectance bands 1 (red), 2 (near-infrared), 3 (blue), and 7 (mid-infrared), as well as four
    observation layers.""",
        'provider':
        pystac.Provider(name='NASA LP DAAC at the USGS EROS Center',
                        url=('https://doi.org/10.5067/MODIS/MOD13Q1.006'),
                        roles=['producer', 'licensor'])
    },
    'MODIS/006/MOD13A1': {
        'links': [
            pystac.Link(
                rel='item',
                target=
                'https://lpdaac.usgs.gov/documents/103/MOD13_User_Guide_V6.pdf',
                title='User Guide'),
            pystac.Link(
                rel='item',
                target=
                'https://ladsweb.modaps.eosdis.nasa.gov/filespec/MODIS/6/MOD13A1',
                title='Data File')
        ],
        'title':
        'MODIS/Terra Vegetation Indices 16-Day L3 Global 500 m SIN Grid',
        'description':
        """The MOD13A1 Version 6 product provides Vegetation Index (VI) values at a per pixel basis
at 500 meter (m) spatial resolution. There are two primary vegetation layers. The first
is the Normalized Difference Vegetation Index (NDVI), which is referred to as the continuity
index to the existing National Oceanic and Atmospheric Administration-Advanced Very High
Resolution Radiometer (NOAA-AVHRR) derived NDVI. The second vegetation layer is the Enhanced
Vegetation Index (EVI), which has improved sensitivity over high biomass regions. The algorithm
for this product chooses the best available pixel value from all the acquisitions from the 16
day period. The criteria used is low clouds, low view angle, and the highest NDVI/EVI value.

Provided along with the vegetation layers and two quality assurance (QA) layers are reflectance
bands 1 (red), 2 (near-infrared), 3 (blue), and 7 (mid-infrared), as well as four observation
layers.""",
        'provider':
        pystac.Provider(name='NASA LP DAAC at the USGS EROS Center',
                        url=('https://doi.org/10.5067/MODIS/MOD13A1.006'),
                        roles=['producer', 'licensor'])
    },
    'MODIS/006/MOD15A2H': {
        'links': [
            pystac.Link(
                rel='item',
                target=
                'https://lpdaac.usgs.gov/documents/624/MOD15_User_Guide_V6.pdf',
                title='User Guide'),
            pystac.Link(
                rel='item',
                target=
                'https://ladsweb.modaps.eosdis.nasa.gov/filespec/MODIS/6/MOD15A2H',
                title='Data File')
        ],
        'title':
        'MODIS/Terra Leaf Area Index/FPAR 8-Day L4 Global 500 m SIN Grid',
        'description':
        """The MOD15A2H Version 6 Moderate Resolution Imaging Spectroradiometer (MODIS) combined Leaf Area
Index (LAI) and Fraction of Photosynthetically Active Radiation (FPAR) product is an 8-day
composite dataset with 500 meter (m) pixel size. The algorithm chooses the “best” pixel available
from all the acquisitions of the Terra sensor from within the 8-day period.

LAI is defined as the one-sided green leaf area per unit ground area in broadleaf canopies and
as one-half the total needle surface area per unit ground area in coniferous canopies. FPAR is
defined as the fraction of incident photosynthetically active radiation, 400-700 nanometers (nm),
absorbed by the green elements of a vegetation canopy.

Science Datasets (SDSs) in the Level 4 (L4) MOD15A2H product include LAI, FPAR, two quality layers,
and standard deviation for LAI and FPAR. Two low resolution browse images, LAI and FPAR, are also
available for each MOD15A2H granule.""",
        'provider':
        pystac.Provider(name='NASA LP DAAC at the USGS EROS Center',
                        url=('https://doi.org/10.5067/MODIS/MOD15A2H.006'),
                        roles=['producer', 'licensor'])
    },
    'MODIS/006/MOD16A3GF': {
        'links': [
            pystac.Link(
                rel='item',
                target=
                'https://lpdaac.usgs.gov/documents/494/MOD16_User_Guide_V6.pdf',
                title='User Guide'),
            pystac.Link(
                rel='item',
                target=
                'https://ladsweb.modaps.eosdis.nasa.gov/filespec/MODIS/6/MOD16A3GF',
                title='Data File')
        ],
        'title':
        'MODIS/Terra Net Evapotranspiration Gap-Filled Yearly L4 Global 500 m SIN Grid',
        'description':
        """The MOD16A3GF Version 6 Evapotranspiration/Latent Heat Flux (ET/LE) product is a year-end
gap-filled yearly composite dataset produced at 500 meter (m) pixel resolution. The algorithm
used for the MOD16 data product collection is based on the logic of the Penman-Monteith equation,
which includes inputs of daily meteorological reanalysis data along with Moderate Resolution
Imaging Spectroradiometer (MODIS) remotely sensed data products such as vegetation property
dynamics, albedo, and land cover.

The MOD16A3GF will be generated at the end of each year when the entire yearly 8-day MOD15A2H
is available. Hence, the gap-filled MOD16A3GF is the improved MOD16, which has cleaned the
poor-quality inputs from yearly Leaf Area Index and Fraction of Photosynthetically Active Radiation
(LAI/FPAR) based on the Quality Control (QC) label for every pixel. If any LAI/FPAR pixel did not
meet the quality screening criteria, its value is determined through linear interpolation. However,
users cannot get MOD16A3GF in near-real time because it will be generated only at the end of a given
year.

Provided in the MOD16A3GF product are layers for composited ET, LE, Potential ET (PET), and
Potential LE (PLE) along with a quality control layer. Two low resolution browse images, ET
and LE, are also available for each MOD16A3GF granule.

The pixel values for the two Evapotranspiration layers (ET and PET) are the sum for all days
within the defined year, and the pixel values for the two Latent Heat layers (LE and PLE) are
the average of all days within the defined year.""",
        'provider':
        pystac.Provider(name='NASA LP DAAC at the USGS EROS Center',
                        url=('https://doi.org/10.5067/MODIS/MOD16A3GF.006'),
                        roles=['producer', 'licensor'])
    },
    'MODIS/006/MOD17A2H': {
        'links': [
            pystac.Link(
                rel='item',
                target=
                'https://lpdaac.usgs.gov/documents/495/MOD17_User_Guide_V6.pdf',
                title='User Guide'),
            pystac.Link(
                rel='item',
                target=
                'https://ladsweb.modaps.eosdis.nasa.gov/filespec/MODIS/6/MOD17A2H',
                title='Data File')
        ],
        'title':
        'MODIS/Terra Gross Primary Productivity 8-Day L4 Global 500 m SIN',
        'description':
        """The MOD17A2H Version 6 Gross Primary Productivity (GPP)
product is a cumulative 8-day composite of
values with 500 meter (m) pixel size based on the radiation use efficiency concept that can be
potentially used as inputs to data models to calculate terrestrial energy, carbon, water cycle
processes, and biogeochemistry of vegetation. The data product includes information about GPP
and Net Photosynthesis (PSN). The PSN band values are the GPP less the Maintenance Respiration
(MR). The data product also contains a PSN Quality Control (QC) layer. The quality layer
contains quality information for both the GPP and thePSN.""",
        'provider':
        pystac.Provider(name='NASA LP DAAC at the USGS EROS Center',
                        url=('https://doi.org/10.5067/MODIS/MOD17A2H.006'),
                        roles=['producer', 'licensor'])
    },
    'MODIS/006/MOD17A2HGF': {
        'links': [
            pystac.Link(
                rel='item',
                target=
                'https://lpdaac.usgs.gov/documents/495/MOD17_User_Guide_V6.pdf',
                title='User Guide'),
            pystac.Link(
                rel='item',
                target=
                'https://ladsweb.modaps.eosdis.nasa.gov/filespec/MODIS/6/MOD17A2HGF',
                title='Data File')
        ],
        'title':
        'MODIS/Terra Gross Primary Productivity Gap-Filled 8-Day L4 Global 500 m SIN Grid',
        'description':
        """The MOD17A2HGF Version 6 Gross Primary Productivity (GPP) product
is a cumulative 8-day composite of
values with 500 meter (m) pixel size based on the radiation use efficiency concept that can
be potentially used as inputs to data models to calculate terrestrial energy, carbon, water
cycle processes, and biogeochemistry of vegetation. The data product includes information
about GPP and Net Photosynthesis (PSN). The PSN band values are the GPP less the Maintenance
Respiration (MR). The data product also contains a PSN Quality Control (QC) layer. The quality
layer contains quality information for both the GPP and the PSN.

The MOD17A2HGF will be generated at the end of each year when the entire yearly 8-day MOD15A2H
is available. Hence, the gap-filled MOD17A2HGF is the improved MOD17, which has cleaned the
poor-quality inputs from 8-day Leaf Area Index and Fraction of Photosynthetically Active
Radiation (FPAR/LAI) based on the Quality Control (QC) label for every pixel. If any LAI/FPAR
pixel did not meet the quality screening criteria, its value is determined through linear
interpolation. However, users cannot get MOD17A2HGF in near-real time because it will be
generated only at the end of a given year.""",
        'provider':
        pystac.Provider(name='NASA LP DAAC at the USGS EROS Center',
                        url=('https://doi.org/10.5067/MODIS/MOD17A2HGF.006'),
                        roles=['producer', 'licensor'])
    },
    'MODIS/006/MOD17A3HGF': {
        'links': [
            pystac.Link(
                rel='item',
                target=
                'https://lpdaac.usgs.gov/documents/495/MOD17_User_Guide_V6.pdf',
                title='User Guide'),
            pystac.Link(
                rel='item',
                target=
                'https://ladsweb.modaps.eosdis.nasa.gov/filespec/MODIS/6/MOD17A3HGF',
                title='Data File')
        ],
        'title':
        'MODIS/Terra Net Primary Production Gap-Filled Yearly L4 Global 500 m SIN Grid',
        'description':
        """The MOD17A3HGF Version 6 product provides information
about annual Net Primary Production (NPP) at 500 meter (m) pixel resolution.
Annual NPP is derived from the sum of all 8-day Net Photosynthesis (PSN) products
(MOD17A2H) from the given year. The PSN value is the difference of the Gross
Primary Productivity (GPP) and the Maintenance Respiration (MR).

The MOD17A3HGF will be generated at the end of each year when the entire yearly
8-day MOD15A2H is available. Hence, the gap-filled MOD17A3HGF is the improved MOD17,
which has cleaned the poor-quality inputs from 8-day Leaf Area Index and Fraction
of Photosynthetically Active Radiation (LAI/FPAR) based on the Quality Control (QC)
label for every pixel. If any LAI/FPAR pixel did not meet the quality screening
criteria, its value is determined through linear interpolation. However, users
cannot get MOD17A3HGF in near-real time because it will be generated only at the
end of a given year.""",
        'provider':
        pystac.Provider(name='NASA LP DAAC at the USGS EROS Center',
                        url=('https://doi.org/10.5067/MODIS/MOD17A2HGF.006'),
                        roles=['producer', 'licensor'])
    },
    'MODIS/006/MOD44B': {
        'links': [
            pystac.Link(
                rel='item',
                target=
                'https://lpdaac.usgs.gov/documents/112/MOD44B_User_Guide_V6.pdf',
                title='User Guide'),
            pystac.Link(
                rel='item',
                target=
                'https://ladsweb.modaps.eosdis.nasa.gov/filespec/MODIS/6/MOD44B',
                title='Data File')
        ],
        'title':
        'MODIS/Terra Vegetation Continuous Fields Yearly L3 Global 250 m SIN Grid',
        'description':
        """The MOD44B Version 6 Vegetation Continuous Fields
(VCF) yearly product is a global representation of surface vegetation cover as
gradations of three ground cover components: percent tree cover, percent non-tree
cover, and percent non-vegetated (bare). VCF products provide a continuous,
quantitative portrayal of land surface cover at 250 meter (m) pixel resolution,
with a sub-pixel depiction of percent cover in reference to the three ground cover
components. The sub-pixel mixture of ground cover estimates represents a revolutionary
approach to the characterization of vegetative land cover that can be used to enhance
inputs to environmental modeling and monitoring applications.

The MOD44B data product layers include percent tree cover, percent non-tree cover,
percent non-vegetated, cloud cover, and quality indicators. The start date of the
annual period for this product begins with day of year (DOY) 65 (March 5).""",
        'provider':
        pystac.Provider(name='NASA LP DAAC at the USGS EROS Center',
                        url=('https://doi.org/10.5067/MODIS/MOD44B.006'),
                        roles=['producer', 'licensor'])
    },
    'MODIS/006/MCD12Q1': {
        'links': [
            pystac.Link(
                rel='item',
                target=
                'https://lpdaac.usgs.gov/documents/101/MCD12_User_Guide_V6.pdf',
                title='User Guide'),
            pystac.Link(
                rel='item',
                target=
                'https://ladsweb.modaps.eosdis.nasa.gov/filespec/MODIS/6/MCD12Q1',
                title='Data File')
        ],
        'title':
        'MODIS/Terra+Aqua Land Cover Type Yearly L3 Global 500 m SIN Grid',
        'description':
        """The Terra and Aqua combined Moderate Resolution
Imaging Spectroradiometer (MODIS) Land Cover Type (MCD12Q1) Version 6 data product
provides global land cover types at yearly intervals (2001-2019), derived from six
different classification schemes listed in the User Guide. The MCD12Q1 Version 6
data product is derived using supervised classifications of MODIS Terra and Aqua
reflectance data. The supervised classifications then undergo additional
post-processing that incorporate prior knowledge and ancillary information to
further refine specific classes.

Layers for Land Cover Type 1-5, Land Cover Property 1-3, Land Cover Property
Assessment 1-3, Land Cover Quality Control (QC), and a Land Water Mask are
provided in each MCD12Q1 Version 6 Hierarchical Data Format 4 (HDF4) file.""",
        'provider':
        pystac.Provider(name='NASA LP DAAC at the USGS EROS Center',
                        url=('https://doi.org/10.5067/MODIS/MCD12Q1.006'),
                        roles=['producer', 'licensor'])
    },
    'MODIS/006/MOD44W': {
        'links': [
            pystac.Link(
                rel='item',
                target=
                'https://lpdaac.usgs.gov/documents/109/MOD44W_User_Guide_ATBD_V6.pdf',
                title='User Guide')
        ],
        'title':
        'MODIS/Terra Land Water Mask Derived from MODIS and'
        ' SRTM L3 Yearly Global 250 m SIN Grid',
        'description':
        """The Terra Moderate Resolution Imaging Spectroradiometer
(MODIS) Land Water Mask (MOD44W) Version 6 data product provides a global
map of surface water at 250 meter (m) spatial resolution. The data are
available annually from 2000 to 2015. MOD44W Version 6 is derived using a
decision tree classifier trained with MODIS data and validated with the
Version 5 MOD44W data product. A series of masks are applied to address
known issues caused by terrain shadow, burn scars, cloudiness, or ice cover
in oceans. A primary improvement in Version 6 is the generation of time series
data rather than a simple static representation of water, given that water bodies
fluctuate in size and location over time due to both natural and anthropogenic causes.
Provided in each MOD44W Version 6 Hierarchical Data Format 4 (HDF4) file are layers
for land, water, no data, and an associated per pixel quality assurance (QA) layer
that provides users with information on the determination of water.""",
        'provider':
        pystac.Provider(name='NASA LP DAAC at the USGS EROS Center',
                        url=('https://doi.org/10.5067/MODIS/MOD44W.006'),
                        roles=['producer', 'licensor'])
    },
    'MODIS/006/MOD14A1': {
        'links': [
            pystac.Link(
                rel='item',
                target=
                'https://lpdaac.usgs.gov/documents/88/MOD14_User_Guide_v6.pdf',
                title='User Guide'),
            pystac.Link(
                rel='item',
                target=
                'https://ladsweb.modaps.eosdis.nasa.gov/filespec/MODIS/6/MOD14A1',
                title='Data File')
        ],
        'title':
        'MODIS/Terra Thermal Anomalies/Fire Daily L3 Global 1 km SIN Grid',
        'description':
        """The Terra Moderate Resolution Imaging
Spectroradiometer (MODIS) Thermal Anomalies and Fire Daily
(MOD14A1) Version 6 data are generated every eight days at 1 kilometer (km) spatial resolultion
as a Level 3 product. MOD14A1 contains eight consecutive days of fire data conveniently packaged
into a single file.

The Science Dataset (SDS) layers include the fire mask, pixel quality indicators, maximum fire
radiative power (MaxFRP), and the position of the fire pixel within the scan. Each layer consists of
daily per pixel information for each of the eight days of data acquisition.""",
        'provider':
        pystac.Provider(name='NASA LP DAAC at the USGS EROS Center',
                        url=('https://doi.org/10.5067/MODIS/MOD44W.006'),
                        roles=['producer', 'licensor'])
    },
    'MODIS/006/MOD14A2': {
        'links': [
            pystac.Link(
                rel='item',
                target=
                'https://lpdaac.usgs.gov/documents/876/MOD14_User_Guide_v6.pdf',
                title='User Guide'),
            pystac.Link(
                rel='item',
                target=
                'https://ladsweb.modaps.eosdis.nasa.gov/filespec/MODIS/6/MOD14A2',
                title='Data File')
        ],
        'title':
        'MODIS/Terra Thermal Anomalies/Fire 8-Day L3 Global 1 km SIN Grid',
        'description':
        """The Terra Moderate Resolution Imaging
Spectroradiometer (MODIS) Thermal Anomalies and Fire 8-Day (MOD14A2)
Version 6 data are generated at 1 kilometer (km) spatial resolultion as
a Level 3 product. The MOD14A2 gridded composite contains the maximum value
of the individual fire pixel classes detected during the eight days of acquisition.

The Science Dataset (SDS) layers include the fire mask and pixel quality indicators.""",
        'provider':
        pystac.Provider(name='NASA LP DAAC at the USGS EROS Center',
                        url=('https://doi.org/10.5067/MODIS/MOD14A2.006'),
                        roles=['producer', 'licensor'])
    }
}

MODIS_BAND_DATA = {
    'MODIS/006/MCD43A4': [
        Band.create(name='Nadir_Reflectance_Band1',
                    common_name='red',
                    description='NBAR at local solar noon for band 1',
                    center_wavelength=0.645),
        Band.create(name='Nadir_Reflectance_Band2',
                    common_name='nir',
                    description='NBAR at local solar noon for band 2',
                    center_wavelength=0.8585),
        Band.create(name='Nadir_Reflectance_Band3',
                    common_name='blue',
                    description='NBAR at local solar noon for band 3',
                    center_wavelength=0.469),
        Band.create(name='Nadir_Reflectance_Band4',
                    common_name='green',
                    description='NBAR at local solar noon for band 4',
                    center_wavelength=0.555),
        Band.create(name='Nadir_Reflectance_Band5',
                    description='NBAR at local solar noon for band 5',
                    center_wavelength=1.24),
        Band.create(name='Nadir_Reflectance_Band6',
                    common_name='swir16',
                    description='NBAR at local solar noon for band 6',
                    center_wavelength=1.64),
        Band.create(name='Nadir_Reflectance_Band7',
                    common_name='swir22',
                    description='NBAR at local solar noon for band 7',
                    center_wavelength=2.13),
        Band.create(name='BRDF_Albedo_Band_Mandatory_Quality_Band1',
                    description='BRDF albedo mandatory quality for band 1'),
        Band.create(name='BRDF_Albedo_Band_Mandatory_Quality_Band2',
                    description='BRDF albedo mandatory quality for band 2'),
        Band.create(name='BRDF_Albedo_Band_Mandatory_Quality_Band3',
                    description='BRDF albedo mandatory quality for band 3'),
        Band.create(name='BRDF_Albedo_Band_Mandatory_Quality_Band4',
                    description='BRDF albedo mandatory quality for band 4'),
        Band.create(name='BRDF_Albedo_Band_Mandatory_Quality_Band5',
                    description='BRDF albedo mandatory quality for band 5'),
        Band.create(name='BRDF_Albedo_Band_Mandatory_Quality_Band6',
                    description='BRDF albedo mandatory quality for band 6'),
        Band.create(name='BRDF_Albedo_Band_Mandatory_Quality_Band7',
                    description='BRDF albedo mandatory quality for band 7')
    ],
    'MODIS/006/MOD10A1': [
        Band.create(
            name='NDSI_Snow_Cover',
            description=""" NDSI snow cover plus other results. This value is
                            computed for MOD10_L2 and retrieved when the
                            observation of the day is selected. Possible values
                            are:
                            0–100: NDSI snow cover
                            200: missing data
                            201: no decision
                            211: night
                            237: inland water
                            239: ocean
                            250: cloud
                            254: detector saturated
                            255: fill"""),
        Band.create(
            name='NDSI_Snow_Cover_Basic_QA',
            description=""" A basic estimate of the quality of the algorithm
                            result. This value is computed for MOD10_L2 and
                            retrieved with the corresponding observation of the
                            day. Possible values are:
                            0: best
                            1: good
                            2: OK
                            3: poor (not currently in use)
                            211: night
                            239: ocean
                            255: unusable input or no data"""),
        Band.create(
            name='NDSI_Snow_Cover_Algorithm_Flags_QA',
            description=""" Bit flags indicating screen results and the presence
                            of inland water. See “Section 1.7.1 Interpreting
                            NDSI_Snow_Cover_Algorithm_Flags_QA” for a
                            description. These flags are set when MOD10_L2 is
                            generated and retrieved with the corresponding
                            observation of the day. Bits are set to on (1) as
                            follows:
                            Bit 0: Inland water
                            Bit 1: Low visible screen failed. Snow detection
                            reversed.
                            Bit 2: Low NDSI screen failed. Snow detection
                            reversed.
                            Bit 3: Combined temperature/height screen failed.
                            On means either:
                            brightness temperature ≥ 281 K, pixel height <
                            1300 m, flag set, snow detection reversed to not
                            snow, OR;
                            brightness temperature ≥ 281 K, pixel height ≥ 1300
                            m, flag set, snow detection NOT reversed.
                            Bit 4: Shortwave IR (SWIR) reflectance
                            anomalously high. On means either:
                            Snow pixel with SWIR > 0.45, flag set, snow
                            detection reversed to not snow, OR;
                            Snow pixel with 25% < SWIR <= 45%, flag set to
                            indicate unusual snow conditon, snow detection
                            NOT reversed.
                            Bit 5: spare
                            Bit 6: spare
                            Bit 7: solar zenith screen failed, uncertainty
                            increased."""),
        Band.create(
            name='NDSI',
            description=""" Raw NDSI (i.e. prior to screening) reported in the
                        range 0–10,000. Values are scaled by 1 x 104. This
                        value is computed for MOD10_L2 and retrieved
                        with the corresponding observation of the day."""),
        Band.create(name='Snow_Albedo_Daily_Tile',
                    description=""" Snow albedo plus other results.
                            Possible values are:
                            1–100: snow albedo
                            101: no decision
                            111: night
                            125: land
                            137: inland water
                            139: ocean
                            150: cloud
                            151: cloud detected as snow
                            250: missing
                            251: self-shadowing
                            252: land mask mismatch
                            253: BRDF failure
                            254: non-production mask"""),
        Band.create(
            name='orbit_pnt',
            description=""" Pointer to the orbit number of the swath that was
                            selected as the observation of the day. The pointer
                            references by index the list of orbit numbers written
                            to the ORBITNUMBERARRAY metadata object in
                            ArchiveMetadata.0."""),
        Band.create(
            name='granule_pnt',
            description=""" Pointer to the granule (swath) that was mapped into
                            the tile. The pointer references the corresponding
                            value in the GRANULEPOINTERARRAY metadata
                            object written to ArchiveMetadata.0. See “Section
                            1.7.2 | Using granule_pnt” for more information""")
    ],
    'MODIS/006/MOD11A1': [
        Band.create(name='LST_Day_1km',
                    description='Daytime Land Surface Temperature'),
        Band.create(name='QC_Day',
                    description='Daytime LST Quality Indicators'),
        Band.create(name='Day_view_time',
                    description='Local time of day observation'),
        Band.create(name='Day_view_angl',
                    description='View zenith angle of day observation'),
        Band.create(name='LST_Night_1km',
                    description='Nighttime Land Surface Temperature'),
        Band.create(name='QC_Night',
                    description='Nighttime LST Quality indicators'),
        Band.create(name='Night_view_time',
                    description='Local time of night observation'),
        Band.create(name='Night_view_angl',
                    description='View zenith angle of night observation'),
        Band.create(name='Emis_31', description='Band 31 emissivity'),
        Band.create(name='Emis_32', description='Band 32 emissivity'),
        Band.create(name='Clear_day_cov',
                    description='Day clear-sky coverage'),
        Band.create(name='Clear_night_cov',
                    description='Night clear-sky coverage')
    ],
    'MODIS/006/MOD11A2': [
        Band.create(name='LST_Day_1km',
                    description='Daytime Land Surface Temperature'),
        Band.create(name='QC_Day',
                    description='Daytime LST Quality Indicators'),
        Band.create(name='Day_view_time',
                    description='Local time of day observation'),
        Band.create(name='Day_view_angl',
                    description='View zenith angle of day observation'),
        Band.create(name='LST_Night_1km',
                    description='Nighttime Land Surface Temperature'),
        Band.create(name='QC_Night',
                    description='Nighttime LST Quality indicators'),
        Band.create(name='Night_view_time',
                    description='Local time of night observation'),
        Band.create(name='Night_view_angl',
                    description='View zenith angle of night observation'),
        Band.create(name='Emis_31', description='Band 31 emissivity'),
        Band.create(name='Emis_32', description='Band 32 emissivity'),
        Band.create(name='Clear_day_cov',
                    description='Day clear-sky coverage'),
        Band.create(name='Clear_night_cov',
                    description='Night clear-sky coverage')
    ],
    'MODIS/006/MOD21A2': [
        Band.create(name='LST_Day_1KM',
                    description='Day Land surface temperature'),
        Band.create(name='QC_Day', description='Day Quality Control (QC)'),
        Band.create(name='View_Angle_Day',
                    description='Day MODIS view zenith angle'),
        Band.create(name='View_Time_Day',
                    description='Time of MODIS observation for day'),
        Band.create(name='LST_Night_1KM',
                    description='Night Land Surface Temperature'),
        Band.create(name='QC_Night', description='Night Quality Control (QC)'),
        Band.create(name='View_Angle_Night',
                    description='Night view zenith angle'),
        Band.create(name='View_Time_Night',
                    description='Time of Observation for night'),
        Band.create(name='Emis_29',
                    description='Average Day/Night Band 29 emissivity'),
        Band.create(name='Emis_31',
                    description='Average Day/Night Band 31 emissivity'),
        Band.create(name='Emis_32',
                    description='Average Day/Night Band 32 emissivity')
    ],
    'MODIS/006/MOD13Q1': [
        Band.create(name='250m 16 days NDVI', description='16 day NDVI'),
        Band.create(name='250m 16 days EVI', description='16 day EVI'),
        Band.create(name='250m 16 days VI Quality',
                    description='VI quality indicators'),
        Band.create(name='250m 16 days red reflectance',
                    common_name='red',
                    description='Surface Reflectance Band 1'),
        Band.create(name='250m 16 days NIR reflectance',
                    common_name='nir',
                    description='Surface Reflectance Band 2'),
        Band.create(name='250m 16 days blue reflectance',
                    common_name='blue',
                    description='Surface Reflectance Band 3'),
        Band.create(name='250m 16 days MIR reflectance',
                    common_name='swir22',
                    description='Surface Reflectance Band 7'),
        Band.create(name='250m 16 days view zenith angle',
                    description='View zenith angle of VI Pixel'),
        Band.create(name='250m 16 days sun zenith angle',
                    description='Sun zenith angle of VI pixel'),
        Band.create(name='250m 16 days relative azimuth angle',
                    description='Relative azimuth angle of VI pixel'),
        Band.create(name='250m 16 days composite day of the year',
                    description='Day of year VI pixel'),
        Band.create(name='250m 16 days pixel reliability',
                    description='Quality reliability of VI pixel'),
    ],
    'MODIS/006/MOD13A1': [
        Band.create(name='500m 16 days NDVI', description='500m 16 days NDVI'),
        Band.create(name='500m 16 days EVI', description='500m 16 days EVI'),
        Band.create(name='500m 16 days VI Quality	',
                    description='VI quality indicators'),
        Band.create(name='500m 16 days red reflectance',
                    common_name='red',
                    description='Surface Reflectance Band 1'),
        Band.create(name='500m 16 days red reflectance',
                    common_name='nir',
                    description='Surface Reflectance Band 2'),
        Band.create(name='500m 16 days red reflectance',
                    common_name='blue',
                    description='Surface Reflectance Band 3'),
        Band.create(name='500m 16 days red reflectance',
                    common_name='swir22',
                    description='Surface Reflectance Band 7'),
        Band.create(name='500m 16 days view zenith angle',
                    description='View zenith angle of VI Pixel'),
        Band.create(name='500m 16 days sun zenith angle',
                    description='Sun zenith angle of VI pixel'),
        Band.create(name='500m 16 days relative aziumuth angle',
                    description='Relative azimuth angle of VI pixel'),
        Band.create(name='500m 16 days composite day of the year',
                    description='Day of year VI pixel'),
        Band.create(name='500m 16 days pixel reliability',
                    description='Quality reliability of VI pixel')
    ],
    'MODIS/006/MOD15A2H': [
        Band.create(
            name='Fpar_500m',
            description='Fraction of Photosynthetically Active Radiation'),
        Band.create(name='Lai_500m', description='Leaf Area Index'),
        Band.create(name='FparLai_QC	',
                    description='Quality for LAI and FPAR'),
        Band.create(name='FparExtra_QC',
                    description='Extra detail Quality for LAI and FPAR'),
        Band.create(name='FparStdDev_500m', description='Percent'),
        Band.create(name='LaiStdDev_500m',
                    description='Standard deviation of LAI')
    ],
    'MODIS/006/MOD16A3GF': [
        Band.create(name='ET_500m', description='Total of Evapotranspiration'),
        Band.create(name='LE_500m', description='Average of Latent Heat Flux'),
        Band.create(name='PET_500m	',
                    description='Total Potential Evapotranspiration'),
        Band.create(name='PLE_500m',
                    description='Average of Potential Latent Heat Flux'),
        Band.create(name='ET_QC_500m',
                    description='Evapotranspiration Quality Assessment')
    ],
    'MODIS/006/MOD17A2H': [
        Band.create(name='Gpp_500m', description='Gross Primary Productivity'),
        Band.create(name='PsnNet_500m', description='Net Photosynthesis'),
        Band.create(name='Psn_QC_500m',
                    description='Quality control indicators')
    ],
    'MODIS/006/MOD17A2HGF': [
        Band.create(name='Gpp_500m', description='Gross Primary Productivity'),
        Band.create(name='PsnNet_500m', description='Net Photosynthesis'),
        Band.create(name='Psn_QC_500m',
                    description='Quality control indicators')
    ],
    'MODIS/006/MOD17A3HGF': [
        Band.create(name='Npp_500m', description='Net Primary Productivity'),
        Band.create(name='Npp_QC_500m', description='Quality control Bits')
    ],
    'MODIS/006/MOD44B': [
        Band.create(name='Percent_Tree_Cover',
                    description='Percent of pixel that is tree covered'),
        Band.create(name='Percent_NonTree_Vegetation',
                    description='Percent of pixel that is nontree vegetation'),
        Band.create(name='Percent_NonVegetated',
                    description='Percent of pixel non vegetated'),
        Band.create(name='Quality', description='Quality Control indicators'),
        Band.create(name='Percent_Tree_Cover_SD',
                    description='Standard deviation of percent tree covered'),
        Band.create(name='Percent_NonVegetated_SD',
                    description='Standard deviation of percent not vegetated'),
        Band.create(name='Cloud', description='Pixel cloud cover indicators')
    ],
    'MODIS/006/MCD12Q1': [
        Band.create(name='LC_Type1',
                    description='Land Cover Type 1: Annual International'
                    'Geosphere-Biosphere Programme (IGBP) classification'),
        Band.create(
            name='LC_Type2',
            description=
            'Land Cover Type 2: Annual University of Maryland (UMD) classification'
        ),
        Band.create(
            name='LC_Type3',
            description=
            'Land Cover Type 3: Annual Leaf Area Index (LAI) classification'),
        Band.create(
            name='LC_Type4',
            description=
            'Land Cover Type 4: Annual BIOME-Biogeochemical Cycles (BGC) classification'
        ),
        Band.create(
            name='LC_Type5',
            description=
            'Land Cover Type 5: Annual Plant Functional Types classification'),
        Band.create(
            name='LC_Prop1',
            description=
            'FAO-Land Cover Classification System 1 (LCCS1) land cover layer'),
        Band.create(name='LC_Prop2', description='FAO-LCCS2 land use layer'),
        Band.create(name='LC_Prop3',
                    description='FAO-LCCS3 surface hydrology layer'),
        Band.create(name='LC_Prop1_Assessment',
                    description='LCCS1 land cover layer confidence'),
        Band.create(name='LC_Prop2_Assessment',
                    description='LCCS2 land use layer confidence'),
        Band.create(name='LC_Prop3_Assessment',
                    description='LCCS3 surface hydrology layer confidence'),
        Band.create(name='QC', description='Product quality flags'),
        Band.create(
            name='LW',
            description=
            'Binary land (class 2) / water (class 1) mask derived from MOD44W')
    ],
    'MODIS/006/MOD44W': [
        Band.create(name='Water_mask', description='Land/Water Mask'),
        Band.create(name='Water_mask_QA', description='Quality Assurance (QA)')
    ],
    'MODIS/006/MOD14A1': [
        Band.create(name='FireMask', description='Confidence of fire'),
        Band.create(name='QA', description='Pixel quality indicators'),
        Band.create(name='MaxFRP', description='Maximum Fire Radiative Power'),
        Band.create(name='Sample',
                    description='Position of fire pixel within scan')
    ],
    'MODIS/006/MOD14A2': [
        Band.create(name='FireMask', description='Confidence of fire'),
        Band.create(name='QA', description='Pixel quality indicators')
    ]
}

ADDITIONAL_MODIS_PROPERTIES = {
    'MODIS/006/MOD11A1': {
        'QC_Mandatory_QA_flags_00':
        'LST produced, good quality, not necessary to examine more detailed QA',
        'QC_Mandatory_QA_flags_01':
        'LST produced, other quality, recommend examination of more detailed QA',
        'QC_Mandatory_QA_flags_10': 'LST not produced due to cloud effects',
        'QC_Mandatory_QA_flags_11':
        'LST not produced primarily due to reasons other than cloud',
        'QC_Data_quality_flag_00': 'good quality data',
        'QC_Data_quality_flag_01': 'other quality data',
        'QC_Data_quality_flag_10': 'TBD',
        'QC_Data_quality_flag_11': 'TBD',
        'QC_Emis_Error_flag_00': 'average emissivity error <= 0.01',
        'QC_Emis_Error_flag_01': 'average emissivity error <= 0.02',
        'QC_Emis_Error_flag_10': 'average emissivity error <= 0.04',
        'QC_Emis_Error_flag_11': 'average emissivity error > 0.04',
        'QC_LST_Error_flag_00': 'average LST error <= 1K',
        'QC_LST_Error_flag_01': 'average LST error <= 2K',
        'QC_LST_Error_flag_10': 'average LST error <= 3K',
        'QC_LST_Error_flag_11': 'average LST error > 3K'
    },
    'MODIS/006/MOD11A2': {
        'QC_Mandatory_QA_flags_00':
        'LST produced, good quality, not necessary to examine more detailed QA',
        'QC_Mandatory_QA_flags_01':
        'LST produced, other quality, recommend examination of more detailed QA',
        'QC_Mandatory_QA_flags_10': 'LST not produced due to cloud effects',
        'QC_Mandatory_QA_flags_11':
        'LST not produced primarily due to reasons other than cloud',
        'QC_Data_quality_flag_00': 'good quality data',
        'QC_Data_quality_flag_01': 'other quality data',
        'QC_Data_quality_flag_10': 'TBD',
        'QC_Data_quality_flag_11': 'TBD',
        'QC_Emis_Error_flag_00': 'average emissivity error <= 0.01',
        'QC_Emis_Error_flag_01': 'average emissivity error <= 0.02',
        'QC_Emis_Error_flag_10': 'average emissivity error <= 0.04',
        'QC_Emis_Error_flag_11': 'average emissivity error > 0.04',
        'QC_LST_Error_flag_00': 'average LST error <= 1K',
        'QC_LST_Error_flag_01': 'average LST error <= 2K',
        'QC_LST_Error_flag_10': 'average LST error <= 3K',
        'QC_LST_Error_flag_11': 'average LST error > 3K'
    },
    'MODIS/006/MOD21A2': {
        'QC_Mandatory_QA_flags_00':
        'Pixel produced, good quality, no further QA info necessary',
        'QC_Mandatory_QA_flags_01':
        """Pixel produced but unreliable quality. Either
                                        one or more of the following conditions are met:
                                        emissivity in both bands 31 and 32 < 0.95, retrieval
                                        affected by nearby cloud, low transmissivity due to
                                        high water vapor loading (<0.4), Recommend more
                                        detailed analysis of other QC information""",
        'QC_Mandatory_QA_flags_10': 'Pixel not produced due to cloud',
        'QC_Mandatory_QA_flags_11':
        'Pixel not produced due to reasons other than cloud',
        'QC_Data_quality_flag_00': 'Good data quality of L1B bands 29, 31, 32',
        'QC_Data_quality_flag_01': 'Missing pixel',
        'QC_Data_quality_flag_10': 'Fairly calibrated',
        'QC_Data_quality_flag_11': 'Poorly calibrated, TES processing skipped',
        'QC_Cloud_flag_00': 'Cloud free',
        'QC_Cloud_flag_01': 'Thin cirrus',
        'QC_Cloud_flag_10': 'Pixel within 2 pixels of nearest cloud',
        'QC_Cloud_flag_11': 'Cloudy pixels',
        'QC_Iterations_00': 'Slow convergence',
        'QC_Iterations_01': 'Nominal',
        'QC_Iterations_10': 'Nominal',
        'QC_Iterations_11': 'Fast',
        'QC_Atmospheric_Opacity_00': '>=3 (Warm, humid air; or cold land)',
        'QC_Atmospheric_Opacity_01': '0.2 - 0.3 (Nominal value)',
        'QC_Atmospheric_Opacity_10': '0.1 - 0.2 (Nominal value)',
        'QC_Atmospheric_Opacity_11': '<0.1 (Dry, or high altitude pixel)',
        'QC_MMD_00': '> 0.15 (Most silicate rocks)',
        'QC_MMD_01': '0.1 - 0.15 (Rocks, sand, some soils)',
        'QC_MMD_10': '0.03 - 0.1 (Mostly soils, mixed pixel)',
        'QC_MMD_11': '<0.03 (Vegetation, snow, water, ice)',
        'QC_Emissivity_accuracy_00': '>0.02 (Poor performance)',
        'QC_Emissivity_accuracy_01': '0.015 - 0.02 (Marginal performance)',
        'QC_Emissivity_accuracy_10': '0.01 - 0.015 (Good performance)',
        'QC_Emissivity_accuracy_11': '<0.01 (Excellent performance)',
        'QC_LST_accuracy _00': '>2 K (Poor performance)',
        'QC_LST_accuracy_01': '1.5 - 2 K (Marginal performance)',
        'QC_LST_accuracy_10': '1 - 1.5 K (Good performance)',
        'QC_LST_accuracy_11': '<1 K (Excellent performance)'
    },
    'MODIS/006/MOD13Q1': {
        'QA_SDS_VI_Quality_MODLAND_QA_Bits_00':
        'VI produced with good quality',
        'QA_SDS_VI_Quality_MODLAND_QA_Bits_01':
        'VI produced, but check other QA',
        'QA_SDS_VI_Quality_MODLAND_QA_Bits_10':
        'Pixel produced, but most probably cloudy',
        'QA_SDS_VI_Quality_MODLAND_QA_Bits_11':
        'Pixel not produced due to other reasons than clouds',
        'QA_SDS_VI_Usefulness_0000': 'Highest quality',
        'QA_SDS_VI_Usefulness_0001': 'Lower quality',
        'QA_SDS_VI_Usefulness_0010': 'Decreasing quality',
        'QA_SDS_VI_Usefulness_0100': 'Decreasing quality',
        'QA_SDS_VI_Usefulness_1000': 'Decreasing quality',
        'QA_SDS_VI_Usefulness_1001': 'Decreasing quality',
        'QA_SDS_VI_Usefulness_1010': 'Decreasing quality',
        'QA_SDS_VI_Usefulness_1100': 'Lowest quality',
        'QA_SDS_VI_Usefulness_1101': 'Quality so low that it is not useful',
        'QA_SDS_VI_Usefulness_1110': 'L1B data faulty',
        'QA_SDS_VI_Usefulness_1111':
        'Not useful for any other reason/not processed',
        'QA_SDS_Aerosol_Quantity_00': 'Climatology',
        'QA_SDS_Aerosol_Quantity_01': 'Low',
        'QA_SDS_Aerosol_Quantity_10': 'Intermediate',
        'QA_SDS_Aerosol_Quantity_11': 'High',
        'QA_SDS_Adjacent_cloud_detected_0': 'No',
        'QA_SDS_Adjacent_cloud_detected_1': 'Yes',
        'QA_SDS_Atmosphere_BRDF_Correction_0': 'No',
        'QA_SDS_Atmosphere_BRDF_Correction_1': 'Yes',
        'QA_SDS_Mixed_Clouds_0': 'No',
        'QA_SDS_Mixed_Clouds_1': 'Yes',
        'QA_SDS_Land_Water_Mask_000': 'Shallow ocean',
        'QA_SDS_Land_Water_Mask_001': 'Land - Nothing else but land',
        'QA_SDS_Land_Water_Mask_010': 'Ocean coastlines and lake shorelines',
        'QA_SDS_Land_Water_Mask_011': 'Shallow inland water',
        'QA_SDS_Land_Water_Mask_100': 'Ephemeral water',
        'QA_SDS_Land_Water_Mask_101': 'Deep inland water',
        'QA_SDS_Land_Water_Mask_110': 'Moderate or continental ocean',
        'QA_SDS_Land_Water_Mask_111': 'Deep ocean',
        'QA_SDS_Possible_Snow_Ice_0': 'No',
        'QA_SDS_Possible_Snow_Ice_1': 'Yes',
        'QA_SDS_Possible_shadow_0': 'No',
        'QA_SDS_Possible_shadow_1': 'Yes',
        'Summary_QA_0': 'Good Data - Use with confidence',
        'Summary_QA_1':
        'Marginal data - Useful, but look at other QA information',
        'Summary_QA_2': 'Snow/Ice - Target covered with snow/ice',
        'Summary_QA_3': 'Cloudy - Target not visible, covered with cloud'
    },
    'MODIS/006/MOD13A1': {
        'QA_SDS_VI_Quality_MODLAND_QA_Bits_00':
        'VI produced with good quality',
        'QA_SDS_VI_Quality_MODLAND_QA_Bits_01':
        'VI produced, but check other QA',
        'QA_SDS_VI_Quality_MODLAND_QA_Bits_10':
        'Pixel produced, but most probably cloudy',
        'QA_SDS_VI_Quality_MODLAND_QA_Bits_11':
        'Pixel not produced due to other reasons than clouds',
        'QA_SDS_VI_Usefulness_0000': 'Highest quality',
        'QA_SDS_VI_Usefulness_0001': 'Lower quality',
        'QA_SDS_VI_Usefulness_0010': 'Decreasing quality',
        'QA_SDS_VI_Usefulness_0100': 'Decreasing quality',
        'QA_SDS_VI_Usefulness_1000': 'Decreasing quality',
        'QA_SDS_VI_Usefulness_1001': 'Decreasing quality',
        'QA_SDS_VI_Usefulness_1010': 'Decreasing quality',
        'QA_SDS_VI_Usefulness_1100': 'Lowest quality',
        'QA_SDS_VI_Usefulness_1101': 'Quality so low that it is not useful',
        'QA_SDS_VI_Usefulness_1110': 'L1B data faulty',
        'QA_SDS_VI_Usefulness_1111':
        'Not useful for any other reason/not processed',
        'QA_SDS_Aerosol_Quantity_00': 'Climatology',
        'QA_SDS_Aerosol_Quantity_01': 'Low',
        'QA_SDS_Aerosol_Quantity_10': 'Intermediate',
        'QA_SDS_Aerosol_Quantity_11': 'High',
        'QA_SDS_Adjacent_cloud_detected_0': 'No',
        'QA_SDS_Adjacent_cloud_detected_1': 'Yes',
        'QA_SDS_Atmosphere_BRDF_Correction_0': 'No',
        'QA_SDS_Atmosphere_BRDF_Correction_1': 'Yes',
        'QA_SDS_Mixed_Clouds_0': 'No',
        'QA_SDS_Mixed_Clouds_1': 'Yes',
        'QA_SDS_Land_Water_Mask_000': 'Shallow ocean',
        'QA_SDS_Land_Water_Mask_001': 'Land - Nothing else but land',
        'QA_SDS_Land_Water_Mask_010': 'Ocean coastlines and lake shorelines',
        'QA_SDS_Land_Water_Mask_011': 'Shallow inland water',
        'QA_SDS_Land_Water_Mask_100': 'Ephemeral water',
        'QA_SDS_Land_Water_Mask_101': 'Deep inland water',
        'QA_SDS_Land_Water_Mask_110': 'Moderate or continental ocean',
        'QA_SDS_Land_Water_Mask_111': 'Deep ocean',
        'QA_SDS_Possible_Snow_Ice_0': 'No',
        'QA_SDS_Possible_Snow_Ice_1': 'Yes',
        'QA_SDS_Possible_shadow_0': 'No',
        'QA_SDS_Possible_shadow_1': 'Yes',
        'Summary_QA_0': 'Good Data - Use with confidence',
        'Summary_QA_1':
        'Marginal data - Useful, but look at other QA information',
        'Summary_QA_2': 'Snow/Ice - Target covered with snow/ice',
        'Summary_QA_3': 'Cloudy - Target not visible, covered with cloud'
    },
    'MODIS/006/MOD15A2H': {
        'LAI_FPAR_fill_value_class_249':
        'Land cover assigned as "unclassified" or not able to determine',
        'LAI_FPAR_fill_value_class_250':
        'Land cover assigned as urban/built-up',
        'LAI_FPAR_fill_value_class_251':
        'Land cover assigned as "permanent" wetlands/inundated marshland',
        'LAI_FPAR_fill_value_class_252':
        'Land cover assigned as perennial snow, ice',
        'LAI_FPAR_fill_value_class_253':
        'Land cover assigned as barren, sparse vegetation (rock, tundra, desert)',
        'LAI_FPAR_fill_value_class_254':
        'Land cover assigned as perennial salt or inland fresh water',
        'LAI_FPAR_fill_value_class_255': 'Fill',
        'STD_LAI_STD_FPAR_fill_value_class_248':
        'No standard deviation available, pixel produced using backup method',
        'STD_LAI_STD_FPAR_fill_value_class_249':
        'Land cover assigned as "unclassified" or not able to determine',
        'STD_LAI_STD_FPAR_fill_value_class_250':
        'Land cover assigned as urban/built-up',
        'STD_LAI_STD_FPAR_fill_value_class_251':
        'Land cover assigned as "permanent" wetlands / inundated marshland',
        'STD_LAI_STD_FPAR_fill_value_class_252':
        'Land cover assigned as perennial snow, ice',
        'STD_LAI_STD_FPAR_fill_value_class_253':
        'Land cover assigned as barren, sparse vegetation (rock, tundra, desert)',
        'STD_LAI_STD_FPAR_fill_value_class_254':
        'Land cover assigned as perennial salt or inland fresh water',
        'STD_LAI_STD_FPAR_fill_value_class_255': 'Fill'
    },
    'MODIS/006/MOD16A3GF': {
        'ET_QC_500m_fill_value_class_249':
        'Land cover assigned as "unclassified" or not able to determine',
        'ET_QC_500m_fill_value_class_250':
        'Land cover assigned as urban/built-up',
        'ET_QC_500m_fill_value_class_251':
        'Land cover assigned as "permanent" wetlands/inundated marshland',
        'ET_QC_500m_fill_value_class_252':
        'Land cover assigned as perennial snow, ice',
        'ET_QC_500m_fill_value_class_253':
        'Land cover assigned as barren, sparse vegetation (rock, tundra, desert)',
        'ET_QC_500m_fill_value_class_254':
        'Land cover assigned as perennial salt or inland fresh water',
        'ET_QC_500m_fill_value_class_255': 'Fill',
        'ET_QC_500m_fill_value_class_65529':
        'Land cover assigned as "unclassified" or not able to determine',
        'ET_QC_500m_fill_value_class_65530':
        'Land cover assigned as urban/built-up',
        'ET_QC_500m_fill_value_class_65531':
        'Land cover assigned as "permanent" wetlands/inundated marshland',
        'ET_QC_500m_fill_value_class_65532':
        'Land cover assigned as perennial snow, ice',
        'ET_QC_500m_fill_value_class_65533':
        'Land cover assigned as barren, sparse vegetation (rock, tundra, desert)',
        'ET_QC_500m_fill_value_class_65534':
        'Land cover assigned as perennial salt or water bodies',
        'ET_QC_500m_fill_value_class_65535': 'Fill',
        'ET_QC_500m_fill_value_class_32761':
        'Land cover assigned as "unclassified" or not able to determine',
        'ET_QC_500m_fill_value_class_32762':
        'Land cover assigned as urban/built-up',
        'ET_QC_500m_fill_value_class_32763':
        'Land cover assigned as "permanent" wetlands/inundated marshland',
        'ET_QC_500m_fill_value_class_32764':
        'Land cover assigned as perennial snow, ice',
        'ET_QC_500m_fill_value_class_32765':
        'Land cover assigned as barren, sparse vegetation (rock, tundra, desert)',
        'ET_QC_500m_fill_value_class_32766':
        'Land cover assigned as perennial salt or water bodies',
        'ET_QC_500m_fill_value_class_32767': 'Fill'
    },
    'MODIS/006/MOD17A2H': {
        'Non-Terrestrial_fill_value_class_32761':
        'Land cover assigned as "unclassified" or not able to determine',
        'Non-Terrestrial_fill_value_class_32762':
        'Land cover assigned as urban/built-up',
        'Non-Terrestrial_fill_value_class_32763':
        'Land cover assigned as "permanent" wetlands/inundated marshland',
        'Non-Terrestrial_fill_value_class_32764':
        'Land cover assigned as perennial snow, ice',
        'Non-Terrestrial_fill_value_class_32765':
        'Land cover assigned as barren, sparse vegetation (rock, tundra, desert)',
        'Non-Terrestrial_fill_value_class_32766':
        'Land cover assigned as perennial salt or water bodies',
        'Non-Terrestrial_fill_value_class_32767':
        'Fill',
        'MODLAND_QC_bits_0':
        'Good Quality - main algorithm with or without saturation',
        'MODLAND_QC_bits_1':
        'Other Quality - back-up algorithm or fill values',
        'SENSOR_0':
        'Terra',
        'SENSOR_1':
        'Aqua',
        'DEADDETECTOR_0':
        'Detectors apparently fine for up to 50% of channels 1,2',
        'DEADDETECTOR_1':
        'Dead detectors caused >50% adjacent detector retrieval',
        'CLOUDSTATE_00':
        '0 Significant clouds NOT present (clear)',
        'CLOUDSTATE_01':
        '1 Significant clouds WERE present',
        'CLOUDSTATE_10':
        '2 Mixed cloud present on pixel',
        'CLOUDSTATE_11':
        '3 Cloud state not defined,assumed clear',
        'SCF_QC_000':
        '0, Main (RT) method used, best result possible (no saturation)',
        'SCF_QC_001':
        '1, Main (RT) method used with saturation. Good,very usable',
        'SCF_QC_010':
        '2, Main (RT) method failed due to bad geometry, empirical algorithm used',
        'SCF_QC_011':
        '3, Main (RT) method failed due to problems other than geometry,'
        'empirical algorithm used',
        'SCF_QC_100':
        "4, Pixel not produced at all, value coudn't be retrieved"
        "(possible reasons: bad L1B data, unusable MOD09GA data)"
    },
    'MODIS/006/MOD17A2HGF': {
        'Non-Terrestrial_fill_value_class_32761':
        'Land cover assigned as "unclassified" or not able to determine',
        'Non-Terrestrial_fill_value_class_32762':
        'Land cover assigned as urban/built-up',
        'Non-Terrestrial_fill_value_class_32763':
        'Land cover assigned as "permanent" wetlands/inundated marshland',
        'Non-Terrestrial_fill_value_class_32764':
        'Land cover assigned as perennial snow, ice',
        'Non-Terrestrial_fill_value_class_32765':
        'Land cover assigned as barren, sparse vegetation (rock, tundra, desert)',
        'Non-Terrestrial_fill_value_class_32766':
        'Land cover assigned as perennial salt or water bodies',
        'Non-Terrestrial_fill_value_class_32767':
        'Fill',
        'MODLAND_QC_bits_0':
        'Good Quality - main algorithm with or without saturation',
        'MODLAND_QC_bits_1':
        'Other Quality - back-up algorithm or fill values',
        'SENSOR_0':
        'Terra',
        'SENSOR_1':
        'Aqua',
        'DEADDETECTOR_0':
        'Detectors apparently fine for up to 50% of channels 1,2',
        'DEADDETECTOR_1':
        'Dead detectors caused >50% adjacent detector retrieval',
        'CLOUDSTATE_00':
        '0 Significant clouds NOT present (clear)',
        'CLOUDSTATE_01':
        '1 Significant clouds WERE present',
        'CLOUDSTATE_10':
        '2 Mixed cloud present on pixel',
        'CLOUDSTATE_11':
        '3 Cloud state not defined,assumed clear',
        'SCF_QC_000':
        '0, Main (RT) method used, best result possible (no saturation)',
        'SCF_QC_001':
        '1, Main (RT) method used with saturation. Good,very usable',
        'SCF_QC_010':
        '2, Main (RT) method failed due to bad geometry, empirical algorithm used',
        'SCF_QC_011':
        '3, Main (RT) method failed due to problems other than geometry, empirical algorithm used',
        'SCF_QC_100':
        '4, Pixel not produced at all, value coudn\'t be retrieved (possible reasons: bad'
        'L1B data, unusable MOD09GA data)'
    },
    'MODIS/006/MOD17A3HGF': {
        'Npp_500m_fill_value_class_32761':
        'Land cover assigned as "unclassified" or not able to determine',
        'Npp_500m_fill_value_class_32762':
        'Land cover assigned as urban/built-up',
        'Npp_500m_fill_value_class_32763':
        'Land cover assigned as "permanent" wetlands/inundated marshland',
        'Npp_500m_fill_value_class_32764':
        'Land cover assigned as perennial snow, ice',
        'Npp_500m_fill_value_class_32765':
        'Land cover assigned as barren, sparse vegetation (rock, tundra, desert)',
        'Npp_500m_fill_value_class_32766':
        'Land cover assigned as perennial salt or water bodies',
        'Npp_500m_fill_value_class_32767': 'Fill',
        'Npp_500m_fill_value_class_249':
        'Land cover assigned as "unclassified" or not able to determine',
        'Npp_500m_fill_value_class_250':
        'Land cover assigned as urban/built-up',
        'Npp_500m_fill_value_class_251':
        'Land cover assigned as "permanent" wetlands/inundated marshland',
        'Npp_500m_fill_value_class_252':
        'Land cover assigned as perennial snow, ice',
        'Npp_500m_fill_value_class_253':
        'Land cover assigned as barren, sparse vegetation (rock, tundra, desert)',
        'Npp_500m_fill_value_class_254':
        'Land cover assigned as perennial salt or water bodies',
        'Npp_500m_fill_value_class_255': 'Fill'
    },
    'MODIS/006/MOD44B': {
        'Cloud_0_DOY_065_to_097': '0 Clear; 1 Bad',
        'Cloud_1_DOY_113_to_145': '0 Clear; 1 Bad',
        'Cloud_2_DOY_161_to_193': '0 Clear; 1 Bad',
        'Cloud_3_DOY_209_to_241': '0 Clear; 1 Bad',
        'Cloud_4_DOY_257_to_289': '0 Clear; 1 Bad',
        'Cloud_5_DOY_305_to_337': '0 Clear; 1 Bad',
        'Cloud_6_DOY_353_to_017': '0 Clear; 1 Bad',
        'Cloud_7_DOY_033_to_045': '0 Clear; 1 Bad',
        'Quality_0_DOY_065_to_097': '0 Clear; 1 Bad',
        'Quality_1_DOY_113_to_145': '0 Clear; 1 Bad',
        'Quality_2_DOY_161_to_193': '0 Clear; 1 Bad',
        'Quality_3_DOY_209_to_241': '0 Clear; 1 Bad',
        'Quality_4_DOY_257_to_289': '0 Clear; 1 Bad',
        'Quality_5_DOY_305_to_337': '0 Clear; 1 Bad',
        'Quality_6_DOY_353_to_017': '0 Clear; 1 Bad',
        'Quality_7_DOY_033_to_045': '0 Clear; 1 Bad'
    },
    'MODIS/006/MCD12Q1': {
        'LC_Type1_class_1':
        '05450a, Evergreen Needleleaf Forests: dominated by'
        'evergreen conifer trees (canopy >2m). Tree cover >60%.',
        'LC_Type1_class_2':
        '086a10, Evergreen Broadleaf Forests: dominated by evergreen'
        'broadleaf and palmate trees (canopy >2m). Tree cover >60%.',
        'LC_Type1_class_3':
        '54a708, Deciduous Needleleaf Forests: dominated by deciduous'
        'needleleaf (larch) trees (canopy >2m). Tree cover >60%.',
        'LC_Type1_class_4':
        '78d203, Deciduous Broadleaf Forests: dominated by deciduous'
        'broadleaf trees (canopy >2m). Tree cover >60%.',
        'LC_Type1_class_5':
        '009900, Mixed Forests: dominated by neither deciduous nor'
        'evergreen (40-60% of each) tree type (canopy >2m). Tree cover >60%.',
        'LC_Type1_class_6':
        'c6b044, Closed Shrublands: dominated by woody perennials'
        '(1-2m height) >60% cover.',
        'LC_Type1_class_7':
        'dcd159, Open Shrublands: dominated by woody perennials'
        '(1-2m height) 10-60% cover.',
        'LC_Type1_class_8':
        'dade48, Woody Savannas: tree cover 30-60% (canopy >2m).',
        'LC_Type1_class_9':
        'fbff13, Savannas: tree cover 10-30% (canopy >2m).',
        'LC_Type1_class_10':
        'b6ff05, Grasslands: dominated by herbaceous annuals (<2m).',
        'LC_Type1_class_11':
        '27ff87, Permanent Wetlands: permanently inundated lands with'
        '30-60% water cover and >10% vegetated cover.',
        'LC_Type1_class_12':
        'c24f44, Croplands: at least 60% of area is cultivated cropland.',
        'LC_Type1_class_13':
        'a5a5a5, Urban and Built-up Lands: at least 30% impervious surface'
        'area including building materials, asphalt and vehicles.',
        'LC_Type1_class_14':
        'ff6d4c, Cropland/Natural Vegetation Mosaics: mosaics of small-scale'
        'cultivation 40-60% with natural tree, shrub, or herbaceous vegetation.',
        'LC_Type1_class_15':
        '69fff8, Permanent Snow and Ice: at least 60% of area is covered by'
        'snow and ice for at least 10 months of the year.',
        'LC_Type1_class_16':
        'f9ffa4, Barren: at least 60% of area is non-vegetated barren (sand, rock, soil)'
        'areas with less than 10% vegetation.',
        'LC_Type1_class_17':
        '1c0dff, Water Bodies: at least 60% of area is covered by permanent water bodies.',
        'LC_Type2_Class_0':
        '1c0dff, Water Bodies: at least 60% of area is covered by permanent water bodies.',
        'LC_Type2_Class_1':
        '05450a, Evergreen Needleleaf Forests: dominated by evergreen conifer'
        'trees (canopy >2m). Tree cover >60%.',
        'LC_Type2_Class_2':
        '086a10, Evergreen Broadleaf Forests: dominated by evergreen broadleaf and palmate'
        'trees (canopy >2m). Tree cover >60%.',
        'LC_Type2_Class_3':
        '54a708, Deciduous Needleleaf Forests: dominated by deciduous needleleaf'
        '(larch) trees (canopy >2m). Tree cover >60%.',
        'LC_Type2_Class_4':
        '78d203, Deciduous Broadleaf Forests: dominated by deciduous broadleaf trees'
        '(canopy >2m). Tree cover >60%.',
        'LC_Type2_Class_5':
        '009900, Mixed Forests: dominated by neither deciduous nor evergreen'
        '(40-60% of each) tree type (canopy >2m). Tree cover >60%.',
        'LC_Type2_Class_6':
        'c6b044, Closed Shrublands: dominated by woody perennials (1-2m height) >60% cover.',
        'LC_Type2_Class_7':
        'dcd159, Open Shrublands: dominated by woody perennials (1-2m height) 10-60% cover.',
        'LC_Type2_Class_8':
        'dade48, Woody Savannas: tree cover 30-60% (canopy >2m).',
        'LC_Type2_Class_9':
        'fbff13, Savannas: tree cover 10-30% (canopy >2m).',
        'LC_Type2_Class_10':
        'b6ff05, Grasslands: dominated by herbaceous annuals (<2m).',
        'LC_Type2_Class_11':
        '27ff87, Permanent Wetlands: permanently inundated lands with 30-60%'
        'water cover and >10% vegetated cover.',
        'LC_Type2_Class_12':
        'c24f44, Croplands: at least 60% of area is cultivated cropland.',
        'LC_Type2_Class_13':
        'a5a5a5, Urban and Built-up Lands: at least 30% impervious surface area'
        'including building materials, asphalt and vehicles.',
        'LC_Type2_Class_14':
        'ff6d4c, Cropland/Natural Vegetation Mosaics: mosaics of small-scale'
        'cultivation 40-60% with natural tree, shrub, or herbaceous vegetation.',
        'LC_Type2_Class_15':
        'f9ffa4, Non-Vegetated Lands: at least 60% of area is non-vegetated barren'
        '(sand, rock, soil) or permanent snow and ice with less than 10% vegetation.',
        'LC_Type3_Class_0':
        '1c0dff, Water Bodies: at least 60% of area is covered by permanent water bodies.',
        'LC_Type3_Class_1':
        'b6ff05, Grasslands: dominated by herbaceous annuals (<2m) including cereal croplands.',
        'LC_Type3_Class_2':
        'dcd159, Shrublands: shrub (1-2m) cover >10%.',
        'LC_Type3_Class_3':
        'c24f44, Broadleaf Croplands: bominated by herbaceous annuals (<2m)'
        'that are cultivated with broadleaf crops.',
        'LC_Type3_Class_4':
        'fbff13, Savannas: between 10-60% tree cover (>2m).',
        'LC_Type3_Class_5':
        '086a10, Evergreen Broadleaf Forests: dominated by evergreen broadleaf and palmate'
        'trees (canopy >2m). Tree cover >60%.',
        'LC_Type3_Class_6':
        '78d203, Deciduous Broadleaf Forests: dominated by deciduous broadleaf trees'
        '(canopy >2m). Tree cover >60%.',
        'LC_Type3_Class_7':
        '05450a, Evergreen Needleleaf Forests: dominated by evergreen conifer trees'
        '(canopy >2m). Tree cover >60%.',
        'LC_Type3_Class_8':
        '54a708, Deciduous Needleleaf Forests: dominated by deciduous needleleaf (larch)'
        'trees (canopy >2m). Tree cover >60%.',
        'LC_Type3_Class_9':
        'f9ffa4, Non-Vegetated Lands: at least 60% of area is non-vegetated barren'
        '(sand, rock, soil) or permanent snow and ice with less than 10% vegetation.',
        'LC_Type3_Class_10':
        'a5a5a5, Urban and Built-up Lands: at least 30% impervious surface area including'
        'building materials, asphalt and vehicles.',
        'LC_Type4_Class_0':
        '1c0dff, Water Bodies: at least 60% of area is covered by permanent water bodies.',
        'LC_Type4_Class_1':
        '05450a, Evergreen Needleleaf Vegetation: dominated by evergreen conifer trees and'
        'shrubs (>1m). Woody vegetation cover >10%.',
        'LC_Type4_Class_2':
        '086a10, Evergreen Broadleaf Vegetation: dominated by evergreen broadleaf and palmate'
        'trees and shrubs (>1m). Woody vegetation cover >10%.',
        'LC_Type4_Class_3':
        '54a708, Deciduous Needleleaf Vegetation: dominated by deciduous needleleaf (larch) trees'
        'and shrubs (>1m). Woody vegetation cover >10%.',
        'LC_Type4_Class_4':
        '78d203, Deciduous Broadleaf Vegetation: dominated by deciduous broadleaf'
        'trees and shrubs (>1m).'
        'Woody vegetation cover >10%.',
        'LC_Type4_Class_5':
        '009900, Annual Broadleaf Vegetation: dominated by herbaceous annuals (<2m).'
        'At least 60% cultivated broadleaf crops.',
        'LC_Type4_Class_6':
        'b6ff05, Annual Grass Vegetation: dominated by herbaceous annuals (<2m) including'
        'cereal croplands.',
        'LC_Type4_Class_7':
        'f9ffa4, Non-Vegetated Lands: at least 60% of area is non-vegetated barren'
        '(sand, rock, soil) or permanent snow/ice with less than 10% vegetation.',
        'LC_Type4_Class_8':
        'a5a5a5, Urban and Built-up Lands: at least 30% impervious surface area including'
        'building materials, asphalt, and vehicles.',
        'LC_Type5_Class_0':
        '1c0dff, Water Bodies: at least 60% of area is covered by permanent water bodies.',
        'LC_Type5_Class_1':
        '05450a, Evergreen Needleleaf Trees: dominated by evergreen conifer trees (>2m).'
        'Tree cover >10%.',
        'LC_Type5_Class_2':
        '086a10, Evergreen Broadleaf Trees: dominated by evergreen broadleaf and palmate'
        'trees (>2m). Tree cover >10%.',
        'LC_Type5_Class_3':
        '54a708, Deciduous Needleleaf Trees: dominated by deciduous needleleaf (larch)'
        'trees (>2m). Tree cover >10%.',
        'LC_Type5_Class_4':
        '78d203, Deciduous Broadleaf Trees: dominated by deciduous broadleaf trees (>2m).'
        'Tree cover >10%.',
        'LC_Type5_Class_5':
        'dcd159, Shrub: Shrub (1-2m) cover >10%.',
        'LC_Type5_Class_6':
        'b6ff05, Grass: dominated by herbaceous annuals (<2m) that are not cultivated.',
        'LC_Type5_Class_7':
        'dade48, Cereal Croplands: dominated by herbaceous annuals (<2m). At least'
        '60% cultivated cereal crops.',
        'LC_Type5_Class_8':
        'c24f44, Broadleaf Croplands: dominated by herbaceous annuals (<2m). At'
        'least 60% cultivated broadleaf crops.',
        'LC_Type5_Class_9':
        'a5a5a5, Urban and Built-up Lands: at least 30% impervious surface area'
        'including building materials,'
        'asphalt, and vehicles.',
        'LC_Type5_Class_10':
        '69fff8, Permanent Snow and Ice: at least 60% of area is covered by snow and'
        'ice for at least 10'
        'months of the year.',
        'LC_Type5_Class_11':
        'f9ffa4, Non-Vegetated Lands: at least 60% of area is non-vegetated barren'
        '(sand, rock, soil) with'
        'less than 10% vegetation.',
        'LC_Prop1_Class_1':
        'f9ffa4, Barren: at least of area 60% is non-vegetated barren (sand, rock, soil)'
        'or permanent snow/ice'
        'with less than 10% vegetation.',
        'LC_Prop1_Class_2':
        '69fff8, Permanent Snow and Ice: at least 60% of area is covered by snow and ice for at'
        'least 10 months of the year.',
        'LC_Prop1_Class_3':
        '1c0dff, Water Bodies: at least 60% of area is covered by permanent water bodies.',
        'LC_Prop1_Class_11':
        '05450a, Evergreen Needleleaf Forests: dominated by evergreen conifer trees (>2m).'
        'Tree cover >60%.',
        'LC_Prop1_Class_12':
        '086a10, Evergreen Broadleaf Forests: dominated by evergreen broadleaf and palmate'
        'trees (>2m). Tree cover >60%.',
        'LC_Prop1_Class_13':
        '54a708, Deciduous Needleleaf Forests: dominated by deciduous needleleaf (larch)'
        'trees (>2m). Tree cover >60%.',
        'LC_Prop1_Class_14':
        '78d203, Deciduous Broadleaf Forests: dominated by deciduous broadleaf trees (>2m).'
        'Tree cover >60%.',
        'LC_Prop1_Class_15':
        '005a00, Mixed Broadleaf/Needleleaf Forests: co-dominated (40-60%) by broadleaf'
        'deciduous and evergreen needleleaf tree (>2m) types. Tree cover >60%.',
        'LC_Prop1_Class_16':
        '009900, Mixed Broadleaf Evergreen/Deciduous Forests: co-dominated (40-60%) by'
        'broadleaf evergreen and deciduous tree (>2m) types. Tree cover >60%.',
        'LC_Prop1_Class_21':
        '006c00, Open Forests: tree cover 30-60% (canopy >2m).',
        'LC_Prop1_Class_22':
        '00d000, Sparse Forests: tree cover 10-30% (canopy >2m).',
        'LC_Prop1_Class_31':
        'b6ff05, Dense Herbaceous: dominated by herbaceous annuals (<2m) at least 60% cover.',
        'LC_Prop1_Class_32':
        '98d604, Sparse Herbaceous: dominated by herbaceous annuals (<2m) 10-60% cover.',
        'LC_Prop1_Class_41':
        'dcd159, Dense Shrublands: dominated by woody perennials (1-2m) >60% cover.',
        'LC_Prop1_Class_42':
        'f1fb58, Shrubland/Grassland Mosaics: dominated by woody perennials (1-2m)'
        '10-60% cover with dense herbaceous annual understory.',
        'LC_Prop1_Class_43':
        'fbee65, Sparse Shrublands: dominated by woody perennials (1-2m)'
        '10-60% cover with minimal herbaceous understory.',
        'LC_Prop2_Class_1':
        'f9ffa4, Barren: at least of area 60% is non-vegetated barren (sand, rock, soil)'
        'or permanent snow/ice with'
        'less than 10% vegetation.',
        'LC_Prop2_Class_2':
        '69fff8, Permanent Snow and Ice: at least 60% of area is covered by snow and'
        'ice for at least 10 months of the year.',
        'LC_Prop2_Class_3':
        '1c0dff, Water Bodies: at least 60% of area is covered by permanent water bodies.',
        'LC_Prop2_Class_9':
        'a5a5a5, Urban and Built-up Lands: at least 30% of area is made up of'
        'impervious surfaces including building materials, asphalt, and vehicles.',
        'LC_Prop2_Class_10':
        '003f00, Dense Forests: tree cover >60% (canopy >2m).',
        'LC_Prop2_Class_20':
        '006c00, Open Forests: tree cover 10-60% (canopy >2m).',
        'LC_Prop2_Class_25':
        'e3ff77, Forest/Cropland Mosaics: mosaics of small-scale cultivation'
        '40-60% with >10% natural tree cover.',
        'LC_Prop2_Class_30':
        'b6ff05, Natural Herbaceous: dominated by herbaceous annuals (<2m).'
        'At least 10% cover.',
        'LC_Prop2_Class_35':
        '93ce04, Natural Herbaceous/Croplands Mosaics: mosaics of small-scale'
        'cultivation 40-60% with natural shrub or herbaceous vegetation.',
        'LC_Prop2_Class_36':
        '77a703, Herbaceous Croplands: dominated by herbaceous annuals (<2m).'
        'At least 60% cover. Cultivated fraction >60%.',
        'LC_Prop2_Class_40':
        'dcd159, Shrublands: shrub cover >60% (1-2m).',
        'LC_Prop3_Class_1':
        'f9ffa4, Barren: at least of area 60% is non-vegetated barren'
        '(sand, rock, soil) or permanent snow/ice with less than 10% vegetation.',
        'LC_Prop3_Class_2':
        '69fff8, Permanent Snow and Ice: at least 60% of area is covered by snow'
        'and ice for at least 10 months of the year.',
        'LC_Prop3_Class_3':
        '1c0dff, Water Bodies: at least 60% of area is covered by permanent water bodies.',
        'LC_Prop3_Class_10':
        '003f00, Dense Forests: tree cover >60% (canopy >2m).',
        'LC_Prop3_Class_20':
        '006c00, Open Forests: tree cover 10-60% (canopy >2m).',
        'LC_Prop3_Class_27':
        '72834a, Woody Wetlands: shrub and tree cover >10% (>1m).'
        'Permanently or seasonally inundated.',
        'LC_Prop3_Class_30':
        'b6ff05, Grasslands: dominated by herbaceous annuals (<2m) >10% cover.',
        'LC_Prop3_Class_40':
        'c6b044, Shrublands: shrub cover >60% (1-2m).',
        'LC_Prop3_Class_50':
        '3aba73, Herbaceous Wetlands: dominated by herbaceous annuals (<2m)'
        '>10% cover. Permanently or seasonally inundated.',
        'LC_Prop3_Class_51':
        '1e9db3, Tundra: tree cover <10%. Snow-covered for at least 8 months of the year.',
        'QC_Class_0':
        'Classified land: has a classification label and is land according to the water mask.',
        'QC_Class_1':
        'Unclassified land: not classified because of missing data but land according to the water'
        'mask, labeled as barren.',
        'QC_Class_2':
        'Classified water: has a classification label and is water according to the water mask.',
        'QC_Class_3':
        'Unclassified water: not classified because of missing data but water'
        'according to the water mask.',
        'QC_Class_4':
        'Classified sea ice: classified as snow/ice but water mask says it is water and less'
        'than 100m elevation switched to water.',
        'QC_Class_5':
        'Misclassified water: classified as water but water mask says it is land, switched to'
        'secondary label.',
        'QC_Class_6':
        'Omitted snow/ice: land according to the water mask that was classified as'
        'something other than snow but with a maximum annual temperature'
        'below 1◦C, relabeled as snow/ice.',
        'QC_Class_7':
        'Misclassified snow/ice: land according to the water mask that was classified as snow'
        'but with a minimum annual temperature greater than 1◦C, relabeled as barren.',
        'QC_Class_8':
        'Backfilled label: missing label from stabilization, filled with'
        'the pre-stabilized result.',
        'QC_Class_9':
        'Forest type changed: climate-based change to forest class.',
        'LW_Class_1':
        '1c0dff, Water',
        'LW_Class_2':
        'f9ffa4, Land'
    },
    'MODIS/006/MOD44W': {
        'Water_Mask_Class_0': 'Land',
        'Water_Mask_Class_1': 'Water',
        'Water_Mask_Class_250': 'Outside of Projection',
        'QA_1': 'High confidence observation',
        'QA_2': 'Lower confidence water, but MOD44W V5 indicated water',
        'QA_3': 'Lower confidence land',
        'QA_4': 'Ocean mask',
        'QA_5': 'Ocean mask, but no water observations recorded',
        'QA_6': 'Burned area (MCD64A1)',
        'QA_7': 'Urban or impervious surface',
        'QA_8': 'No water detected, but MOD44W V5 shows inland water',
        'QA_10': 'Fill - outside of projected area'
    },
    'MODIS/006/MOD14A1': {
        'FireMask_Class_0': 'Not processed (missing input data)',
        'FireMask_Class_1':
        'Not processed (obsolete; not used since Collection 1)',
        'FireMask_Class_2': 'Not processed (other reason)',
        'FireMask_Class_3': 'Non-fire water pixel',
        'FireMask_Class_4': 'Cloud (land or water)',
        'FireMask_Class_5': 'Non-fire land pixel',
        'FireMask_Class_6': 'Unknown (land or water)',
        'FireMask_Class_7': 'Fire (low confidence, land or water)',
        'FireMask_Class_8': 'Fire (nominal confidence, land or water)',
        'FireMask_Class_9': 'Fire (high confidence, land or water)',
        'QA_bit_0_1_land_water_state_0': 'Water',
        'QA_bit_0_1_land_water_state_1': 'Coast',
        'QA_bit_0_1_land_water_state_2': 'Land',
        'QA_bit_0_1_land_water_state_3': 'Missing data',
        'QA_bit_2_night_day_0': 'Night',
        'QA_bit_2_night_day_1': 'Day'
    },
    'MODIS/006/MOD14A2': {
        'FireMask_Class_0': 'Not processed (missing input data)',
        'FireMask_Class_1':
        'Not processed (obsolete; not used since Collection 1)',
        'FireMask_Class_2': 'Not processed (other reason)',
        'FireMask_Class_3': 'Non-fire water pixel',
        'FireMask_Class_4': 'Cloud (land or water)',
        'FireMask_Class_5': 'Non-fire land pixel',
        'FireMask_Class_6': 'Unknown (land or water)',
        'FireMask_Class_7': 'Fire (low confidence, land or water)',
        'FireMask_Class_8': 'Fire (nominal confidence, land or water)',
        'FireMask_Class_9': 'Fire (high confidence, land or water)',
        'QA_bit_0_1_land_water_state_0': 'Water',
        'QA_bit_0_1_land_water_state_1': 'Coast',
        'QA_bit_0_1_land_water_state_2': 'Land',
        'QA_bit_0_1_land_water_state_3': 'Missing data',
        'QA_bit_2_night_day_0': 'Night',
        'QA_bit_2_night_day_1': 'Day'
    }
}
