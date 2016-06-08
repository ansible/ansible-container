# -*- coding: utf-8 -*-
from __future__ import absolute_import

import logging

logger = logging.getLogger(__name__)

import os
import sys
from StringIO import StringIO
from functools import wraps
from distutils import spawn

from ..utils import *

from compose.cli.command import project_from_options
from compose.cli import main
from compose.cli.log_printer import LogPrinter, build_log_presenters

__all__ = ['teed_stdout',
           'which_docker',
           'launch_docker_compose',
           'extract_hosts_from_docker_compose']

# Don't try this at home, kids.

# *sigh* Okay, fine. Well...
# We need to tee the stdout to a StringIO buffer as well as to stdout.
# If you've got a better idea, I'm all ears.

class Tee(StringIO):
    def write(self, x):
        StringIO.write(self, x)
        sys.stdout.write(x)

    def flush(self):
        StringIO.flush(self)
        sys.stdout.flush()


def monkeypatch__log_printer_from_project(buffer):
    @wraps(main.log_printer_from_project)
    def __wrapped__(
            project,
            containers,
            monochrome,
            log_args,
            cascade_stop=False,
            event_stream=None,
    ):
        return LogPrinter(
            containers,
            build_log_presenters(project.service_names, monochrome),
            event_stream or project.events(),
            cascade_stop=cascade_stop,
            output=buffer,
            log_args=log_args)

    return __wrapped__


original__log_printer_from_project = main.log_printer_from_project


class TeedStdout(object):
    stdout = None

    def __enter__(self):
        self.stdout = StringIO()
        main.log_printer_from_project = monkeypatch__log_printer_from_project(self.stdout)
        return self.stdout

    def __exit__(self, exc_type, exc_val, exc_tb):
        main.log_printer_from_project = original__log_printer_from_project

teed_stdout = TeedStdout

# Phew. That sucked.

def which_docker():
    return spawn.find_executable('docker')

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

def launch_docker_compose(base_path, project_name, temp_dir, verb, services=[],
                          no_color=False, extra_command_options=dict(), **context):
    version = compose_format_version(base_path)
    jinja_render_to_temp(('%s-docker-compose.j2.yml' if version == 2
                         else '%s-docker-compose-v1.j2.yml') % (verb,),
                         temp_dir,
                         'docker-compose.yml',
                         hosts=extract_hosts_from_docker_compose(
                             base_path),
                         project_name=project_name,
                         base_path=os.path.realpath(base_path),
                         **context)
    options = DEFAULT_COMPOSE_OPTIONS.copy()
    options.update({
        u'--file': [
            os.path.normpath(
                os.path.join(base_path,
                             'ansible',
                             'container.yml')
            ),
            os.path.join(temp_dir,
                         'docker-compose.yml')],
        u'COMMAND': 'up',
        u'ARGS': ['--no-build'] + services
    })
    command_options = DEFAULT_COMPOSE_UP_OPTIONS.copy()
    command_options[u'--no-build'] = True
    command_options[u'--no-color'] = no_color
    command_options[u'SERVICE'] = services
    command_options.update(extra_command_options)
    project = project_from_options(base_path, options)
    command = main.TopLevelCommand(project)
    command.up(command_options)

def extract_hosts_from_docker_compose(base_path):
    compose_data = parse_compose_file(base_path)
    if compose_format_version(base_path, compose_data) == 2:
        services = compose_data.pop('services', {})
    else:
        services = compose_data
    return [key for key in services.keys() if key != 'ansible-container']
