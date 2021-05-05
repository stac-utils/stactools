import os
import shutil
from tempfile import TemporaryDirectory
from subprocess import Popen, call

import click
import jinja2
from pystac.utils import make_absolute_href


def launch_browser(catalog_uri):
    catalog_uri = make_absolute_href(catalog_uri)

    catalog_dir = os.path.dirname(catalog_uri)
    catalog_filename = os.path.basename(catalog_uri)

    with TemporaryDirectory() as tmp_dir:
        for fname in ['Dockerfile-node', 'Dockerfile-titiler']:
            p = os.path.join(os.path.dirname(__file__), fname)
            shutil.copy(p, os.path.join(tmp_dir, fname))

        # Load template docker-compose
        template_loader = jinja2.FileSystemLoader(
            searchpath=os.path.dirname(__file__))
        template_env = jinja2.Environment(loader=template_loader)
        template_file = "docker-compose.yml.template"
        template = template_env.get_template(template_file)

        rendered_docker_compose = template.render(
            catalog_dir=catalog_dir, catalog_filename=catalog_filename)

        with open(os.path.join(tmp_dir, "docker-compose.yml"), 'w') as f:
            f.write(rendered_docker_compose)

        curdir = os.path.abspath(os.curdir)
        try:
            os.chdir(tmp_dir)
            p = Popen(['docker-compose', 'up'])
            p.wait()
        finally:
            call(['docker-compose', 'kill'])
            p.terminate()
            os.chdir(curdir)


def browse_command(cli):
    @cli.command(
        'browse',
        short_help=('Launch a local stac-browser and tiler via docker '
                    'to browse a STAC'))
    @click.argument('catalog')
    def cmd(catalog):
        """Launch docker containers that serve the STAC at CATALOG through stac-browser.

        This requires docker to be installed. This will build and run 3 containers,
        one for serving the STAC, one for running stac-browser, and one for running
        titiler, which is used to render tiles of 3 band COGs on the stac-browser
        Item map.
        """
        launch_browser(catalog)

    return cmd
