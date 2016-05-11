# -*- coding: utf-8 -*-

from __future__ import absolute_import

import logging
import os
import yaml

from .constants import SHIPIT_PATH, SHIPIT_PLAYBOOK_NAME
from .k8s_service import K8SService
from .k8s_deployment import K8SDeployment
from .exceptions import ShipItException
from collections import OrderedDict


logger = logging.getLogger(__name__)


def represent_odict(dump, tag, mapping, flow_style=None):
    '''
    https://gist.github.com/miracle2k/3184458
    Like BaseRepresenter.represent_mapping, but does not issue the sort().
    '''
    value = []
    node = yaml.MappingNode(tag, value, flow_style=flow_style)
    if dump.alias_key is not None:
        dump.represented_objects[dump.alias_key] = node
    best_style = True
    if hasattr(mapping, 'items'):
        mapping = mapping.items()
    for item_key, item_value in mapping:
        node_key = dump.represent_data(item_key)
        node_value = dump.represent_data(item_value)
        if not (isinstance(node_key, yaml.ScalarNode) and not node_key.style):
            best_style = False
        if not (isinstance(node_value, yaml.ScalarNode) and not node_value.style):
            best_style = False
        value.append((node_key, node_value))
    if flow_style is None:
        if dump.default_flow_style is not None:
            node.flow_style = dump.default_flow_style
        else:
            node.flow_style = best_style
    return node


class K8SPlaybook(object):

    def __init__(self, config=None, project_name=None, project_dir=None):
        self.config = config
        self.project_name = project_name
        self.project_dir = project_dir

    def get_tasks(self):
        tasks = []
        services = K8SService(config=self.config, project_name=self.project_name).get_task()
        tasks += services

        deployments = K8SDeployment(config=self.config, project_name=self.project_name).get_task()
        tasks += deployments

        return tasks

    def build_vars(self):
        pass

    def write_deployment(self, hosts="localhost", connection="local", gather_facts=False):
        '''
        Create SHIPIT_PATH within the project dir, and within that add a deployment playbook, roles path
        and a <project_name> role.

        :param hosts: Inventory hosts
        :type hosts: str
        :param connection: Connection type
        :type hosts: str
        :param gather_facts: Control whether or not plays execute setup module.
        :type gather_facts: bool
        :return: None
        '''

        deploy_path = os.path.join(self.project_dir, SHIPIT_PATH)
        role_path = os.path.join(self.project_dir, 'roles', self.project_name)
        tasks_path = os.path.join(role_path, 'tasks')
        vars_path = os.path.join(role_path, 'vars')

        self.create_path(tasks_path)
        self.create_path(vars_path)

        yaml.SafeDumper.add_representer(OrderedDict,
                                        lambda dumper, value: represent_odict(dumper, u'tag:yaml.org,2002:map', value))

        # Create tasks/main.yml
        tasks_playbook = self.get_tasks()
        with open(os.path.join(tasks_path, 'main.yml'), 'w') as f:
            f.write(yaml.safe_dump(tasks_playbook, default_flow_style=False))

        # Create the playbook
        plays = [OrderedDict()]
        plays[0]['name'] = "Deploy %s" % self.project_name
        plays[0]['hosts'] = hosts

        if connection:
            plays[0]['connection'] = connection
        if not gather_facts:
            plays[0]['gather_facts'] = 'no'

        plays[0]['roles'] = [dict(
            role=self.project_name
        )]

        with open(os.path.join(deploy_path, SHIPIT_PLAYBOOK_NAME), 'w') as f:
            f.write(yaml.safe_dump(plays, default_flow_style=False))

    @staticmethod
    def create_path(path):
        try:
            os.makedirs(path)
        except OSError:
            # ignore if path already exists
            pass
        except Exception as exc:
            raise ShipItException("Error creating %s - %s" % (path, str(exc)))





