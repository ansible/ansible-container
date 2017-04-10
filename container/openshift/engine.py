# -*- coding: utf-8 -*-
from __future__ import absolute_import

import logging
plainLogger = logging.getLogger(__name__)

from container.utils.visibility import getLogger
logger = getLogger(__name__)

import ruamel
from ruamel.yaml.comments import CommentedMap, CommentedSeq

from container import conductor_only, host_only
from container.k8s.engine import Engine as K8s_Engine, log_runs
from container import exceptions
from .deploy import Deployment


try:
    from openshift.helper.openshift import OpenShiftObjectHelper, OpenShiftException
except ImportError:
    raise ImportError('Use of this engine requires you "pip install \'openshift\'" first.')


class Engine(K8s_Engine):

    display_name = u'OpenShift'

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
            self._k8s_client = self._client = OpenShiftObjectHelper()
        return self._k8s_client

    # def _create_ks8_object(self, api_version, kind, request):
    #     name = request.get('metadata', {}).get('name')
    #     namespace = request.get('metadata', {}).get('namespace')
    #
    #     self.client.set_model(api_version, kind)
    #     k8s_obj = self.client.get_object(name, namespace)
    #     if not k8s_obj:
    #         # create when it doesn't exist
    #         try:
    #             k8s_obj = self.client.create_object(namespace, body=request)
    #         except KubernetesException as exc:
    #             raise exceptions.AnsibleContainerConductorException(
    #                 u"Error creating {0}: {1}".format(request['kind'], exc)
    #             )
    #     else:
    #         # otherwise, replace it. not idempotent, but good enough for now
    #         try:
    #             k8s_obj = self.client.replace_object(name, namespace, body=request)
    #         except KubernetesException as exc:
    #             raise exceptions.AnsibleContainerConductorException(
    #                 u"Error creating {0}: {1}".format(request['kind'], exc)
    #             )
    #     return k8s_obj
