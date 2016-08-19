# -*- coding: utf-8 -*-
from __future__ import absolute_import

import logging

logger = logging.getLogger(__name__)

import os
import json
import yaml
import re

from jinja2 import Environment, FileSystemLoader
from collections import Mapping
from .exceptions import AnsibleContainerConfigException

# TODO: Actually do some schema validation

class AnsibleContainerConfig(Mapping):
    _config = {}
    base_path = None

    def __init__(self, base_path, var_files=None):
        self.base_path = base_path
        self.var_files = var_files
        self.config_path = os.path.join(self.base_path, 'ansible/container.yml')
        self._template_vars = None
        self._config = self.set_env('prod')

    def set_env(self, env):
        assert env in ['dev', 'prod']
        config = self._read_config()
        if not config.get('services') or isinstance(config.get('services'), basestring):
            # Services must be defined, and not as a template variable
            raise AnsibleContainerConfigException("No services found in ansible/container.yml. "
                                                  "Have you defined any services?")
        self._template_vars = self._get_variables(config)
        if self._template_vars:
            config = self._render_template()
            logger.debug("Rendered config:")
            logger.debug(config)
            try:
                config = yaml.safe_load(config)
                if config.get('defaults'):
                    del config['defaults']
            except Exception as exc:
                raise AnsibleContainerConfigException("Parsing container.yml - %s" % str(exc))

        for service, service_config in config['services'].items():
            if isinstance(service_config, dict):
                dev_overrides = service_config.pop('dev_overrides', {})
                if env == 'dev':
                    service_config.update(dev_overrides)
        return config

    def _read_config(self):
        '''
        Initial read of container.yml. Ensure all {{ vars }} are escaped with quotes, then parse yaml and
        return the result. This allows us to extract 'defaults' before applying template vars.
        '''
        try:
            ifs = open(self.config_path, 'r')
        except Exception:
            raise AnsibleContainerConfigException("Failed to open %s. Are you in the correct directory?" %
                                                  self.config_path)
        try:
            config = ifs.read()
            config = re.sub(r"}}(?!\"|\')", "}}'", re.sub(r"(?<!\"|\'){{", "'{{", config, flags=re.M), flags=re.M)
            config = yaml.safe_load(config)
            ifs.close()
        except yaml.YAMLError as exc:
            raise AnsibleContainerConfigException("Initial parse of container.yml - %s" % str(exc))
        except Exception as exc:
            raise AnsibleContainerConfigException("Reading container.yml - %s" % str(exc))
        return config

    def _render_template(self):
        j2_tmpl_path = os.path.join(self.base_path, 'ansible')
        j2_env = Environment(loader=FileSystemLoader(j2_tmpl_path))
        j2_tmpl = j2_env.get_template('container.yml')
        return j2_tmpl.render(**self._template_vars).encode('utf8')

    def _get_variables(self, config):
        new_vars = {}
        if config.get('defaults'):
            new_vars.update(config.pop('defaults'))
        if self.var_files:
            logger.debug('Reading variables from var files...')
            for file in self.var_files:
                new_vars.update(self._get_variables_from_file(file))
        new_vars.update(self._get_environment_variables())
        if new_vars:
            logger.debug('Template variables: ')
            logger.debug(json.dumps(new_vars, sort_keys=True, indent=4, separators=(',', ': ')))
        return new_vars

    def _get_environment_variables(self):
        logger.debug('Getting AC environment variables...')
        new_vars = {}
        for var, value in os.environ.iteritems():
            matches = re.match(r'^AC_(.+)$', var)
            if matches:
                new_vars[matches.group(1).lower()] = value
        return new_vars

    def _get_variables_from_file(self, file):
        file_path = os.path.expandvars(os.path.expanduser(file))
        if not os.path.isfile(file_path):
            file_path = os.path.join(self.base_path, file)
            if not os.path.isfile(file_path):
                file_path = os.path.join(self.base_path, 'ansible', file)
        if not os.path.isfile(file_path):
            raise AnsibleContainerConfigException("Unable to locate %s. Check that the file exists and you"
                                                  "have read access." % file_path)
        try:
            fs = open(file_path, 'r')
            data = fs.read()
            fs.close()
        except Exception:
            raise AnsibleContainerConfigException("Failed to open %s. Check that the file exists and you "
                                                  "have read access." % file_path)
        try:
            config = json.loads(data)
        except:
            # Failed to load as JSON. Let's try YAML.
            try:
                config = yaml.safe_load(data)
            except yaml.YAMLError as exc:
                raise AnsibleContainerConfigException("Reading %s\n. YAML exception: %s" % (file_path, str(exc)))
        return config

    def __getitem__(self, item):
        return self._config.get(item)

    def __iter__(self):
        return iter(self._config)

    def __len__(self):
        return len(self._config)

