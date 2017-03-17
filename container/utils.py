# -*- coding: utf-8 -*-
from __future__ import absolute_import

from .visibility import getLogger
logger = getLogger(__name__)

import os
import importlib

from jinja2 import Environment, FileSystemLoader

from .exceptions import AnsibleContainerException, AnsibleContainerNotInitializedException
from .config import AnsibleContainerConfig
from .temp import MakeTempDir


__all__ = ['AVAILABLE_SHIPIT_ENGINES',
           'assert_initialized',
           'create_path',
           'config_format_version',
           'get_config',
           'get_latest_image_for',
           'jinja_render_to_temp',
           'jinja_template_path',
           'load_engine',
           'load_shipit_engine',
           'make_temp_dir',
           ]

AVAILABLE_SHIPIT_ENGINES = {
    'kube': {
        'help': 'Generate a role that deploys to Kubernetes.',
        'cls': 'kubernetes'
    },
    'openshift': {
        'help': 'Generate a role that deploys to OpenShift Origin.',
        'cls': 'openshift'
    }
}


make_temp_dir = MakeTempDir

def create_path(path):
    try:
        os.makedirs(path)
    except OSError:
        pass
    except Exception as exc:
        raise AnsibleContainerException("Error: failed to create %s - %s" % (path, str(exc)))

def jinja_template_path():
    return os.path.normpath(
        os.path.join(
            os.path.dirname(__file__),
            'templates'))

def jinja_render_to_temp(template_file, temp_dir, dest_file, **context):
    j2_tmpl_path = jinja_template_path()
    j2_env = Environment(loader=FileSystemLoader(j2_tmpl_path))
    j2_tmpl = j2_env.get_template(template_file)
    rendered = j2_tmpl.render(dict(temp_dir=temp_dir, **context))
    logger.debug('Rendered Jinja Template:', body=rendered.encode('utf8'))
    open(os.path.join(temp_dir, dest_file), 'wb').write(
        rendered.encode('utf8'))

def get_config(base_path, var_file=None):
    return AnsibleContainerConfig(base_path, var_file=var_file)

def config_format_version(base_path, config_data=None):
    if not config_data:
        config_data = get_config(base_path)
    return int(config_data.pop('version', 1))

def assert_initialized(base_path):
    ansible_dir = os.path.normpath(base_path)
    container_file = os.path.join(ansible_dir, 'container.yml')
    if not all((
        os.path.exists(ansible_dir), os.path.isdir(ansible_dir),
        os.path.exists(container_file), os.path.isfile(container_file),
    )):
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

def load_engine(engine_name='', base_path='', **kwargs):
    """

    :param engine_name: the string for the module containing the engine.py code
    :param base_path: the base path during operation
    :return: container.engine.BaseEngine
    """
    mod = importlib.import_module('container.%s.engine' % engine_name)
    project_name = os.path.basename(base_path).lower()
    logger.debug('Engine loaded for project', name=project_name, path=base_path)
    return mod.Engine(base_path, project_name, kwargs)


def load_shipit_engine(engine_class, **kwargs):
    '''
    Given a class name, dynamically load a shipit engine.

    :param engine_class: name of the shipit engine class
    :param kwargs: key/value args to pass to the new shipit engine obj.
    :return: shipit engine object
    '''
    try:
        engine_module = importlib.import_module(
            'container.shipit.%s.engine' % engine_class)
    except ImportError as exc:
        raise ImportError(
            'No shipit module for %s found - %s' % (engine_class, str(exc)))
    try:
        engine_cls = getattr(engine_module, 'ShipItEngine')
    except Exception as exc:
        raise ImportError('Error getting ShipItEngine for %s - %s' % (engine_class, str(exc)))

    return engine_cls(**kwargs)


