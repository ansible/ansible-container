# -*- coding: utf-8 -*-
from __future__ import absolute_import

import logging

logger = logging.getLogger(__name__)

"""Prebake and push all new conductor images."""

import subprocess

from container.docker.engine import PREBAKED_DISTROS
import container

version = container.__version__
subprocess.check_call(['python', 'setup.py', 'prebake'])
for distro in PREBAKED_DISTROS:
    print('Uploading %s...' % distro)
    distro_key = distro.replace(':', '-')
    print(['docker', 'tag',
           'container-conductor-%s:%s' % (distro_key, version),
           'ansible/container-conductor-%s:%s' % (distro_key, version)])
    subprocess.check_call(['docker', 'tag',
                           'container-conductor-%s:%s' % (distro_key, version),
                           'ansible/container-conductor-%s:%s' % (distro_key, version)])
    print(['docker', 'push',
           'ansible/container-conductor-%s:%s' % (distro_key, version)])
    subprocess.check_call(['docker', 'push',
                           'ansible/container-conductor-%s:%s' % (distro_key, version)])

