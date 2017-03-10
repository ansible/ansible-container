# -*- coding: utf-8 -*-
from __future__ import absolute_import

import logging

logger = logging.getLogger(__name__)

import os
import json

from ruamel import yaml
import docker

if 'TO_AC' not in os.environ or 'DISTRO_DATA' not in os.environ:
    raise ImportError('TO_AC and DISTRO_DATA must be in the environment. You '
                      'probably want to run this via "python setup.py test"')

distro_vars = json.loads(os.environ['DISTRO_DATA'])

role_defaults = yaml.round_trip_load(
    open(os.path.join(os.environ['TO_AC'], 'roles', distro_vars['name'],
                      'defaults', 'main.yml'))
)

role_meta = yaml.round_trip_load(
    open(os.path.join(os.environ['TO_AC'], 'roles', distro_vars['name'],
                      'meta', 'container.yml'))
)

role_tasks = yaml.round_trip_load(
    open(os.path.join(os.environ['TO_AC'], 'roles', distro_vars['name'],
                      'tasks', 'main.yml'))
)

docker_client = docker.from_env()
built_image_name = u'%s-%s' % (os.environ['TO_AC'], distro_vars['name'])
built_image_info = docker_client.api.inspect_image(built_image_name)
base_image_info = docker_client.api.inspect_image(distro_vars['base_image'])


