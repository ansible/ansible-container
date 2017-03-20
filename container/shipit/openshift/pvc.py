
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import logging
from collections import OrderedDict

from ..base_engine import BaseShipItObject

logger = logging.getLogger(__name__)


class Pvc(BaseShipItObject):

    def _get_template_or_task(self, request_type="task", service_names=None):
        templates = []
        for name, service in self.config.get('services', {}).items():
            new_templates = self._create(name, request_type, service)
            if new_templates:
                templates += new_templates
        return templates

    def _create(self, name, request_type, service):
        '''
        Creates a PVC template or playbook task
        :param request_type:
        '''
        templates = []
        for claim in service.get('options', {}).get('openshift', {}).get('persistent_volume_claims', []):
            if request_type == 'config':
                template = dict(
                    apiVersion="v1",
                    kind="PersistentVolumeClaim",
                    metadata=dict(
                        name=claim['claim_name'],
                    ),
                    spec=dict(
                        requested=dict(
                            storage='1Gi'
                        )
                    )
                )
                if claim.get('access_modes'):
                    template['spec']['accessModes'] = claim['access_modes']
                if claim.get('requested_storage'):
                    template['spec']['requested']['storage'] = claim['requested_storage']
                if claim.get('annotations'):
                    template['metadata']['annotations'] = claim['annotations']
                if claim.get('match_labels'):
                    if not template['spec'].get('selector'):
                        template['spec']['selector'] = dict()
                    template['spec']['selector']['matchLabels'] = claim['match_labels']
                if claim.get('match_expressions'):
                    if not template['spec'].get('selector'):
                        template['spec']['selector'] = dict()
                    template['spec']['selector']['matchExpressions'] = claim['match_expressions']
                if claim.get('persistent_volume_name'):
                    template['spec']['volumeName'] = claim['persistent_volume_name']
            else:
                template = dict(
                    oso_pvc=OrderedDict(
                        project_name=self.project_name,
                        name=claim['claim_name'],
                        state='present',
                    )
                )
                if claim.get('access_modes'):
                    template['oso_pvc']['access_modes'] = claim['access_modes']
                if claim.get('requested_storage'):
                    template['oso_pvc']['requested_storage'] = claim['requested_storage']
                if claim.get('annotations'):
                    template['oso_pvc']['annotations'] = claim['annotations']
                if claim.get('match_labels'):
                    template['oso_pvc']['match_labels'] = claim['match_labels']
                if claim.get('match_expressions'):
                    template['oso_pvc']['match_expressions'] = claim['match_expressions']
                if claim.get('persistent_volume_name'):
                    template['oso_pvc']['volume_name'] = claim['persistent_volume_name']

            templates.append(template)
        return templates
