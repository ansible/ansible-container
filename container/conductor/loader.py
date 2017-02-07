# -*- coding: utf-8 -*-
from __future__ import absolute_import

import logging

logger = logging.getLogger(__name__)

import importlib

def load_engine(engine_name, project_name, services=[], **kwargs):
    conductor_module_name = __name__.rsplit('.', 1)[0]
    mod = importlib.import_module('.%s.engine' % engine_name,
                                  package=conductor_module_name)
    return mod.Engine(project_name, services, **kwargs)
