# -*- coding: utf-8 -*-

from __future__ import absolute_import

import logging

from .k8s_playbook import K8SPlaybook

logger = logging.getLogger(__name__)


def run_shipit(type=None, config=None, project_name=None, project_dir=None, hosts="localhost", connection="local",
               gather_facts=False):

    #TODO - for now assuming we just want k8s which is really OS. Maybe at somepoint we'll want the
    #       the option to deploy to other things...
    playbook = K8SPlaybook(config=config, project_name=project_name, project_dir=project_dir)
    playbook.write_deployment(hosts=hosts, connection=connection, gather_facts=gather_facts)

