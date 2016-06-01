# -*- coding: utf-8 -*-
from __future__ import absolute_import

import logging

logger = logging.getLogger(__name__)

import os
import tempfile
import shutil
import importlib
from jinja2 import Environment, FileSystemLoader
from yaml import load as yaml_load

from .exceptions import AnsibleContainerNotInitializedException

__all__ = ['make_temp_dir',
           'jinja_template_path',
           'jinja_render_to_temp',
           'parse_compose_file',
           'compose_format_version',
           'assert_initialized',
           'get_latest_image_for',
           'load_engine']


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


def jinja_template_path():
    return os.path.normpath(
        os.path.join(
            os.path.dirname(__file__),
            'templates'))

def jinja_render_to_temp(template_file, temp_dir, dest_file, **context):
    j2_tmpl_path = jinja_template_path()
    j2_env = Environment(loader=FileSystemLoader(j2_tmpl_path))
    j2_tmpl = j2_env.get_template(template_file)
    dockerfile = j2_tmpl.render(context)
    open(os.path.join(temp_dir, dest_file), 'w').write(
        dockerfile.encode('utf8'))

def parse_compose_file(base_path):
    compose_file = os.path.normpath(
        os.path.join(
            base_path,
            'ansible',
            'container.yml'
        )
    )
    try:
        ifs = open(compose_file)
    except OSError:
        raise AnsibleContainerNotInitializedException()
    compose_data = yaml_load(ifs)
    ifs.close()
    return compose_data

def compose_format_version(base_path, compose_data=None):
    if not compose_data:
        compose_data = parse_compose_file(base_path)
    return int(compose_data.pop('version', 1))


def assert_initialized(base_path):
    ansible_dir = os.path.normpath(
        os.path.join(base_path, 'ansible'))
    container_file = os.path.join(ansible_dir, 'container.yml')
    if not os.path.exists(ansible_dir) or not os.path.isdir(ansible_dir) or \
            not os.path.exists(container_file) or not os.path.isfile(container_file):
        raise AnsibleContainerNotInitializedException()

def get_latest_image_for(project_name, host, client):
    image_data = client.images(
        '%s-%s' % (project_name, host,)
    )
    try:
        latest_image_data, = [datum for datum in image_data
                              if '%s-%s:latest' % (project_name, host,) in
                              datum['RepoTags']]
        image_buildstamp = [tag for tag in latest_image_data['RepoTags']
                            if not tag.endswith(':latest')][0].split(':')[-1]
        image_id = latest_image_data['Id']
        return image_id, image_buildstamp
    except (IndexError, ValueError):
        # No previous image built
        return None, None

def load_engine(engine_name, base_path):
    """

    :param engine_name: the string for the module containing the engine.py code
    :param base_path: the base path during operation
    :return: container.engine.BaseEngine
    """
    mod = importlib.import_module('container.%s.engine' % engine_name)
    project_name = os.path.basename(base_path).lower()
    return mod.Engine(base_path, project_name)
