# -*- coding: utf-8 -*-
from __future__ import absolute_import

import logging

logger = logging.getLogger(__name__)


class BaseShipItEngine(object):

    def __init__(self, base_path):
        self.base_path = base_path

    def add_options(self, subparser):
        """
        Given an argument subparser, add to it the arguments and options
        this engine allows.

        https://docs.python.org/2/library/argparse.html#sub-commands

        :param subparser: An argparse.ArgumentSubparser
        :return: None
        """
        raise NotImplementedError()

    def run(self, **kwargs):
        """
        Actually generate the Ansible role to deploy to this target.

        :param kwargs: The commandline options provided at runtime
        :return:
        """
        raise NotImplementedError()
