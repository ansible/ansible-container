# -*- coding: utf-8 -*-
from __future__ import absolute_import

__version__ = '0.9.0-pre'

import os

# Many features of Ansible Container are flagged on whether or not we're running
# inside the Conductor container or not. This is the flag.
ENV = 'conductor' if os.environ.get('ANSIBLE_CONTAINER') else 'host'
