# -*- coding: utf-8 -*-
from __future__ import absolute_import

import logging
from datetime import datetime

from container.utils import create_path, logger, jinja_render_to_temp

logger = logging.getLogger(__name__)

import os
import importlib
import tempfile
import shutil

from jinja2 import Environment, FileSystemLoader


class MakeTempDir(object):
    temp_dir = None

    def __enter__(self):
        self.temp_dir = tempfile.mkdtemp()
        logger.debug('Using temporary directory %r...', self.temp_dir)
        return os.path.realpath(self.temp_dir)

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            logger.debug('Cleaning up temporary directory %r...', self.temp_dir)
            shutil.rmtree(self.temp_dir)
        except Exception:
            logger.exception('Failure cleaning up temp space %r', self.temp_dir)

conductor_dir = os.path.normpath(os.path.dirname(__file__))

make_temp_dir = MakeTempDir

def jinja_render_to_temp(templates_path, template_file, temp_dir, dest_file, **context):
    j2_env = Environment(loader=FileSystemLoader(templates_path))
    j2_tmpl = j2_env.get_template(template_file)
    rendered = j2_tmpl.render(dict(temp_dir=temp_dir, **context))
    logger.debug('Rendered Jinja Template:')
    logger.debug(rendered.encode('utf8'))
    open(os.path.join(temp_dir, dest_file), 'wb').write(
        rendered.encode('utf8'))


def metadata_to_image_config(metadata):

    def ports_to_exposed_ports(list_of_ports):
        to_return = {}
        for port_spec in list_of_ports:
            exposed_ports = port_spec.rsplit(':')[-1]
            if '-' in exposed_ports:
                low, high = exposed_ports.split('-', 1)
                for port in range(int(low), int(high)+1):
                    to_return[str(port)] = {}
            else:
                to_return[exposed_ports] = {}
        return to_return

    def format_environment(environment):
        if isinstance(environment, dict):
            return ['='.join(tpl) for tpl in environment.iteritems()]
        else:
            return environment

    TRANSLATORS = {
        # Keys are the key found in the service_data
        # Values are a 2-tuple of the image config JSON key and a function to
        # convert the service_data value to the image config JSON value or None
        # if no translation is necessary

        'hostname': ('Hostname', None),
        'domainname': ('Domainname', None),
        'user': ('User', None),
        'ports': ('ExposedPorts', ports_to_exposed_ports),
        'environment': ('Env', lambda _obj: format_environment),
        'command': ('Cmd', None),
        'working_dir': ('WorkingDir', None),
        'entrypoint': ('Entrypoint', None),
        'volumes': ('Volumes', lambda _list: {parts[0]:{}
                                              for parts in [v.split()
                                                            for v in _list]}),
        'labels': ('Labels', None),
        'onbuild': ('OnBuild', None)
    }

    config = dict(
        Hostname='',
        Domainname='',
        User='',
        ExposedPorts={},
        Env=[],
        Cmd='',
        WorkingDir='',
        Entrypoint=None,
        Volumes={},
        Labels={},
        OnBuild=[]
    )

    for metadata_key, (key, translator) in TRANSLATORS.iteritems():
        if metadata_key in metadata:
            config[key] = (translator(metadata[metadata_key]) if translator
                           else metadata[metadata_key])
    return config


def create_role_from_templates(role_name=None, role_path=None, project_name=None, description=None):
    '''
    Create a new role with initial files from templates.
    :param role_name: Name of the role
    :param role_path: Full path to the role
    :param project_name: Name of the project, or the base path name.
    :param description: One line description of the role.
    :return: None
    '''

    role_paths = {
        u'base': [u'README.j2', u'travis.j2.yml'],
        u'defaults': [u'defaults.j2.yml'],
        u'meta': [u'meta.j2.yml'],
        u'test': [u'test.j2.yml', u'travis.j2.yml'],
        u'tasks': [],
    }

    context = {
        u'role_name': role_name,
        u'project_name': project_name,
        u'role_description': description
    }

    create_path(role_path)

    for p, templates in role_paths.items():
        target_dir = os.path.join(role_path, p) if p != 'base' else role_path
        if p != 'base':
            create_path(target_dir)
        for template in templates:
            target_name = template.replace('.j2', '')
            if target_name.startswith('travis'):
                target_name = '.' + target_name
            if target_name.startswith('defaults') or target_name.startswith('meta'):
                target_name = 'main.yml'
            if not os.path.exists(os.path.join(target_dir, target_name)):
                logger.debug("Rendering template for %s/%s" % (target_dir, template))
                jinja_render_to_temp('role/%s' % template,
                                     target_dir,
                                     target_name,
                                     **context)

    new_file_name = "main_{}.yml".format(datetime.today().strftime('%y%m%d%H%M%S'))
    new_tasks_file = os.path.join(role_path, 'tasks', new_file_name)
    tasks_file = os.path.join(role_path, 'tasks', 'main.yml')

    if os.path.exists(tasks_file):
        logger.debug("Backing up tasks/main.yml to {}".format(new_file_name))
        os.rename(tasks_file, new_tasks_file)
