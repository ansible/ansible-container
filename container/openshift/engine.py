# -*- coding: utf-8 -*-
from __future__ import absolute_import

import logging
plainLogger = logging.getLogger(__name__)

from container.utils.visibility import getLogger
logger = getLogger(__name__)

import ruamel
from ruamel.yaml.comments import CommentedMap, CommentedSeq

from container import conductor_only, host_only
from container.docker.engine import Engine as DockerEngine, log_runs
from container import exceptions
from .deploy import Deployment


try:
    from openshift.helper.kubernetes import KubernetesObjectHelper, KubernetesException
except ImportError:
    raise ImportError('Use of this engine requires you "pip install \'openshift\'" first.')


class Engine(DockerEngine):

    # Capabilities of engine implementations
    CAP_BUILD_CONDUCTOR = False
    CAP_BUILD = False
    CAP_DEPLOY = True
    CAP_IMPORT = False
    CAP_LOGIN = True
    CAP_PUSH = True
    CAP_RUN = True

    display_name = u'K8s'

    _client = None
    _k8s_client = None
    _deployment = None

    FINGERPRINT_LABEL_KEY = 'com.ansible.container.fingerprint'
    LAYER_COMMENT = 'Built with Ansible Container (https://github.com/ansible/ansible-container)'

    @property
    def deployment(self):
        if not self._deployment:
            self._deployment = Deployment(self.services, self.project_name)
        return self._deployment

    @property
    def k8s_client(self):
        if not self._k8s_client:
            self._k8s_client = self._client = KubernetesObjectHelper()
        return self._k8s_client

    @log_runs
    @host_only
    def run_conductor(self, command, config, base_path, params, engine_name=None):
        engine_name = __name__.rsplit('.', 2)[-2]
        return super(Engine, self).run_conductor(command, config, base_path, params, engine_name=engine_name)

    @conductor_only
    def generate_orchestration_playbook(self, repository_data=None):
        """ If repository_data is specified, presume to pull images from that
        repository. If not, presume the images are already present. """

        for service_name in self.services:
            image = self.get_latest_image_for_service(service_name)
            self.services[service_name]['image'] = image.tags[0]

        play = CommentedMap()
        play['name'] = 'Deploy {} to {}'.format(self.project_name, self.display_name)
        play['hosts'] = 'localhost'
        play['gather_facts'] = 'no'
        play['connection'] = 'local'
        play['roles'] = CommentedSeq()
        play['tasks'] = CommentedSeq()

        role = """
        # Include Ansible Kubernetes and OpenShift modules
        role: kubernetes-modules
        """
        role_yaml = ruamel.yaml.round_trip_load(role)
        play['roles'].append(role_yaml)

        if len(self.deployment.service_tasks):
            play['tasks'].extend(self.deployment.service_tasks)

        if len(self.deployment.deployment_tasks):
            play['tasks'].extend(self.deployment.deployment_tasks)

        playbook = CommentedSeq()
        playbook.append(play)

        logger.debug(u'Created playbook to run project', playbook=playbook)
        return playbook

    def _create_ks8_object(self, api_version, kind, request):
        name = request.get('metadata', {}).get('name')
        namespace = request.get('metadata', {}).get('namespace')

        self.client.set_model(api_version, kind)
        k8s_obj = self.client.get_object(name, namespace)
        if not k8s_obj:
            # create when it doesn't exist
            try:
                k8s_obj = self.client.create_object(namespace, body=request)
            except KubernetesException as exc:
                raise exceptions.AnsibleContainerConductorException(
                    u"Error creating {0}: {1}".format(request['kind'], exc)
                )
        else:
            # otherwise, replace it. not idempotent, but good enough for now
            try:
                k8s_obj = self.client.replace_object(name, namespace, body=request)
            except KubernetesException as exc:
                raise exceptions.AnsibleContainerConductorException(
                    u"Error creating {0}: {1}".format(request['kind'], exc)
                )
        return k8s_obj
