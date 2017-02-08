# -*- coding: utf-8 -*-
from __future__ import absolute_import

import logging

logger = logging.getLogger(__name__)

import os
import sys
import hashlib
import tempfile
import shutil
import yaml
import psutil

import delegator
from ansible.playbook.role.include import RoleInclude
from ansible.vars import VariableManager
from ansible.parsing.dataloader import DataLoader

from .loader import load_engine


def resolve_role_to_path(role_name):
    loader, variable_manager = DataLoader(), VariableManager()
    logger.debug('Loader is %s', loader)
    role_obj = RoleInclude.load(data=role_name, play=None,
                                variable_manager=variable_manager,
                                loader=loader)
    role_path = role_obj._role_path
    return role_path

def get_role_fingerprint(role_name):

    def hash_file(hash_obj, file_path):
        blocksize = 64 * 1024
        with open(file_path, 'rb') as ifs:
            while True:
                data = ifs.read(blocksize)
                if not data:
                    break
                hash_obj.update(data)
                hash_obj.update('::')

    def hash_dir(hash_obj, dir_path):
        for root, dirs, files in os.walk(dir_path, topdown=True):
            for file_path in files:
                abs_file_path = os.path.join(root, file_path)
                hash_obj.update(abs_file_path)
                hash_obj.update('::')
                hash_file(hash_obj, abs_file_path)

    def hash_role(hash_obj, role_path):
        # A role is easy to hash - the hash of the role content with the
        # hash of any role dependencies it has
        hash_dir(hash_obj, role_path)
        for dependency in get_dependencies_for_role(role_path):
            if dependency:
                dependency_path = resolve_role_to_path(dependency)
                hash_role(hash_obj, dependency_path)

    def get_dependencies_for_role(role_path):
        meta_main_path = os.path.join(role_path, 'meta', 'main.yml')
        meta_main = yaml.safe_load(open(meta_main_path))
        for dependency in meta_main.get('dependencies', []):
            yield dependency.get('role', None)

    hash_obj = hashlib.sha256()
    hash_role(hash_obj, resolve_role_to_path(role_name))
    return hash_obj.hexdigest()


def get_metadata_from_role(role_name):
    role_path = resolve_role_to_path(role_name)
    metadata_file = os.path.join(role_path, 'meta', 'container.yml')
    if os.path.exists(metadata_file):
        with open(metadata_file) as ifs:
            metadata = yaml.safe_load(ifs)
            # TODO: Decide what we want this metadata file to look like now
        return metadata
    return {}

def run_playbook(playbook, engine, services):
    try:
        tmpdir = tempfile.mkdtemp()
        playbook_path = os.path.join(tmpdir, 'playbook.yml')
        with open(playbook_path, 'w') as ofs:
            yaml.safe_dump(playbook, ofs)
        inventory_path = os.path.join(tmpdir, 'hosts')
        with open(inventory_path, 'w') as ofs:
            for service in services:
                ofs.write('%s\n' % service)

        ansible_args = dict(inventory=inventory_path,
                            playbook=playbook_path,
                            engine_args=engine.ansible_args,
                            ansible_playbook=engine.ansible_exec_path)

        result = delegator.run('{ansible_playbook} '
                               '-i {inventory} '
                               '{engine_args} '
                               '{playbook}'.format(**ansible_args),
                               block=False)
        while psutil.pid_exists(result.pid):
            for line in iter(result.std_out.readline, ''):
                sys.stdout.write(line)

        return result.return_code, result.err
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def apply_role_to_container(role, container_id, service, engine):
    playbook = [
        {'hosts': service,
         'roles': [role]}
    ]

    container_metadata = engine.inspect_container(container_id)
    onbuild = container_metadata['Config']['OnBuild']
    # FIXME: Actually do stuff if onbuild is not null

    rc, stderr = run_playbook(playbook, engine, [service])
    if rc:
        logger.error('Error applying role!')
        logger.error(stderr)
    return rc

