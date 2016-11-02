#!/usr/bin/env python
from __future__ import print_function

import subprocess
import argparse
import sys
from six import iteritems
from subprocess import CalledProcessError, STDOUT
from time import sleep


def wait_on_hosts(hosts, max_attempts=3, sleep_time=1):
    '''
    Wait for a container to have a State.Running value = true.
    :param hosts: list of service names taken from container.yml
    :param max_attempts: Max number of times to inspect the container and check State.Running
    :param sleep_time: Number of seconds to wait between attempts.
    :return: dict of host:running pairs
    '''
    results = {}
    for host in hosts:
        container = "ansible_{}_1".format(host)
        tries = max_attempts
        host_ready = False
        output = None
        results[host] = False
        while tries > 0 and not host_ready:
            try:
                output = subprocess.check_output(["docker", "inspect", "--format", "{{ .State.Running }}",
                                                  container], stderr=STDOUT)
            except CalledProcessError:
                pass
            tries -= 1
            if output and 'true' in output:
                host_ready = True
                results[host] = True
            else:
                sleep(sleep_time)
    return results

if __name__ == '__main__':

    parser = argparse.ArgumentParser(prog='wait_on_host',
                                     description='Wait for a host or list of hosts to be in a running state')
    parser.add_argument('--max-attempts', '-m', type=int, action='store', default=3,
                        help=u"max number of attempts at checking a container's state, defaults to 3")
    parser.add_argument('--sleep-time', '-s', type=int, action='store', default=1,
                        help=u'number of seconds to wait between attempts, defaults to 1')
    parser.add_argument('host', nargs='+',
                        help=u'name of the host to wait on')
    args = parser.parse_args()

    if args.host:
        results = wait_on_hosts(args.host, max_attempts=args.max_attempts, sleep_time=args.sleep_time)
        status = 0
        for host, running in iteritems(results):
            print("Host {0} {1}".format(host, 'running' if running else 'failed'))
            if not running:
                status = 1
        sys.exit(status)
