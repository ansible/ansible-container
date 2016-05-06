# -*- coding: utf-8 -*-
from __future__ import absolute_import

import logging

logger = logging.getLogger(__name__)

import os
import sys
import argparse
import tarfile
import tempfile
import shutil
import datetime
from distutils import spawn
from jinja2 import Environment, FileSystemLoader
from yaml import load as yaml_load

import docker
from docker.utils import kwargs_from_env
from compose.cli.command import project_from_options
from compose.cli.main import TopLevelCommand

from logging import config
logging.config.dictConfig(
    {
        'version': 1,
        'disable_existing_loggers': True,
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            'harbormaster': {
                'handlers': ['console'],
                'level': 'INFO',
            },
            'compose': {
                'handlers': [],
                'level': 'INFO'
            },
            'docker': {
                'handlers': [],
                'level': 'INFO'
            }
        },
    }
)

AVAILABLE_COMMANDS = ['help', 'init', 'build', 'run']


class HarbormasterNotInitializedException(Exception):
    pass


class HarbormasterVersionCompatibilityException(Exception):
    pass


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


def build_buildcontainer_image(base_path):
    # To ensure version compatibility, we have to generate the kwargs ourselves
    client_kwargs = kwargs_from_env(assert_hostname=False)
    client = docker.AutoVersionClient(**client_kwargs)
    temp_dir = tempfile.mkdtemp()
    try:
        logger.info('Building Docker Engine context...')
        tarball_path = os.path.join(temp_dir, 'context.tar')
        tarball_file = open(tarball_path, 'wb')
        tarball = tarfile.TarFile(fileobj=tarball_file,
                                  mode='w')
        harbormaster_dir = os.path.normpath(os.path.join(base_path,
                                                         'harbormaster'))
        try:
            tarball.add(harbormaster_dir, arcname='harbormaster')
        except OSError:
            raise HarbormasterNotInitializedException()
        jinja_render_to_temp('ansible-dockerfile.j2', temp_dir, 'Dockerfile')
        tarball.add(os.path.join(temp_dir, 'Dockerfile'),
                    arcname='Dockerfile')
        jinja_render_to_temp('hosts.j2', temp_dir, 'hosts',
                             hosts=extract_hosts_from_harbormaster_compose(base_path))
        tarball.add(os.path.join(temp_dir, 'hosts'), arcname='hosts')
        tarball.close()
        tarball_file = open(tarball_path, 'rb')
        logger.info('Starting Docker build of Harbormaster image...')
        return [streamline for streamline in client.build(fileobj=tarball_file,
                                                          rm=True,
                                                          custom_context=True,
                                                          pull=True,
                                                          forcerm=True,
                                                          tag='ansible-builder')]
    finally:
        try:
            shutil.rmtree(temp_dir)
        except Exception, e:
            logger.exception('Failure cleaning up temp space')
            pass

def which_docker():
    return spawn.find_executable('docker')

