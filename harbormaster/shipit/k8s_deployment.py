
# -*- coding: utf-8 -*-

import logging
import re

logger = logging.getLogger(__name__)


class K8SDeployment(object):

    def __init__(self, config=None, project_name=None):
        self.project_name = project_name
        self.config = config

    def get_template(self, service_names=None):
        templates = []
        for service in self.config.services:
            if not service_names or service['name'] in service_names:
                templates.append(self._create_template(service))
        return templates

    def get_task(self, service_names=None):
        templates = []
        for service in self.config.services:
            if not service_names or service['name'] in service_names:
                templates.append(self._create_template(service))
        return templates

    def _create_template(self, service):
        '''
        Creates a deployment template from a set of services. Each service is a container
        defined in the replication controller.
        '''

        name = "%s-%s" % (self.project_name, service['name'])
        containers = [self._service_to_container(service)]

        template = dict(
            apiVersion="v1",
            kind="DeploymentConfig",
            metadata=dict(
                name=name,
            ),
            spec=dict(
                template=dict(
                    metadata=dict(
                        labels=dict(
                            app=service['name']
                        )
                    ),
                    spec=dict(
                        containers=containers
                    )
                ),
                replicas=1,
                selector=dict(
                    name=service['name']
                ),
                strategy=dict(
                    type='Rolling'
                )
            )
        )

        return template

    def _create_task(self, service):
        '''
        Generates an Ansible playbook task.

        :param service:
        :return:
        '''

        containers = [self._service_to_container(service)]

        template = dict(
            k8s_deployment=dict(
                project_name=self.project_name,
                service_name=service['name'],
                labels=dict(
                    app=service['name']
                ),
                containers=containers,
                replicas=1,
                strategy='Rolling'
            )
        )

        return template

    def _service_to_container(self, service):
        container = dict(name=service['name'])
        for key, value in service.items():
            if key == 'ports':
                container['ports'] = self._get_container_ports(value)
            elif key in ('links', 'labels'):
                pass
            elif key == 'environment':
                container['env'] = self._expand_env_vars(value)
            else:
                container[key] = value
        return container

    @staticmethod
    def _get_container_ports(ports):
        '''
        Convert docker ports to list of kube containerPort
        :param ports:
        :type ports: list
        :return:
        '''
        results = []
        for port in ports:
            if ':' in port:
                parts = port.split(':')
                results.append(dict(containerPort=int(parts[1])))
            else:
                results.append(port)
        return results

    @staticmethod
    def _expand_env_vars(env_variables):
        '''
        Turn container environment attribute into kube env dictionary of name/value pairs.

        :param env_variables: container env attribute value
        :type env_variables: dict or list
        :return: dict
        '''
        def f(x):
            return re.sub('^k8s_', '', x, flags=re.I)

        def m(x):
            return re.match('k8s_', x, flags=re.I)

        def r(x, y):
            if m(x):
                return dict(name=f(x), value=self._resolve_resource(y))
            return dict(name=x, value=y)

        results = []
        if isinstance(env_variables, dict):
            for key, value in env_variables.items():
                results.append(r(key, value))
        elif isinstance(env_variables, list):
            for envvar in env_variables:
                parts = envvar.split('=')
                if len(parts) == 1:
                    results.append(dict(name=f(parts[0]), value=None))
                elif len(parts) == 2:
                    results.append(r(parts[0], parts[1]))
        return results

    @staticmethod
    def _resolve_resource(path):
        result = path
        if '/' in path:
            res_type, res_name = path.split('/')
            result = unicode("{{ %s_%s }} " % (res_type, res_name))
        return result
