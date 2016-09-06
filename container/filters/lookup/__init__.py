# -*- coding: utf-8 -*-

from __future__ import absolute_import

import logging

logger = logging.getLogger(__name__)


class LookupBase(object):

    def run(self, terms, variables, **kwargs):
        raise NotImplementedError()
        return []

