# -*- coding: utf-8 -*-
from __future__ import absolute_import

import logging

logger = logging.getLogger(__name__)

import os
import tarfile
import datetime

import docker
from docker.utils import kwargs_from_env
from compose.cli.command import project_from_options
from compose.cli.main import TopLevelCommand

from .exceptions import (HarbormasterNotInitializedException,
                         HarbormasterAlreadyInitializedException)
from .utils import (extract_hosts_from_harbormaster_compose,
                    jinja_render_to_temp,
                    which_docker,
                    make_temp_dir,
                    compose_format_version,
                    jinja_template_path)


def cmdrun_init(base_path):
    harbormaster_dir = os.path.normpath(
        os.path.join(os.path.curdir, 'harbormaster'))
    if os.path.exists(harbormaster_dir):
        raise HarbormasterAlreadyInitializedException()
    os.mkdir('harbormaster')
    template_dir = os.path.join(jinja_template_path(), 'harbormaster')
    for tmpl_filename in os.listdir(template_dir):
        jinja_render_to_temp('harbormaster/%s' % tmpl_filename,
                             harbormaster_dir,
                             tmpl_filename.replace('.j2', ''))
    logger.info('Harbormaster initialized.')

def build_buildcontainer_image(base_path):
    # To ensure version compatibility, we have to generate the kwargs ourselves
    client_kwargs = kwargs_from_env(assert_hostname=False)
    client = docker.AutoVersionClient(**client_kwargs)
    with make_temp_dir() as temp_dir:
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
    with make_temp_dir() as temp_dir:
        version = compose_format_version(base_path)
        jinja_render_to_temp('build-docker-compose.j2.yml' if version == 2
                             else 'build-docker-compose-v1.j2.yml',
                             temp_dir,
                             'docker-compose.yml',
                             hosts=extract_hosts_from_harbormaster_compose(base_path),
                             harbormaster_img_id=harbormaster_img_id,
                             which_docker=which_docker())
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
        logger.info('Starting Compose engine to build your images...')
        command.up(command_options)
        build_container_info, = client.containers(
            filters={'name': 'harbormaster_harbormaster_1'},
            limit=1, all=True
        )
        harbormaster_container_id = build_container_info['Id']
        # Not the best way to test for success or failure, but it works.
        exit_status = build_container_info['Status']
        if '(0)' not in exit_status:
            logger.error('Ansible playbook run failed.')
            logger.info('Cleaning up harbormaster build container...')
            client.remove_container(harbormaster_container_id)
            return
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
        logger.info('Cleaning up harbormaster build container...')
        client.remove_container(harbormaster_container_id)

def cmdrun_run(base_path):
    with make_temp_dir() as temp_dir:
        project_name = os.path.basename(base_path).lower()
        version = compose_format_version(base_path)
        jinja_render_to_temp('run-docker-compose.j2.yml' if version == 2
                             else 'run-docker-compose-v1.j2.yml',
                             temp_dir,
                             'docker-compose.yml',
                             hosts=extract_hosts_from_harbormaster_compose(base_path),
                             project_name=project_name)
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
            u'ARGS': ['--no-build'] + extract_hosts_from_harbormaster_compose(base_path)
        })
        command_options = DEFAULT_COMPOSE_UP_OPTIONS.copy()
        command_options.update({
            u'SERVICE': extract_hosts_from_harbormaster_compose(base_path),
            u'--no-build': True})
        os.environ['HARBORMASTER_BASE'] = os.path.realpath(base_path)
        project = project_from_options('.', options)
        command = TopLevelCommand(project)
        command.up(command_options)
