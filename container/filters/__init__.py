# -*- coding: utf-8 -*-

from __future__ import absolute_import

import logging
logger = logging.getLogger(__name__)

import glob
import os
import imp

from container.exceptions import AnsibleContainerFilterException


def get_package_path(package):
    m = __import__(package)
    parts = package.split('.')[1:]
    for part in parts:
        m = getattr(m, part)
    package_path = os.path.dirname(m.__file__)
    return package_path


def get_filters(package_path, local=False):
    matches = (glob.glob(os.path.join(package_path, "*.py")))
    for path in matches:
        name, _ = os.path.splitext(path)
        if '__init__' in name:
            continue
        if not local:
            with open(path, 'r') as module_file:
                module_src = imp.load_source(name, path, module_file)
        else:
            module_src = __import__('container.filters.{0}'.format(os.path.basename(name)),
                                    fromlist='FilterModule')
        yield getattr(module_src, 'FilterModule')()


ANSIBLE_LOOKUP_NAME = 'ansible.plugins.lookup'
ANSIBLE_FILTERS_NAME = 'ansible.plugins.filter'


class LookupLoader(object):

    module_cache = {}

    def get(self, name):
        '''
        Load a lookup class and return an instance.

        :param name: string containing the name of the lookup submodule to load.
        :return: instance of the LookupModule class defined in the submodule
        '''
        obj = None
        package_path = os.path.dirname(__file__)
        path = os.path.join(package_path, 'lookup', "{0}.py".format(name.lower()))
        if os.path.isfile(path):
            try:
                if not self.module_cache.get(path):
                    self.module_cache[path] = __import__('container.filters.lookup.{0}'.format(name),
                                                         fromlist='LookupModule')
                obj = getattr(self.module_cache[path], 'LookupModule')()
            except Exception as exc:
                logger.debug("Unable to find local filter {0} - {1}".format(name, str(exc)))
                pass

        if not obj:
            # Attempt to load Ansible filter
            package_path = get_package_path(ANSIBLE_LOOKUP_NAME)
            path = os.path.join(package_path, "{0}.py".format(name.lower()))
            if os.path.isfile(path):
                try:
                    if not self.module_cache.get(path):
                        name, _ = os.path.splitext(path)
                        with open(path, 'r') as module_file:
                            self.module_cache[path] = imp.load_source(name, path, module_file)
                    obj = getattr(self.module_cache[path], 'LookupModule')()
                except Exception as exc:
                    raise AnsibleContainerFilterException("Failed to load lookup filter {0} - {1}".format(name,
                                                                                                          str(exc)))
            else:
                raise AnsibleContainerFilterException("Filter {0} not found.".format(name))
        return obj


class FilterLoader(object):

    all_filters = {}

    def all(self):
        '''
        Load all Jinja filters found in Ansible and locally with local filters taking precedence.

        :return: dict
        '''
        if not self.all_filters:
            try:
                package_path = get_package_path(ANSIBLE_FILTERS_NAME)
                for obj in get_filters(package_path):
                    self.all_filters.update(obj.filters())
            except Exception as exc:
                logger.debug('Failed to load ansible.plugin.filters - {0}'.format(str(exc)))
                pass

            try:
                package_path = os.path.dirname(__file__)
                for obj in get_filters(package_path, local=True):
                    self.all_filters.update(obj.filters())
            except Exception as exc:
                logger.debug('Failed to load plugin.filter - {0}'.format(str(exc)))
                pass

        return self.all_filters


class FilterBase(object):

    def filters(self):
        '''
        Get available filters.
        :return: dict of filters
        '''
        raise NotImplementedError()



