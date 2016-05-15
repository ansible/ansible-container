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


from .k8s_common import AnsibleKubeCtl


K8_TEMPLATE_DIR = 'k8s_templates'


class K8sServiceManager(AnsibleKubeCtl):

    def __init__(self):

        self.arg_spec = dict(
            context=dict(type='str'),
            project_name=dict(type='str', aliases=['namespace']),
            state=dict(type='str', choices=['present', 'absent'], default='present'),
            labels=dict(type='dict'),
            ports=dict(type='list'),
            service_name=dict(type='str'),
            loadbalance=dict(type='bool', default=False),
            replace=dict(type='bool', default=False),
            selector=dict(type='dict')
        )

        self.context = None
        self.project_name = None
        self.state = None
        self.labels = None
        self.ports = None
        self.service_name = None
        self.loabalance = None
        self.selector = None

        super(K8sServiceManager, self).__init__(self.arg_spec,
                                                supports_check_mode=True)

    def exec_module(self):

        for key in self.arg_spec:
            setattr(self, key, self.params.get(key))

        actions = []
        changed = False
        services = dict()
        results = dict()

        project_switch = self.set_project(self.project_name)
        if not project_switch:
            actions.append("Create project %s" % self.project_name)
            self.create_project(self.project_name)

        if self.state == 'present':
            service = self.get_resource('service', self.service_name)
            if not service or self.replace:
                template = self._create_template()
                changed = True
                actions.append("Create service %s" % self.service_name)
                self.create_from_template(template=template)
                services[self.service_name] = self.get_resource('service', self.service_name)
        elif self.state == 'absent':
            if self.get_resource('service', self.service_name):
                changed = True
                actions.append("Delete service %s" % self.service_name)
                self.delete_resource('service', self.sevice_name)

        results['changed'] = changed
        if self.check_mode:
            results['actions'] = actions
        if services:
            results['ansible_facts'] = services
        return results

    def _create_template(self, service):
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
