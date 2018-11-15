# -*- coding: utf-8 -*-
from __future__ import absolute_import

import logging

logger = logging.getLogger(__name__)

"""Prebake and push all new conductor images."""

import os
import subprocess

from container.docker.engine import PREBAKED_DISTROS
import container

version = container.__version__

BASE_DISTRO = os.getenv('BASE_DISTRO')
CONDUCTOR_PROVIDER = os.getenv('CONDUCTOR_PROVIDER') or 'ansible'

if BASE_DISTRO:
    print "building selected prebake distros %s for organization %s" % (BASE_DISTRO, CONDUCTOR_PROVIDER)
    subprocess.check_call(['python', 'setup.py', 'prebake', '--distros', BASE_DISTRO, '--conductor-provider', CONDUCTOR_PROVIDER])
else:
    print "building prebake distros for organization %s" % (CONDUCTOR_PROVIDER)
    subprocess.check_call(['python', 'setup.py', 'prebake', '--conductor-provider', CONDUCTOR_PROVIDER])

for distro in ([BASE_DISTRO] if BASE_DISTRO else PREBAKED_DISTROS):
    print('Uploading %s...' % distro)
    distro_key = distro.replace(':', '-')
    print(['docker', 'tag',
           'container-conductor-%s:%s' % (distro_key, version),
           'ansible/container-conductor-%s:%s' % (distro_key, version)])
    subprocess.check_call(['docker', 'tag',
                           'container-conductor-%s:%s' % (distro_key, version),
                           '%s/container-conductor-%s:%s' % (CONDUCTOR_PROVIDER, distro_key, version)])
    print(['docker', 'push',
           '%s/container-conductor-%s:%s' % (CONDUCTOR_PROVIDER, distro_key, version)])
    subprocess.check_call(['docker', 'push',
                           '%s/container-conductor-%s:%s' % (CONDUCTOR_PROVIDER, distro_key, version)])

