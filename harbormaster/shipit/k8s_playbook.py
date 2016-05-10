# -*- coding: utf-8 -*-

import logging

from .k8s_service import K8SService
from .k8s_deployment import K8SDeployment

class K8SPlaybook(object):

    def __init__(self, config=None, project_name=None):
        self.config = config
        self.project_name = project_name

    def build_playbook(self, hosts="localhost"):
        # playbook = dict(
        #     name="%s Deployment" % self.project_name,
        #     hosts=hosts,
        #     connection="local",
        #     gather_facts="no",
        #     tasks=list(),
        # )
        tasks = []
        services = K8SService(config=self.config, project_name=self.project_name).get_task()
        tasks += services

        deployments = K8SDeployment(config=self.config, project_name=self.project_name).get_task()
        task += deployments

        return tasks

    def build_vars(self):
        pass

    def write_role(self, project_dir):





