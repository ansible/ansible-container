# -*- coding: utf-8 -*-
from __future__ import absolute_import

from container.utils.visibility import getLogger
logger = getLogger(__name__)

from ruamel.yaml.comments import CommentedMap, CommentedSeq
from ..k8s.base_deploy import K8sBaseDeploy

"""
Translate the container.yml derived config into an Ansible playbook/role
to deploy the services.
"""


class Deploy(K8sBaseDeploy):

    def get_namespace_task(self, state='present'):
        task = CommentedMap()
        module_name = 'openshift_v1_project'
        task_name = 'Create project' if state == 'present' else 'Remove project'
        task['name'] = '{} {}'.format(task_name, self._namespace_name)
        task[module_name] = CommentedMap()
        task[module_name]['name'] = self._namespace_name
        if state == 'present':
            if self._namespace_display_name:
                task[module_name]['display_name'] = self._namespace_display_name
            if self._namespace_description:
                task[module_name]['description'] = self._namespace_description
        task[module_name]['state'] = state
        return task

    def get_deployment_tasks(self, module_name=None):
        return super(Deploy, self).get_deployment_tasks(module_name='openshift_v1_deployment_config')
