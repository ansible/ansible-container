# -*- coding: utf-8 -*-

from __future__ import absolute_import

import logging

from .config import ShipItConfig
from .role import ShipItRole
from ..base_engine import BaseShipItEngine

logger = logging.getLogger(__name__)


class ShipItEngine(BaseShipItEngine):

    def run(self, **kwargs):
        config = kwargs.pop('config')
        project_name = kwargs.pop('project_name')
        project_dir = kwargs.pop('project_dir')
        create_templates = kwargs.pop('create_templates')

        role = ShipItRole(config=config, project_name=project_name, project_dir=project_dir, engine='openshift')
        role.create_role()
        role.create_playbook()

        if create_templates:
            config_obj = ShipItConfig(config=config, project_name=project_name, project_dir=project_dir)
            config_obj.create_config()



