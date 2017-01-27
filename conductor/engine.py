# -*- coding: utf-8 -*-
from __future__ import absolute_import

import logging

logger = logging.getLogger(__name__)

class BaseEngine(object):
    """
    Interface class for implementations of various container engine integrations
    into Ansible Container.
    """

    def __init__(self, project_name, services):
        self.project_name = project_name
        self.services = services

    @property
    def display_name(self):
        return __name__.split('.')[-2]

    @property
    def ansible_args(self):
        """Additional commandline arguments necessary for ansible-playbook runs."""
        raise NotImplementedError()

    def run_container(self,
                      image_id,
                      service_name,
                      **kwargs):
        """Run a particular container. The kwargs argument contains individual
        parameter overrides from the service definition."""
        raise NotImplementedError()

    def stop_container(self, container_id):
        raise NotImplementedError()

    def restart_all_containers(self):
        raise NotImplementedError()

    def inspect_container(self, container_id):
        raise NotImplementedError()

    def delete_container(self, container_id):
        raise NotImplementedError()

    def get_container_id_for_service(self, service_name):
        raise NotImplementedError()

    def get_image_id_by_fingerprint(self, fingerprint):
        raise NotImplementedError()

    def get_image_id_by_tag(self, tag):
        raise NotImplementedError()

    def get_latest_image_id_for_service(self, service_name):
        raise NotImplementedError()

    def commit_role_as_layer(self,
                             container_id,
                             service_name,
                             fingerprint,
                             metadata):
        raise NotImplementedError()

    def orchestrate(self):
        raise NotImplementedError()

