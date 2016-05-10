

class K8SService(object):



    def _set_creation_timestamp(self, services):
        '''
        We need to know if a service already exists. This adds a creationTimestamp attribute to each service.
        If the creationTimestamp is null, then the service does not exist.
        :return:
        '''
        for service in services:
            service['creationTimestamp'] = None
            name = "%s-%s" % (self.project_name, service['name'])
            current = self.get_resource('service', name)
            if current:
                service['creationTimestamp'] = current['metadata']['creationTimestamp']
        return services

    def _create_services(self, services):
        actions = []
        changed = False
        for service in services:
            if not service.get('creationTimestamp') or (service.get('creationTimestamp') and self.replace):
                if service.get('ports'):
                    template = self._create_template(service)
                    template_path = self.write_template(self.project_src, template, 'service',
                                                        template['metadata']['name'])
                    actions.append("Created template %s" % template_path)
                    changed = True
                    if not service.get('creationTimestamp'):
                        actions.append("Created service %s" % service['name'])
                        self.create_from_template(template_path)
                    else:
                        actions.append("Replaced service %s" % service['name'])
                        self.replace_from_template(template_path)
        return changed, actions

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
        if service.get('labels'):
            labels = service['labels']
            labels.update(dict(app=service['name']))
        else:
            labels = dict(app=service['name'])

        for key, value in labels.items():
            if not isinstance(value, str):
                labels[key] = str(value)

        ports = []
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

        if service.get('creationTimestamp'):
            template = self.get_resource('service', service['name'])
        else:
            name = "%s-%s" % (self.project_name, service['name'])
            template = dict(
                apiVersion="v1",
                kind="Service",
                metadata=dict(
                    name=name,
                ),
                spec=dict(
                    selector=dict(
                        app=service['name']
                    )
                )
            )

        template['metadata']['labels'] = labels
        template['spec']['ports'] = ports

        if labels.get('service_type') == 'loadbalancer':
            template['spec']['type'] = 'LoadBalancer'

        self.klog("template for service %s" % service['name'])
        self.klog(template, pretty_print=True)

        return template