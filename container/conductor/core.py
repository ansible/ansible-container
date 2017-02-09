# -*- coding: utf-8 -*-
from __future__ import absolute_import

import logging

logger = logging.getLogger(__name__)

import os
import time
import hashlib
import tempfile
import shutil
import subprocess
import threading

import yaml
from ansible.playbook.role.include import RoleInclude
from ansible.vars import VariableManager
from ansible.parsing.dataloader import DataLoader

from .loader import load_engine


def resolve_role_to_path(role_name):
    loader, variable_manager = DataLoader(), VariableManager()
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

def run_playbook(playbook, engine, service_map, ansible_options='',
                 debug=False):
    try:
        tmpdir = tempfile.mkdtemp()
        playbook_path = os.path.join(tmpdir, 'playbook.yml')
        with open(playbook_path, 'w') as ofs:
            yaml.safe_dump(playbook, ofs)
        inventory_path = os.path.join(tmpdir, 'hosts')
        with open(inventory_path, 'w') as ofs:
            for service_name, container_id in service_map.iteritems():
                ofs.write('%s ansible_host=%s\n' % (
                    service_name, container_id))

        ansible_args = dict(inventory=inventory_path,
                            playbook=playbook_path,
                            debug_maybe='-vvv' if debug else '',
                            engine_args=engine.ansible_args,
                            ansible_playbook=engine.ansible_exec_path,
                            ansible_options=ansible_options)

        ansible_cmd = ('{ansible_playbook} '
                       '{debug_maybe} '
                       '{ansible_options} '
                       '-i {inventory} '
                       '{engine_args} '
                       '{playbook}').format(**ansible_args)
        logger.debug('Running Ansible Playbook: %s', ansible_cmd)
        process = subprocess.Popen(ansible_cmd,
                                   shell=True,
                                   bufsize=1,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)

        log_iter = iter(process.stdout.readline, '')
        while process.returncode is None:
            try:
                logger.info(log_iter.next().rstrip())
            except StopIteration:
                break
            finally:
                process.poll()

        return process.returncode
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def apply_role_to_container(role, container_id, service_name, engine,
                            ansible_options='', debug=False):
    playbook = [
        {'hosts': service_name,
         'roles': [role]}
    ]

    container_metadata = engine.inspect_container(container_id)
    onbuild = container_metadata['Config']['OnBuild']
    # FIXME: Actually do stuff if onbuild is not null

    rc = run_playbook(playbook, engine, {service_name: container_id},
                      ansible_options, debug)
    if rc:
        logger.error('Error applying role!')
    return rc

def build(engine_name, project_name, services, cache=True, **kwargs):
    engine = load_engine(engine_name, project_name, services)
    logger.info(u'%s integration engine loaded. Build starting.',
                engine.display_name)

    for service_name, service in services.iteritems():
        logger.info(u'Building service %s.', service_name)
        cur_image_id = engine.get_image_id_by_tag(service['from'])
        # the fingerprint hash tracks cacheability
        fingerprint_hash = hashlib.sha256('%s::' % cur_image_id)
        logger.debug(u'%s: Base fingerprint hash = %s', service_name,
                     fingerprint_hash.hexdigest())
        cache_busted = not cache

        cur_container_id = engine.get_container_id_for_service(service_name)
        if cur_container_id:
            if engine.service_is_running(service_name):
                engine.stop_container(cur_container_id, forcefully=True)
            engine.delete_container(cur_container_id)

        if service['roles']:
            for role in service['roles']:
                role_fingerprint = get_role_fingerprint(role)
                fingerprint_hash.update(role_fingerprint)

                if not cache_busted:
                    logger.debug(u'%s: Still trying to keep cache.', service_name)
                    cached_image_id = engine.get_image_id_by_fingerprint(
                        fingerprint_hash.hexdigest())
                    if cached_image_id:
                        # We can reuse the cached image
                        logger.debug(u'%s: Cached layer found with fingerprint %s',
                                     service_name, fingerprint_hash.hexdigest())
                        cur_image_id = cached_image_id
                        logger.info(u'%s: Applied role %s (from cache)', service_name,
                                    role)
                        continue
                    else:
                        cache_busted = True
                        logger.debug(u'%s: Cache busted! No layer found for '
                                     u'fingerprint %s', service_name,
                                     fingerprint_hash.hexdigest())

                target_thread = threading.Thread(
                    target=engine.run_container,
                    kwargs=dict(image_id=cur_image_id,
                                name=engine.container_name_for_service(service_name),
                                service_name=service_name,
                                user='root',
                                working_dir='/',
                                command='sh -c "while true; do sleep 1; '
                                        'done"',
                                entrypoint=[],
                                volumes_from=[engine.container_name_for_service('conductor')]))
                target_thread.daemon = True
                target_thread.start()
                container_id = None
                while container_id is None:
                    time.sleep(0.1)
                    container_id = engine.get_container_id_for_service(service_name)
                logger.debug('Container running as: %s', container_id)

                rc = apply_role_to_container(role, container_id, service_name,
                                             engine,
                                             ansible_options=kwargs['ansible_options'],
                                             debug=kwargs['debug'])
                if rc:
                    raise RuntimeError('Build failed.')
                logger.info(u'%s: Applied role %s', service_name, role)

                engine.stop_container(container_id, forcefully=True)
                target_thread.join()
                metadata = get_metadata_from_role(role)
                image_id = engine.commit_role_as_layer(container_id,
                                                       service_name,
                                                       fingerprint_hash.hexdigest(),
                                                       metadata)
                logger.info(u'%s: Committed layer as image ID %s', service_name, image_id)
                engine.delete_container(container_id)
                cur_image_id = image_id
            logger.info(u'%s: Build complete.', service_name)
        else:
            logger.info(u'%s: No roles specified. Nothing to do.', service_name)
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
    rc = run_playbook(playbook, engine, services)

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

