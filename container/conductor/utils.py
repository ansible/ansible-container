# -*- coding: utf-8 -*-
from __future__ import absolute_import

import logging

logger = logging.getLogger(__name__)

def metadata_to_image_config(metadata):

    def ports_to_exposed_ports(list_of_ports):
        to_return = {}
        for port_spec in list_of_ports:
            exposed_ports = port_spec.rsplit(':')[-1]
            if '-' in exposed_ports:
                low, high = exposed_ports.split('-', 1)
                for port in range(int(low), int(high)+1):
                    to_return[str(port)] = {}
            else:
                to_return[exposed_ports] = {}
        return to_return

    def format_environment(environment):
        if isinstance(environment, dict):
            return ['='.join(tpl) for tpl in environment.iteritems()]
        else:
            return environment

    TRANSLATORS = {
        # Keys are the key found in the service_data
        # Values are a 2-tuple of the image config JSON key and a function to
        # convert the service_data value to the image config JSON value or None
        # if no translation is necessary

        'hostname': ('Hostname', None),
        'domainname': ('Domainname', None),
        'user': ('User', None),
        'ports': ('ExposedPorts', ports_to_exposed_ports),
        'environment': ('Env', lambda _obj: format_environment)
        'command': ('Cmd', None),
        'working_dir': ('WorkingDir', None),
        'entrypoint': ('Entrypoint', None),
        'volumes': ('Volumes', lambda _list: {parts[0]:{}
                                              for parts in [v.split()
                                                            for v in _list]}),
        'labels': ('Labels', None),
        'onbuild': ('OnBuild', None)
    }

    config = dict(
        Hostname='',
        Domainname='',
        User='',
        ExposedPorts={},
        Env=[],
        Cmd='',
        WorkingDir='',
        Entrypoint=None,
        Volumes={},
        Labels=[],
        OnBuild=[]
    )

    for metadata_key, (key, translator) in TRANSLATORS.iteritems():
        if metadata_key in metadata:
            config[key] = (translator(metadata[metadata_key]) if translator
                           else metadata[metadata_key])
    return config

    }

