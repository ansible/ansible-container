#!/usr/bin/python
#
# Copyright 2016 Red Hat | Ansible
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.


DOCUMENTATION = '''

module: k8s_service

short_description: Create or remove a service on a Kubernetes or OpenShift cluster.

description:
  - Create or remove a service on a Kubernetes or OpenShift cluster by setting the C(state) to I(present) or I(absent).
  - The module is idempotent and will not replace an existing service unless the C(reload) option is passed. 
  - Supports check mode. Use check mode to view a list of actions the module will take.

options:

'''

EXAMPLES = '''
'''

RETURN = '''
'''
import logging
import logging.config

from ansible.module_utils.basic import *
from .k8s_api import K8sApi

K8_TEMPLATE_DIR = 'k8s_templates'


logger = logging.getLogger('k8s_service')

logging.config.dictConfig(
    {
        'version': 1,
        'disable_existing_loggers': True,
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
            },
            'file': {
                'level': 'DEBUG',
                'class': 'logging.FileHandler',
                'filename': 'ansible-container.log'
            }
        },
        'loggers': {
            'k8s_service': {
                'handlers': ['file'],
                'level': 'DEBUG',
            },
            'container': {
                'handlers': ['file'],
                'level': 'DEBUG',
            },
            'compose': {
                'handlers': [],
                'level': 'INFO'
            },
            'docker': {
                'handlers': [],
                'level': 'INFO'
            }
        },
    }
)

class K8sServiceManager(AnsibleModule):

    def __init__(self):

        self.arg_spec = dict(
            project_name=dict(type='str', aliases=['namespace']),
            state=dict(type='str', choices=['present', 'absent'], default='present'),
            labels=dict(type='dict'),
            ports=dict(type='list'),
            service_name=dict(type='str'),
            loadbalancer=dict(type='bool', default=False),
            replace=dict(type='bool', default=False),
            selector=dict(type='dict'),
            cli=dict(type='str', choices=['kubectl', 'oc'], default='oc')
        )

        super(K8sServiceManager, self).__init__(self.arg_spec,
                                                supports_check_mode=True)

        self.project_name = None
        self.state = None
        self.labels = None
        self.ports = None
        self.service_name = None
        self.loabalancer = None
        self.selector = None
        self.replace = None
        self.cli = None
        self.api = None

    def exec_module(self):

        for key in self.arg_spec:
            setattr(self, key, self.params.get(key))

        self.api = K8sApi(target=self.cli)

        actions = []
        changed = False
        services = dict()
        results = dict()

        project_switch = self.api.set_project(self.project_name)
        if not project_switch:
            actions.append("Create project %s" % self.project_name)
            self.api.create_project(self.project_name)

        if self.state == 'present':
            service = self.api.get_resource('service', self.service_name)
            if not service:
                template = self._create_template()
                changed = True
                actions.append("Create service %s" % self.service_name)
                if not self.check_mode:
                    self.api.create_from_template(template=template)
            elif service and self.replace:
                template = self._create_template()
                changed = True
                actions.append("Replace service %s" % self.service_name)
                if not self.check_mode:
                    self.api.replace_from_template(template=template)
            services[self.service_name] = self.api.get_resource('service', self.service_name)
        elif self.state == 'absent':
            if self.api.get_resource('service', self.service_name):
                changed = True
                actions.append("Delete service %s" % self.service_name)
                if not self.check_mode:
                    self.api.delete_resource('service', self.service_name)

        results['changed'] = changed
        if self.check_mode:
            results['actions'] = actions
        if services:
            results['ansible_facts'] = services
        return results

    def _create_template(self):
        '''
        apiVersion: v1
            kind: Service
            metadata:
              name: frontend
              labels:
                app: guestbook
                tier: frontend
            spec:
              # if your cluster supports it, uncomment the following to automatically create
              # an external load-balanced IP for the frontend service.
              # type: LoadBalancer
              ports:
                # the port that this service should serve on
              - port: 80
              selector:
                app: guestbook
                tier: frontend
        '''

        selector = self.selector if self.selector else self.service_name

        template = dict(
            apiVersion="v1",
            kind="Service",
            metadata=dict(
                name=self.service_name
            ),
            spec=dict(
                selector=selector,
                ports=self.ports
            )
        )

        if self.labels:
            template['metadata']['labels'] = self.labels

        if self.loabalance:
            template['spec']['type'] = 'LoadBalancer'

        return template


def main():
    manager = K8sServiceManager()
    results = manager.exec_module()
    manager.exit_json(**results)


if __name__ == '__main__':
    main()
