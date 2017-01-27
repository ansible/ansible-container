# -*- coding: utf-8 -*-
from __future__ import absolute_import

import logging

logger = logging.getLogger(__name__)

import os
import sys
import importlib
import hashlib
import tempfile
import shutil
import yaml
import psutil

import delegator

def load_engine(self, engine_name, project_name, services):
    mod = importlib.import_module('%s.engine' % engine_name, package='.')
    return mod.Engine(project_name, services)

def resolve_role_to_path(role_name):
    # FIXME - How do I programatically resolve the role name into a path?
    pass


def get_role_fingerprint(role_name):
    # FIXME - How do I programatically resolve the role name into a path?
    pass

def get_metadata_from_role(role_name):
    role_path = resolve_role_to_path(role_name)
    metadata_file = os.path.join(role_path, 'meta', 'container.yml')
    if os.path.exists(metadata_file):
        with open(metadata_file) as ifs:
            metadata = yaml.safe_load(ifs)
            # TODO: Decide what we want this metadata file to look like now
        return metadata
    return {}

def get_conductor_name(project_name):
    return u'conductor_%s' % (project_name,)

def apply_role_to_container(role, container_id, service, engine):
    playbook = [
        {'hosts': service,
         'roles': [role]}
    ]

    container_metadata = engine.inspect_container(container_id)
    onbuild = container_metadata['Config']['OnBuild']
    # FIXME: Actually do stuff if onbuild is not null

    try:
        tmpdir = tempfile.mkdtemp()
        playbook_path = os.path.join(tmpdir, 'apply_%s.yml' % service)
        with open(playbook_path, 'w') as ofs:
            yaml.safe_dump(playbook, ofs)
        inventory_path = os.path.join(tmpdir, 'apply_%s_hosts' % service)
        with open(inventory_path, 'w') as ofs:
            ofs.write('%s\n' % service)

        ansible_args = dict(inventory=inventory_path,
                            playbook=playbook_path,
                            engine_args=engine.ansible_args)

        result = delegator.run('ansible-playbook '
                               '-i {inventory} '
                               '-c {conn_plugin} '
                               '{engine_args} '
                               '{playbook}'.format(ansible_args),
                               block=False)
        while psutil.pid_exists(result.pid):
            for line in iter(result.std_out.readline, ''):
                sys.stdout.write(line)

        if result.return_code:
            logger.error('Error applying role!')
            logger.error(result.err)
        return result.return_code
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

def build(engine_name, project_name, services, cache=True):
    engine = load_engine(engine_name, project_name, services)
    logger.info('%s integration engine loaded. Build starting.',
                engine.display_name())

    for name, service in services.iteritems():
        logger.info('Building service %s.', name)
        cur_image_id = engine.get_image_id_by_tag(service['from'])
        # the fingerprint hash tracks cacheability
        fingerprint_hash = hashlib.sha256('%s::' % cur_image_id)
        logger.debug('%s: Base fingerprint hash = %s', name,
                     fingerprint_hash.hexdigest())
        cache_busted = not cache

        if service['roles']:
            for role in service['roles']:
                role_fingerprint = get_role_fingerprint(role)
                fingerprint_hash.update(role_fingerprint)

                if not cache_busted:
                    logger.debug('%s: Still trying to keep cache.', name)
                    cached_image_id = engine.get_image_id_by_fingerprint(
                        fingerprint_hash.hexdigest())
                    if cached_image_id:
                        # We can reuse the cached image
                        logger.debug('%s: Cached layer found with fingerprint %s',
                                     name, fingerprint_hash.hexdigest())
                        cur_image_id = cached_image_id
                        logger.info('%s: Applied role %s (from cache)', name,
                                    role)
                        continue
                    else:
                        cache_busted = True
                        logger.debug('%s: Cache busted! No layer found for '
                                     'fingerprint %s', name,
                                     fingerprint_hash.hexdigest())

                container_id = engine.run_container(
                    image_id=cur_image_id,
                    service_name=name,
                    user='root',
                    working_dir='/',
                    command='sh -c "while true; do sleep 1; '
                            'done"',
                    entrypoint=[],
                    volumes_from=[get_conductor_name(project_name)])

                rc = apply_role_to_container(role, container_id, service, engine)
                if rc:
                    raise RuntimeError('Build failed.')
                logger.info('%s: Applied role %s', name, role)

                engine.stop_container(container_id)
                metadata = get_metadata_from_role(role)
                image_id = engine.commit_role_as_layer(container_id,
                                                       name,
                                                       fingerprint_hash.hexdigest(),
                                                       metadata)
                logger.info('%s: Committed layer as image ID %s', name, image_id)
                engine.delete_container(container_id)
                cur_image_id = image_id
            logger.info('%s: Build complete.', name)
        else:
            logger.info('%s: No roles specified. Nothing to do.', name)
    logger.info('All images successfully built.')

def run(engine_name, project_name, services):
    engine = load_engine(engine_name, project_name, services)
    logger.info('%s integration engine loaded. Preparing run.',
                engine.display_name())

    # Verify all images are built
    for service_name in services:
        logger.info('Verifying image for %s', service_name)
        image_id = engine.get_latest_image_id_for_service(service_name)
        if not image_id:
            logger.error('Missing image for %s. Run "ansible-container build" '
                         'to (re)create it.', service_name)
            raise RuntimeError('Run failed.')

    engine.orchestrate()

def restart(engine_name, project_name, services):
    engine = load_engine(engine_name, project_name, services)
    logger.info('%s integration engine loaded. Preparing to restart containers.',
                engine.display_name())
    engine.restart_all_containers()
    logger.info('All services restarted.')

def stop(engine_name, project_name, services):
    engine = load_engine(engine_name, project_name, services)
    logger.info('%s integration engine loaded. Preparing to stop all containers.',
                engine.display_name())
    for service_name in services:
        container_id = engine.get_container_id_for_service(service_name)
        if container_id:
            logger.debug('Stopping %s...', service_name)
            engine.stop_container(container_id)
    logger.info('All services stopped.')


