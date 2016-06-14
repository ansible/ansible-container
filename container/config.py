# -*- coding: utf-8 -*-
from __future__ import absolute_import

import logging

logger = logging.getLogger(__name__)

import os
from collections import Mapping

from yaml import load as yaml_load

# TODO: Actually do some schema validation

class AnsibleContainerConfig(Mapping):
    _config = {}
    base_path = None

    def __init__(self, base_path):
        self.base_path = base_path
        self.set_env('prod')

    def set_env(self, env):
        assert env in ['dev', 'prod']
        ifs = open(os.path.join(self.base_path, 'ansible/container.yml'))
        config = yaml_load(ifs)
        ifs.close()
        for service, service_config in config['services'].items():
            dev_overrides = service_config.pop('dev_overrides', {})
            if env == 'dev':
                service_config.update(dev_overrides)
        self._config = config

    def __getitem__(self, item):
        return self._config.get(item)

    def __iter__(self):
        return iter(self._config)

    def __len__(self):
        return len(self._config)