def build(engine_name, project_name, services, cache=True, **kwargs):
    engine = load_engine(engine_name, project_name, services)
    logger.info(u'%s integration engine loaded. Build starting.',
                engine.display_name)

    for name, service in services.iteritems():
        logger.info(u'Building service %s.', name)
        cur_image_id = engine.get_image_id_by_tag(service['from'])
        # the fingerprint hash tracks cacheability
        fingerprint_hash = hashlib.sha256('%s::' % cur_image_id)
        logger.debug(u'%s: Base fingerprint hash = %s', name,
                     fingerprint_hash.hexdigest())
        cache_busted = not cache

        if service['roles']:
            for role in service['roles']:
                role_fingerprint = get_role_fingerprint(role)
                fingerprint_hash.update(role_fingerprint)

                if not cache_busted:
                    logger.debug(u'%s: Still trying to keep cache.', name)
                    cached_image_id = engine.get_image_id_by_fingerprint(
                        fingerprint_hash.hexdigest())
                    if cached_image_id:
                        # We can reuse the cached image
                        logger.debug(u'%s: Cached layer found with fingerprint %s',
                                     name, fingerprint_hash.hexdigest())
                        cur_image_id = cached_image_id
                        logger.info(u'%s: Applied role %s (from cache)', name,
                                    role)
                        continue
                    else:
                        cache_busted = True
                        logger.debug(u'%s: Cache busted! No layer found for '
                                     u'fingerprint %s', name,
                                     fingerprint_hash.hexdigest())

                container_obj = engine.run_container(
                    image_id=cur_image_id,
                    service_name=name,
                    user='root',
                    working_dir='/',
                    command='sh -c "while true; do sleep 1; '
                            'done"',
                    entrypoint=[],
                    volumes_from=[engine.container_name_for_service('conductor')],
                    detach=True)
                container_id = container_obj.id

                logger.debug('Container running as: %s', container_id)

                rc = apply_role_to_container(role, container_id, service, engine)
                if rc:
                    raise RuntimeError('Build failed.')
                logger.info(u'%s: Applied role %s', name, role)

                engine.stop_container(container_id)
                metadata = get_metadata_from_role(role)
                image_id = engine.commit_role_as_layer(container_id,
                                                       name,
                                                       fingerprint_hash.hexdigest(),
                                                       metadata)
                logger.info(u'%s: Committed layer as image ID %s', name, image_id)
                engine.delete_container(container_id)
                cur_image_id = image_id
            logger.info(u'%s: Build complete.', name)
        else:
            logger.info(u'%s: No roles specified. Nothing to do.', name)
    logger.info(u'All images successfully built.')

def run(engine_name, project_name, services, **kwargs):
    engine = load_engine(engine_name, project_name, services)
    logger.info(u'%s integration engine loaded. Preparing run.',
                engine.display_name())

    # Verify all images are built
    for service_name in services:
        logger.info(u'Verifying image for %s', service_name)
        image_id = engine.get_latest_image_id_for_service(service_name)
        if not image_id:
            logger.error(u'Missing image for %s. Run "ansible-container build" '
                         u'to (re)create it.', service_name)
            raise RuntimeError('Run failed.')

    playbook = engine.generate_orchestration_playbook()
    run_playbook(playbook, engine, services)

def restart(engine_name, project_name, services, **kwargs):
    engine = load_engine(engine_name, project_name, services)
    logger.info(u'%s integration engine loaded. Preparing to restart containers.',
                engine.display_name())
    engine.restart_all_containers()
    logger.info(u'All services restarted.')

def stop(engine_name, project_name, services, **kwargs):
    engine = load_engine(engine_name, project_name, services)
    logger.info(u'%s integration engine loaded. Preparing to stop all containers.',
                engine.display_name())
    for service_name in services:
        container_id = engine.get_container_id_for_service(service_name)
        if container_id:
            logger.debug(u'Stopping %s...', service_name)
            engine.stop_container(container_id)
    logger.info(u'All services stopped.')

def deploy(engine_name, project_name, services, repository_data, playbook_dest, **kwargs):
    engine = load_engine(engine_name, project_name, services)
    logger.info(u'%s integration engine loaded. Preparing deploy.',
                engine.display_name())

    # Verify all images are built
    for service_name in services:
        logger.info(u'Verifying image for %s', service_name)
        image_id = engine.get_latest_image_id_for_service(service_name)
        if not image_id:
            logger.error(u'Missing image for %s. Run "ansible-container build" '
                         u'to (re)create it.', service_name)
            raise RuntimeError(u'Run failed.')

    for service_name in services:
        logger.info(u'Pushing %s to %s...', service_name, repository_data['name'])
        image_id = engine.get_latest_image_id_for_service(service_name)
        engine.push_image(image_id, service_name, repository_data)

    logger.info(u'All images pushed.')

    playbook = engine.generate_orchestration_playbook(repository=repository_data)

    try:
        with open(os.path.join(playbook_dest, '%s.yml' % project_name), 'w') as ofs:
            yaml.safe_dump(playbook, ofs)
    except OSError, e:
        logger.error(u'Failure writing deployment playbook: %s', e)
        raise

def install(engine_name, project_name, services, role, **kwargs):
    # FIXME: Port me from ac_galaxy.py
    pass

