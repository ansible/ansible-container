# -*- coding: utf-8 -*-

import logging
import os
import yaml

import constants
from .k8s_service import K8SService
from .k8s_deployment import K8SDeployment
from .exceptions import ShipItException


logger = logging.getLogger(__name__)


class K8SPlaybook(object):

    def __init__(self, config=None, project_name=None, project_dir=None):
        self.config = config
        self.project_name = project_name
        self.project_dir = project_dir

    def get_tasks(self):
        tasks = []
        services = K8SService(config=self.config, project_name=self.project_name).get_task()
        tasks += services

        deployments = K8SDeployment(config=self.config, project_name=self.project_name).get_task()
        tasks += deployments

        return tasks

    def build_vars(self):
        pass

    def write_deployment(self, hosts="localhost", connection="local", gather_facts=False):
        deploy_path = os.path.join(self.project_dir, constants.SHIPIT_DEPLOY_PATH)
        role_path = os.path.join(deploy_path, 'roles', self.project_name)
        tasks_path = os.path.join(role_path, 'tasks')
        vars_path = os.path.join(role_path, 'vars')

        self.create_path(tasks_path)
        self.create_path(vars_path)

        tasks_playbook = self.get_tasks()
        with open(os.path.join(tasks_path, 'main.yml', 'w')) as f:
            f.write(yaml.dump(tasks_playbook))

        playbook = dict(
            name="%s Deployment" % self.project_name,
            hosts=hosts,
            roles=dict(
                role=self.project_name
            )
        )

        if connection:
            playbook['connection'] = connection
        if not gather_facts:
            playbook['gather_facts'] = False

        with open(os.path.join(deploy_path, 'deploy.yml')) as f:
            f.write(yaml.dump(playbook))

    @staticmethod
    def create_path(path):
        try:
            os.makedirs(path)
        except OSError:
            pass
        except Exception as exc:
            raise ShipItException("Error creating %s - %s" % (path, str(exc)))





