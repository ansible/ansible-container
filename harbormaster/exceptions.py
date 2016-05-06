# -*- coding: utf-8 -*-
from __future__ import absolute_import

import logging

logger = logging.getLogger(__name__)

class HarbormasterNotInitializedException(Exception):
    pass


class HarbormasterAlreadyInitializedException(Exception):
    pass

