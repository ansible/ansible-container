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
        ifs = open(os.path.join(self.base_path, 'ansible/container.yml'))
        self._config = yaml_load(ifs)

    def __getitem__(self, item):
        return self._config.get(item)

    def __iter__(self):
        return iter(self._config)

    def __len__(self):
        return len(self._config)

