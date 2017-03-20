# -*- coding: utf-8 -*-

from __future__ import absolute_import
import logging

logger = logging.getLogger(__name__)


from collections import OrderedDict
from six import string_types
from ..base_engine import BaseShipItObject


class Route(BaseShipItObject):

    def _get_template_or_task(self, request_type="task"):
        templates = []
        for name, service in self.config.get('services', {}).items():
            new_routes = self._create(name, request_type, service)
            if new_routes:
                templates += new_routes
        return templates

    def _create(self, name, request_type, service):
        '''
        Generate Openshift route templates or playbook tasks. Each port on a service definition
        represents an externally exposed port.
        :param request_type:
        '''

        templates = []
        hostname = None

        options = service.get('options', {}).get('openshift', {})
        state = options.get('state', 'present')

        if options.get('hostname'):
            hostname = options['hostname']

        service_ports = self._get_service_ports(service)

        if service_ports:
            for port in service_ports:
                route_name = "%s-%s" % (name, port)
                labels = dict(
                    app=self.project_name,
                    service=name
                )

                if request_type == 'config' and state != 'absent':
                    template = dict(
                        apiVersion="v1",
                        kind="Route",
                        metadata=dict(
                            name=route_name,
                            labels=labels.copy()
                        ),
                        spec=dict(
                            to=dict(
                                kind='Service',
                                name=name,
                            ),
                            port=dict(
                                targetPort="port-%s" % port
                            )
                        )
                    )
                    if hostname:
                        template['spec']['host'] = hostname
                else:
                    template = dict(
                        oso_route=OrderedDict(
                            project_name=self.project_name,
                            route_name=route_name,
                            labels=labels.copy(),
                            service_name=name,
                            service_port="port-%s" % port,
                            replace=True,
                        )
                    )
                    if hostname:
                        template['oso_route']['host'] = hostname

                    template['oso_route']['state'] = state

                templates.append(template)

        return templates

    def _get_service_ports(self, service):
        '''
        Get the external port and the target container port.

        :param service: dict of service attributes
        :return: (external port, target port)
        '''

        #TODO: port ranges?

        result = []
        for port in service.get('ports', []):
            if isinstance(port, string_types) and ':' in port:
                parts = port.split(':')
                result.append(parts[0])
            else:
                result.append(port)
        return result
