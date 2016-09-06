# -*- coding: utf-8 -*-

from __future__ import absolute_import

import logging

from . import FilterBase

logger = logging.getLogger(__name__)


def test_filter(*args, **kwargs):
    '''
    Not really a filter. Use to whether or not import method works.

    :param args:
    :param kwargs:
    :return:
    '''
    return 'success!'


class FilterModule(FilterBase):

    def filters(self):
        return {
            u'test_filter': test_filter
        }