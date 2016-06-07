# -*- coding: utf-8 -*-
from __future__ import absolute_import

import logging

logger = logging.getLogger(__name__)


class BaseShipItEngine(object):

    def __init__(self, base_path):
        self.base_path = base_path

    def run(self, **kwargs):
        """
        Actually generate the Ansible role to deploy to this target.

        :param kwargs: The commandline options provided at runtime
        :return:
        """
        raise NotImplementedError()
