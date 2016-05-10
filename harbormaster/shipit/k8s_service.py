# -*- coding: utf-8 -*-

import logging


class K8SService(object):

    def __init__(self, config=None, project_name=None):
        self.project_name = project_name
        self.config = config
        self.logger = logging.getLogger(__name__)

    def get_template(self, service_names=None):
        templates = []
        for service in self.config.services:
            if not service_names or service['name'] in service_names:
                if service.get('ports'):
                    templates.append(self._create_template(service))
        return templates

    def get_task(self, service_names=None):
        templates = []
        for service in self.config.services:
            if not service_names or service['name'] in service_names:
                if service.get('ports'):
                    templates.append(self._create_task(service))
        return templates

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

        labels = self._get_labels(service)
        ports = self._get_ports(service)

        name = "%s-%s" % (self.project_name, service['name'])
        template = dict(
            apiVersion="v1",
            kind="Service",
            metadata=dict(
                name=name,
                labels=labels
            ),
            spec=dict(
                selector=dict(
                    app=service['name']
                ),
                ports=ports,
            )
        )

        if labels.get('service_type') == 'loadbalancer':
            template['spec']['type'] = 'LoadBalancer'

        return template

    def _create_task(self, service):
        '''
        Generates an Ansible playbook task.

        :param service:
        :return:
        '''

        labels = self._get_labels(service)
        ports = self._get_ports(service)

        template = dict(
            k8s_service=dict(
                project_name=self.project_name,
                service_name=service['name'],
                labels=labels,
                ports=ports,
            )
        )

        if labels.get('service_type') == 'loadbalancer':
            template['k8s_service']['loadbalancer'] = True

        return template

    @staticmethod
    def _get_labels(service):
        if service.get('labels'):
            labels = service['labels']
            labels.update(dict(app=service['name']))
        else:
            labels = dict(app=service['name'])

        for key, value in labels.items():
            if not isinstance(value, str):
                labels[key] = str(value)
        return labels

    @staticmethod
    def _get_ports(service):
        ports = []
        labels = service.get('labels')
        if labels.get('service_port'):
            parts = labels.get('service_port').split(':')
            ports.append(dict(port=int(parts[0]), targetPort=int(parts[1]), protocol='TCP'))
            labels.pop('service_port')
        else:
            for port in service['ports']:
                if ':' in port:
                    parts = port.split(':')
                    ports.append(dict(port=int(parts[0]), protocol='TCP'))
                else:
                    ports.append(dict(port=int(port), protocol='TCP'))
        return ports
