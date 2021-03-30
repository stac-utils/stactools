import logging
import json
import os
from typing import Optional

import click
import pystac

from stactools.aster.cog import create_cogs
from stactools.aster.stac import create_item
from stactools.aster.xml_metadata import XmlMetadata

logger = logging.getLogger(__name__)


def create_aster_command(cli):
    """Creates a command group for commands working with
    ASTER L1T Radiance Version 003 data.
    """
    @cli.group('aster',
               short_help=("Commands for working with "
                           "ASTER L1T Radiance Version 003 data."))
    def aster():
        pass

    @aster.command("create-cogs",
                   short_help="Generates COGs from ASTER L1T HDF EOS data.")
    @click.option('--hdf', required=True, help="HREF to the HDF file")
    @click.option('--xml',
                  required=True,
                  help="HREF to the hdf.xml metadata file")
    @click.option("--output",
                  required=True,
                  help="The output directory to write the COGs to.")
    def create_aster_cogs_cmd(hdf, xml, output):
        xml_metadata = XmlMetadata.from_file(xml)
        create_cogs(hdf, xml_metadata, output)

    @aster.command('create-item',
                   short_help='Create a STAC Item from a ASTER XML file')
    @click.option('--xml', required=True, help='XML metadat file (.hdf.xml).')
    @click.option('--vnir', help="HREF to the VNIR COG file.")
    @click.option('--swir', help="HREF to the SWIR COG file.")
    @click.option('--tir', help="HREF to the TIR COG file.")
    @click.option('--hdf', help="HREF to the HDF EOS data.")
    @click.option('--vnir-browse', help="HREF to the VNIR browse image.")
    @click.option('--tir-browse', help="HREF to the TIR browse image.")
    @click.option('--qa-browse', help="HREF to the QA browse image.")
    @click.option('--qa-txt',
                  help="HREF to the geometric quality assessment report.")
    @click.option('-o',
                  "--output",
                  required=True,
                  help='Output directory to save STAC items to.')
    @click.option(
        '-p',
        '--providers',
        help='Path to JSON file containing array of additional providers')
    def create_item_cmd(xml: str, vnir: str, swir: str, tir: str,
                        hdf: Optional[str], vnir_browse: Optional[str],
                        tir_browse: Optional[str], qa_browse: Optional[str],
                        qa_txt: Optional[str], output,
                        providers: Optional[str]):
        """Creates a STAC Item based on metadata from an HDF-EOS
        ASTER L1T Radiance Version 003 XML metadata file an d
        VNIR, SWIR, and TIR COG files.
        """
        additional_providers = None
        if providers is not None:
            with open(providers) as f:
                additional_providers = [
                    pystac.Provider.from_dict(d) for d in json.load(f)
                ]

        item = create_item(xml,
                           vnir_cog_href=vnir,
                           swir_cog_href=swir,
                           tir_cog_href=tir,
                           hdf_href=hdf,
                           vnir_browse_href=vnir_browse,
                           tir_browse_href=tir_browse,
                           qa_browse_href=qa_browse,
                           qa_txt_href=qa_txt,
                           additional_providers=additional_providers)

        item_path = os.path.join(output, '{}.json'.format(item.id))
        item.set_self_href(item_path)

        item.save_object()

    return aster
