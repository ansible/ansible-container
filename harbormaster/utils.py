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
from compose.cli.command import project_from_options
from compose.cli.main import TopLevelCommand

from .exceptions import HarbormasterNotInitializedException


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

# Docker-compose uses docopt, which outputs things like the below
# So I'm starting with the defaults and then updating them.
# One structure for the global options and one for the command specific

DEFAULT_COMPOSE_OPTIONS = {
    u'--help': False,
    u'--host': None,
    u'--project-name': None,
    u'--skip-hostname-check': False,
    u'--tls': False,
    u'--tlscacert': None,
    u'--tlscert': None,
    u'--tlskey': None,
    u'--tlsverify': False,
    u'--verbose': False,
    u'--version': False,
    u'-h': False,
    u'--file': [],
    u'COMMAND': None,
    u'ARGS': []
}

DEFAULT_COMPOSE_UP_OPTIONS = {
    u'--abort-on-container-exit': False,
    u'--build': False,
    u'--force-recreate': False,
    u'--no-color': False,
    u'--no-deps': False,
    u'--no-recreate': False,
    u'--no-build': False,
    u'--remove-orphans': False,
    u'--timeout': None,
    u'-d': False,
    u'SERVICE': []
}

def launch_docker_compose(base_path, temp_dir, verb, **context):
    version = compose_format_version(base_path)
    jinja_render_to_temp(('%s-docker-compose.j2.yml' if version == 2
                         else '%s-docker-compose-v1.j2.yml') % (verb,),
                         temp_dir,
                         'docker-compose.yml',
                         hosts=extract_hosts_from_harbormaster_compose(
                             base_path),
                         **context)
    options = DEFAULT_COMPOSE_OPTIONS.copy()
    options.update({
        u'--file': [
            os.path.normpath(
                os.path.join(base_path,
                             'harbormaster',
                             'harbormaster.yml')
            ),
            os.path.join(temp_dir,
                         'docker-compose.yml')],
        u'COMMAND': 'up',
        u'ARGS': ['--no-build']
    })
    command_options = DEFAULT_COMPOSE_UP_OPTIONS.copy()
    command_options[u'--no-build'] = True
    os.environ['HARBORMASTER_BASE'] = os.path.realpath(base_path)
    project = project_from_options('.', options)
    command = TopLevelCommand(project)
    command.up(command_options)

def extract_hosts_from_harbormaster_compose(base_path):
    compose_data = parse_compose_file(base_path)
    if compose_format_version(base_path, compose_data) == 2:
        services = compose_data.pop('services', {})
    else:
        services = compose_data
    return [key for key in services.keys() if key != 'harbormaster']

def extract_hosts_touched_by_playbook(base_path):
    compose_data = parse_compose_file(base_path)
    if compose_format_version(base_path, compose_data) == 2:
        services = compose_data.pop('services', {})
    else:
        services = compose_data
    ansible_args = services.get('harbormaster', {}).get('command', [])
    if not ansible_args:
        logger.warning('No ansible playbook arguments found in harbormaster.yml')
        return []



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

def which_docker():
    return spawn.find_executable('docker')

def parse_compose_file(base_path):
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
    return compose_data

def compose_format_version(base_path, compose_data=None):
    if not compose_data:
        compose_data = parse_compose_file(base_path)
    return int(compose_data.pop('version', 1))
