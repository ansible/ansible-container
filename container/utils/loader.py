# -*- coding: utf-8 -*-
from __future__ import absolute_import

import importlib

from .visibility import getLogger
logger = getLogger(__name__)

from ..conductor.engine import CAPABILITIES
from . import conductor_dir

def load_engine(capabilities_needed, engine_name, project_name, services=[], **kwargs):
    logger.debug(u"Loading engine capabilities", capabilities=capabilities_needed, engine=engine_name)
    mod = importlib.import_module('.%s.engine' % engine_name,
                                  package='container.conductor')
    engine_obj = mod.Engine(project_name, services, **kwargs)
    for capability in capabilities_needed:
        if not getattr(engine_obj, 'CAP_%s' % capability):
            raise ValueError(u'The engine for %s does not support %s',
                             engine_obj.display_name,
                             CAPABILITIES[capability])
    return engine_obj