def cmdrun_build(base_path, recreate=True):
    # To ensure version compatibility, we have to generate the kwargs ourselves
    client_kwargs = kwargs_from_env(assert_hostname=False)
    client = docker.AutoVersionClient(**client_kwargs)
    if recreate or not client.images(name='ansible-builder', quiet=True):
        logger.info('(Re)building the Harbormaster image is necessary.')
        build_output = build_buildcontainer_image(base_path)
        for line in build_output:
            logger.debug(line)
    harbormaster_img_id = client.images(name='ansible-builder', quiet=True)[0]
    logger.info('Harbormaster image has ID %s', harbormaster_img_id)
    temp_dir = tempfile.mkdtemp()
    logger.debug('Temp dir is %s', temp_dir)
    try:
        jinja_render_to_temp('build-docker-compose.j2.yml', temp_dir,
                             'docker-compose.yml',
                             hosts=extract_hosts_from_harbormaster_compose(base_path),
                             harbormaster_img_id=harbormaster_img_id,
                             which_docker=which_docker())
        # Docker-compose uses docopt, which outputs things like the below
        # So I'm starting with the defaults and then updating them.
        # One structure for the global options and one for the command specific
        options = {
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
            u'-h': False}
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
        command_options = {
            u'--abort-on-container-exit': False,
            u'--build': False,
            u'--force-recreate': False,
            u'--no-color': False,
            u'--no-deps': False,
            u'--no-recreate': False,
            u'--remove-orphans': False,
            u'--timeout': None,
            u'-d': False,
            u'SERVICE': []}
        command_options[u'--no-build'] = True
        os.environ['HARBORMASTER_BASE'] = os.path.realpath(base_path)
        project = project_from_options('.', options)
        command = TopLevelCommand(project)
        logger.info('Starting Compose engine to build your images...')
        command.up(command_options)
        # FIXME: You don't actually check to see if everything worked.
        # Cool - now export those containers as images
        # FIXME: support more-than-one-instance
        project_name = os.path.basename(base_path).lower()
        logger.debug('project_name is %s' % project_name)
        version = datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')
        logger.info('Exporting built containers as images...')
        for host in extract_hosts_from_harbormaster_compose(base_path):
            container_id, = client.containers(
                filters={'name': 'harbormaster_%s_1' % host},
                limit=1, all=True, quiet=True
            )
            exported = client.export(container_id)
            client.import_image_from_data(
                exported.read(),
                repository='%s-%s' % (project_name, host),
                tag=version)
            image_id, = client.images(
                '%s-%s:%s' % (project_name, host, version),
                quiet=True
            )
            logger.info('Exported %s-%s with image ID %s', project_name, host,
                        image_id)
            client.tag(image_id, '%s-%s' % (project_name, host), tag='latest',
                       force=True)
            logger.info('Cleaning up %s build container...', host)
            client.remove_container(container_id)
        container_id, = client.containers(
            quiet=True, filters={'name': 'harbormaster_harbormaster_1'},
            limit=1, all=True
        )
        logger.info('Cleaning up harbormaster build container...')
        client.remove_container(container_id)
    finally:
        try:
            shutil.rmtree(temp_dir)
        except Exception, e:
            logger.exception('Failure cleaning up temp space')
            pass

def cmdrun_run(base_path):
    temp_dir = tempfile.mkdtemp()
    logger.debug('Temp dir is %s', temp_dir)
    try:
        project_name = os.path.basename(base_path).lower()
        jinja_render_to_temp('run-docker-compose.j2.yml', temp_dir,
                             'docker-compose.yml',
                             hosts=extract_hosts_from_harbormaster_compose(base_path),
                             project_name=project_name)

        # Docker-compose uses docopt, which outputs things like the below
        # So I'm starting with the defaults and then updating them.
        # One structure for the global options and one for the command specific
        options = {
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
            u'-h': False}
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
            u'ARGS': ['--no-build'] + extract_hosts_from_harbormaster_compose(base_path)
        })
        command_options = {
            u'--abort-on-container-exit': False,
            u'--build': False,
            u'--force-recreate': False,
            u'--no-build': True,
            u'--no-color': False,
            u'--no-deps': False,
            u'--no-recreate': False,
            u'--remove-orphans': False,
            u'--timeout': None,
            u'-d': False,
            u'SERVICE': extract_hosts_from_harbormaster_compose(base_path)}
        command_options[u'--no-build'] = True
        os.environ['HARBORMASTER_BASE'] = os.path.realpath(base_path)
        project = project_from_options('.', options)
        command = TopLevelCommand(project)
        command.up(command_options)
    finally:
        try:
            shutil.rmtree(temp_dir)
        except Exception, e:
            logger.exception('Failure cleaning up temp space')
            pass


def commandline():
    parser = argparse.ArgumentParser(description=u'Build, orchestrate, run, and '
                                                 u'ship Docker containers with '
                                                 u'Ansible playbooks')
    parser.add_argument('subcommand', choices=AVAILABLE_COMMANDS,
                        help=u'Subcommand to run - options are: {}'.format(
                            AVAILABLE_COMMANDS))
    args = parser.parse_args()
    if args.subcommand == 'help':
        parser.print_help()
        sys.exit(0)
    globals()[u'cmdrun_{}'.format(args.subcommand)](os.getcwd())

