# -*- coding: utf-8 -*-
from __future__ import absolute_import

import logging

logger = logging.getLogger(__name__)

import os
import tempfile
import shutil
from distutils import spawn
from jinja2 import Environment, FileSystemLoader
from yaml import load as yaml_load

from .exceptions import (HarbormasterNotInitializedException,
                         HarbormasterVersionCompatibilityException)

class MakeTempDir(object):
    temp_dir = None

    def __enter__(self):
        self.temp_dir = tempfile.mkdtemp()
        logger.debug('Using temporary directory %s...', self.temp_dir)
        return self.temp_dir

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            logger.debug('Cleaning up temporary directory %s...', self.temp_dir)
            shutil.rmtree(self.temp_dir)
        except Exception, e:
            logger.exception('Failure cleaning up temp space')
            pass

make_temp_dir = MakeTempDir

def extract_hosts_from_harbormaster_compose(base_path):
    compose_file = os.path.normpath(
        os.path.join(
            base_path,
            'harbormaster',
            'harbormaster.yml'
        )
    )
    try:
        ifs = open(compose_file)
    except OSError:
        raise HarbormasterNotInitializedException()
    compose_data = yaml_load(ifs)
    ifs.close()
    if not int(compose_data.pop('version', 1)) == 2:
        raise HarbormasterVersionCompatibilityException()
    services = compose_data.pop('services', {})
    return [key for key in services.keys() if key != 'harbormaster']


def jinja_render_to_temp(template_file, temp_dir, dest_file, **context):
    j2_tmpl_path = os.path.normpath(
        os.path.join(
            os.path.dirname(__file__),
            'templates'))
    j2_env = Environment(loader=FileSystemLoader(j2_tmpl_path))
    j2_tmpl = j2_env.get_template(template_file)
    dockerfile = j2_tmpl.render(context)
    open(os.path.join(temp_dir, dest_file), 'w').write(
        dockerfile.encode('utf8'))

def which_docker():
    return spawn.find_executable('docker')

