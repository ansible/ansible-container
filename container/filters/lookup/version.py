# -*- coding: utf-8 -*-

from __future__ import absolute_import

import logging

logger = logging.getLogger(__name__)

from . import LookupBase
from container import __version__

class LookupModule(LookupBase):

    def run(self, terms, variables, **kwargs):
        '''
        Return the Ansible Container version. Probably not very useful. Use to
        test that local filters are working.

        :param terms:
        :param variables:
        :param kwargs:
        :return: list
        '''
        return [__version__]