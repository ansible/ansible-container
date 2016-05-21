# -*- coding: utf-8 -*-

from __future__ import absolute_import

import json
import logging
import os

from ..base_config import BaseShipItConfig
from ..constants import SHIPIT_CONFIG_PATH
from .deployment import Deployment
from .route import Route
from .service import Service
from container.exceptions import AnsibleContainerShipItException

logger = logging.getLogger(__name__)


class ShipItConfig(BaseShipItConfig):

    def create_config(self):
        dest_path = os.path.join(self.project_dir, SHIPIT_CONFIG_PATH)
        try:
            os.makedirs(dest_path)
        except OSError:
            # ignore if path already exists
            pass
        except Exception as exc:
            raise AnsibleContainerShipItException("Error creating %s - %s" % (path, str(exc)))

        templates = Service(config=self.config, project_name=self.project_name).get_template()
        for template in templates:
            name = "%s-service.json" % template['metadata']['name']
            with open(os.path.join(dest_path, name), 'w') as f:
                f.write(json.dumps(template, indent=4))

        templates = Route(config=self.config, project_name=self.project_name).get_template()
        for template in templates:
            name = "%s.json" % template['metadata']['name']
            with open(os.path.join(dest_path, name), 'w') as f:
                f.write(json.dumps(template, indent=4))

        templates = Deployment(config=self.config, project_name=self.project_name).get_template()
        for template in templates:
            name = "%s-deployment.json" % template['metadata']['name']
            with open(os.path.join(dest_path, name), 'w') as f:
                f.write(json.dumps(template, indent=4))




