#!/usr/bin/env python

import yaml
import json
import sys
import argparse
import re
import os


def config_keys():
    '''
    Get the list of hosts from env var ANSIBLE_ORCHESTRATED_HOSTS.

    :return: list
    '''
    return os.environ.get('ANSIBLE_ORCHESTRATED_HOSTS', '').split(',')


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

