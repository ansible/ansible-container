#!/usr/bin/env python

import yaml
import json
import sys
import argparse
import re

def config_keys():
    '''
    Read container.yml and return the set of service keys.

    :return: list
    '''
    with open('/ansible-container/ansible/container.yml', 'r') as f:
        config = f.read()
        # Escape any vars. Replaces {{ with '{{ when not preceded by a non-whitespace
        # char and }} with  }}' when not followed by a non-whitespace char.
        config = re.sub(r"}}(?!\S)", "}}'", re.sub(r"(?<!\S){{", "'{{", config))
        config = yaml.safe_load(config)
    return config['services'].keys()

def cmd_list():
    hosts = config_keys()
    return dict(
        docker=hosts,
        _meta=dict(
            hostvars={
                host: {'ansible_host': 'ansible_%s_1' % host}
                for host in hosts
            }
        )
    )

def cmd_host(host):
    hosts = config_keys()
    if host not in hosts:
        return {}
    return dict(
        ansible_host='ansible_%s_1' % host
    )

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=u'Dynamic inventory for ansible-container')
    parser.add_argument('--list', action='store_true', dest='list',
                        help=u'List hosts', default=False)
    parser.add_argument('--host', action='store', dest='host',
                        help=u'Host detail', default=None)
    args = parser.parse_args()
    if args.host:
        json.dump(cmd_host(args.host), sys.stdout)
    else:
        json.dump(cmd_list(), sys.stdout)

