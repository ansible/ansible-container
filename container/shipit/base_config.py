# -*- coding: utf-8 -*-

from __future__ import absolute_import

import logging

logger = logging.getLogger(__name__)


class BaseShipItConfig(object):

    def __init__(self, config=None, project_name=None, project_dir=None):
        self.config = config
        self.project_name = project_name
        self.project_dir = project_dir

    def create_config(self):
        '''
        Write cloud configuration files

        :return: None
        '''

        raise NotImplementedError()