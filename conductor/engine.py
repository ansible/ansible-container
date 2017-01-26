# -*- coding: utf-8 -*-
from __future__ import absolute_import

import logging

logger = logging.getLogger(__name__)

class BaseEngine(object):
    """
    Interface class for implementations of various container engine integrations
    into Ansible Container.
    """

    @property
    def display_name(self):
        return __name__.split('.')[-2]

    @property
    def ansible_args(self):
        """Additional commandline arguments necessary for ansible-playbook runs."""
        raise NotImplementedError()



    def run_container(self,
                      image_id,
                      project_name,
                      service_name,
                      **kwargs):
        raise NotImplementedError()

    def stop_container(self, *args, **kwargs):
        raise NotImplementedError()

    def restart_container(self, *args, **kwargs):
        raise NotImplementedError()

    def inspect_container(self, container_id):
        raise NotImplementedError()

    def delete_container(self, container_id):
        raise NotImplementedError()

    def get_image_id_by_fingerprint(self, fingerprint):
        raise NotImplementedError()

    def get_image_id_by_tag(self, tag):
        raise NotImplementedError()

    def commit_role_as_layer(self,
                             container_id,
                             project_name,
                             service_name,
                             fingerprint,
                             metadata):
        raise NotImplementedError()
