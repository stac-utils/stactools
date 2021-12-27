""" CLI for test data maintenance and generation.
"""
import os
import shutil
import logging
from tempfile import TemporaryDirectory

import click

from stactools.core.utils.subprocess import call

logger = logging.getLogger(__name__)


@click.group()
def cli() -> None:
    pass


@cli.command("make-rasters-smaller")
@click.option("--dir",
              required=True,
              help="Directory to walk and transform rasters.")
@click.option("-n",
              "--dry-run",
              required=True,
              help="Do a dry run; print commands.",
              is_flag=True)
def make_rasters_smaller_cmd(dir: str, dry_run: bool) -> None:

    def make_it_smaller(tif_path: str) -> None:
        with TemporaryDirectory() as tmp_dir:
            tmp_path = os.path.join(tmp_dir, "smaller.tif")
            translate_cmd = [
                "gdal_translate", "-of", "GTiff", "-outsize", "512", "512",
                tif_path, tmp_path
            ]
            if dry_run:
                logger.info(' '.join(translate_cmd))
            else:
                call(translate_cmd)

                shutil.move(tmp_path, tif_path)

    for root, _, files in os.walk(dir):
        for f in files:
            if f.lower().endswith('.tif'):
                full_path = os.path.join(root, f)
                make_it_smaller(full_path)


def run_cli() -> None:
    cli(prog_name='testutils')


if __name__ == "__main__":
    run_cli()
