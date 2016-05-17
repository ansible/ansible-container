# -*- coding: utf-8 -*-
from __future__ import absolute_import

import logging

logger = logging.getLogger(__name__)

import os
import tarfile
import datetime
import getpass
import json

import docker
from docker.utils import kwargs_from_env

from .exceptions import (HarbormasterNotInitializedException,
                         HarbormasterAlreadyInitializedException,
                         HarbormasterNoAuthenticationProvided)
from .utils import (extract_hosts_from_harbormaster_compose,
                    jinja_render_to_temp,
                    launch_docker_compose,
                    make_temp_dir,
                    jinja_template_path,
                    which_docker,
                    extract_hosts_touched_by_playbook,
                    get_current_logged_in_user,
                    assert_initialized)


def cmdrun_init(base_path, **kwargs):
    harbormaster_dir = os.path.normpath(
        os.path.join(base_path, 'harbormaster'))
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
    assert_initialized(base_path)
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


def cmdrun_build(base_path, recreate=True, **kwargs):
    assert_initialized(base_path)
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
        logger.info('Starting Compose engine to build your images...')
        touched_hosts = extract_hosts_touched_by_playbook(base_path,
                                                          harbormaster_img_id)
        launch_docker_compose(base_path, temp_dir, 'build',
                              which_docker=which_docker(),
                              harbormaster_img_id=harbormaster_img_id)
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
        for host in touched_hosts:
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
        for host in set(extract_hosts_from_harbormaster_compose(base_path)) - set(touched_hosts):
            logger.info('Cleaning up %s build container...', host)
            container_id, = client.containers(
                filters={'name': 'harbormaster_%s_1' % host},
                limit=1, all=True, quiet=True
            )
            client.remove_container(container_id)
        logger.info('Cleaning up harbormaster build container...')
        client.remove_container(harbormaster_container_id)

def cmdrun_run(base_path, **kwargs):
    assert_initialized(base_path)
    with make_temp_dir() as temp_dir:
        project_name = os.path.basename(base_path).lower()
        launch_docker_compose(base_path, temp_dir, 'run',
                              services=extract_hosts_from_harbormaster_compose(base_path),
                              project_name=project_name)

DEFAULT_DOCKER_REGISTRY_URL = 'https://index.docker.io/v1/'

def cmdrun_push(base_path, username=None, password=None, url=None, **kwargs):
    assert_initialized(base_path)
    # To ensure version compatibility, we have to generate the kwargs ourselves
    client_kwargs = kwargs_from_env(assert_hostname=False)
    client = docker.AutoVersionClient(**client_kwargs)
    if not url:
        url = DEFAULT_DOCKER_REGISTRY_URL
    if username:
        # We assume if no username was given, the docker config file suffices
        while not password:
            password = getpass.getpass(u'Enter password for %s at %s: ' % (
                username, url
            ))
        client.login(username, password, registry=url)
    username = get_current_logged_in_user(url)
    if not username:
        raise HarbormasterNoAuthenticationProvided(u'Please provide login '
                                                   u'credentials for this registry.')
    logger.info('Pushing to repository for user %s', username)
    harbormaster_img_id = client.images(name='ansible-builder', quiet=True)[0]
    project_name = os.path.basename(base_path).lower()
    for host in extract_hosts_touched_by_playbook(base_path,
                                                  harbormaster_img_id):
        image_data = client.images(
            '%s-%s' % (project_name, host,)
        )
        latest_image_data, = [datum for datum in image_data
                              if '%s-%s:latest' % (project_name, host,) in
                              datum['RepoTags']]
        image_buildstamp = [tag for tag in latest_image_data['RepoTags']
                            if not tag.endswith(':latest')][0].split(':')[-1]
        client.tag(latest_image_data['Id'],
                   '%s/%s-%s' % (username, project_name, host),
                   tag=image_buildstamp)
        logger.info('Pushing %s-%s:%s...', project_name, host, image_buildstamp)
        status = client.push('%s/%s-%s' % (username, project_name, host),
                             tag=image_buildstamp,
                             stream=True)
        last_status = None
        for line in status:
            line = json.loads(line)
            if type(line) is dict and 'error' in line:
                logger.error(line['error'])
            elif type(line) is dict and 'status' in line:
                if line['status'] != last_status:
                    logger.info(line['status'])
                last_status = line['status']
            else:
                logger.debug(line)
    logger.info('Done!')



