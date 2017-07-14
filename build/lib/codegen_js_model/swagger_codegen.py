from __future__ import absolute_import
import codecs
import requests
try:
    import simplejson as json
except ImportError:
    import json
from multiprocessing import Pool
from os import makedirs
from os.path import join, exists, dirname

import yaml
import click

from ._version import __version__
from .parser import Swagger
from .base import Template
from .wxapp import WxAppGenerator


def spec_load(filename):
    if filename.endswith('.json'):
        loader = json.load
    elif filename.endswith('.yml') or filename.endswith('.yaml'):
        loader = yaml.load
    else:
        with codecs.open(filename, 'r', 'utf-8') as f:
            contents = f.read()
            contents = contents.strip()
            if contents[0] in ['{', '[']:
                loader = json.load
            else:
                loader = yaml.load
    if filename.startswith('http'):
        r = requests.get(filename)
        return r.json()
    else:
        with codecs.open(filename, 'r', 'utf-8') as f:
            return loader(f)


def write(dist, content):
    dir_ = dirname(dist)
    if not exists(dir_):
        makedirs(dir_)
    with codecs.open(dist, 'w', 'utf-8') as f:
        f.write(content)


def _copy_ui_dir(ui_dest, ui_src):
    from distutils.dir_util import copy_tree
    from os import unlink

    if exists(ui_dest):
        status = 'skip'
    else:
        status = 'generate'
        makedirs(ui_dest)
        copy_tree(ui_src, ui_dest)
        unlink(join(ui_dest, 'index.html'))
    return status


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo('current version: %s' % __version__)
    ctx.exit()


@click.command()
@click.argument('destination', required=True)
@click.option('-s', '--swagger', '--swagger-doc',
              required=True, help='Swagger doc file or url.')
@click.option('-f', '--force',
              default=False, is_flag=True, help='Force overwrite.')
@click.option('-p', '--package',
              help='Package name / application name.')
@click.option('-t', '--template-dir',
              help='Path of your custom templates directory.')
@click.option('--spec', '--specification',
              default=False, is_flag=True,
              help='Generate online specification json response.')
@click.option('-j', '--jobs',
              default=4, help='Parallel jobs for processing.')
@click.option('-tlp', '--templates',
              default='wxapp', help='gen wxapp templates,default wxapp.')
@click.option('--version', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True,
              help='Show current version.')
def generate(destination, swagger_doc, force=False, package=None,
             template_dir=None, templates='wxapp',
             specification=False, jobs=4):
    pool = Pool(processes=int(jobs))
    package = package or destination.replace('-', '_')
    data = spec_load(swagger_doc)
    swagger = Swagger(data, pool)
    if templates == 'wxapp':
        generator = WxAppGenerator(swagger)
    else:
        return
    generator.with_spec = specification
    template = Template()
    env = dict(package=package,
               module=swagger.module_name)
    for code in generator.generate():
        source = template.render_code(code)
        dest = join(destination, code.dest(env))
        dest_exists = exists(dest)
        can_override = force or code.override
        statuses = {
            (False, False): 'generate',
            (False, True): 'generate',
            (True, False): 'skip',
            (True, True): 'override'
        }
        status = statuses[(dest_exists, can_override)]
        click.secho('%-12s' % status, nl=False)
        click.secho(dest)

        if status != 'skip':
            write(dest, source)