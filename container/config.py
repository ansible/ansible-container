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

    def __init__(self, base_path, var_file=None):
        self.base_path = base_path
        self.var_file = var_file
        self.config_path = os.path.join(self.base_path, 'ansible/container.yml')
        self.set_env('prod')

    def set_env(self, env):
        '''
        Loads config from container.yml, resolves Jinja2 templates and stores the resulting dict to self._config.

        :param env: string of either 'dev' or 'prod'. Indicates 'dev_overrides' handling.
        :return: None
        '''
        assert env in ['dev', 'prod']
        config = self._read_config()
        if not config.get('services') or isinstance(config.get('services'), basestring):
            # Services must be defined, and not as a template variable.
            raise AnsibleContainerConfigException(u"No services found in ansible/container.yml. "
                                                  u"Have you defined any services?")
        template_vars = self._get_variables(config)
        if template_vars:
            config = self._render_template(template_vars)
        for service, service_config in config['services'].items():
            if isinstance(service_config, dict):
                dev_overrides = service_config.pop('dev_overrides', {})
                if env == 'dev':
                    service_config.update(dev_overrides)
        logger.debug(u"Config:\n%s" % json.dumps(config,
                                                 sort_keys=True,
                                                 indent=4,
                                                 separators=(',', ': ')))
        self._config = config

    def _read_config(self):
        '''
        Initial read of container.yml. Ensures all {{ vars }} are escaped with quotes, then parses the Yaml and
        returns the resulting dict. Does not perform Jinja2 template rendering.

        returns: dict
        '''
        try:
            with open(self.config_path, 'r') as f:
                config = f.read()
        except OSError:
            raise AnsibleContainerConfigException(u"Failed to open %s. Are you in the correct directory?" %
                                                  self.config_path)
        try:
            # Escape vars. Replaces {{ with '{{ when not preceeded by a non-whitespace char and }} with  }}' when
            # not followed by a non-whitespace char.
            config = re.sub(r"}}(?!\S)", "}}'", re.sub(r"(?<!\S){{", "'{{", config))
            config = yaml.safe_load(config)
        except yaml.YAMLError as exc:
            raise AnsibleContainerConfigException(u"Initial parse of container.yml - %s" % str(exc))

        return config

    def _render_template(self, template_vars):
        '''
        Reads container.yml, applies Jinja2 template rendering, parses the Yaml and returns the resulting dict.

        :param template_vars: dict providing context for Jinja2 template rendering
        :return: dict
        '''
        j2_tmpl_path = os.path.join(self.base_path, 'ansible')
        j2_env = Environment(loader=FileSystemLoader(j2_tmpl_path))
        j2_tmpl = j2_env.get_template('container.yml')
        config = j2_tmpl.render(**template_vars).encode('utf8')
        logger.debug(u"Rendered config:\n %s" % config)
        try:
            config = yaml.safe_load(config)
        except yaml.YAMLError as exc:
            raise AnsibleContainerConfigException(u"Parsing container.yml - %s" % str(exc))
        if config.get('defaults'):
            del config['defaults']
        return config

    def _get_variables(self, config):
        '''
        Resolve variables by creating an empty dict and updating it first with the 'defaults' section in the config,
        then any variables from var_file, and finally any AC_* environment variables. Returns the resulting dict.

        :param config: dict from parsed container.yml
        :return: dict
        '''
        new_vars = {}
        if config.get('defaults'):
            new_vars.update(config.pop('defaults'))
        if self.var_file:
            logger.debug('Reading variables from var file...')
            new_vars.update(self._get_variables_from_file(self.var_file))
        new_vars.update(self._get_environment_variables())
        logger.debug(u'Template variables:\n %s' % json.dumps(new_vars,
                                                              sort_keys=True,
                                                              indent=4,
                                                              separators=(',', ': ')))
        return new_vars

    def _get_environment_variables(self):
        '''
        Look for any environment variables that start with 'AC_'. Returns dict of key:value pairs, where the
        key is the result of removing 'AC_' from the variable name and converting the remainder to lowercase.
        For example, 'AC_DEBUG=1' becomes 'debug: 1'.

        :return dict
        '''
        logger.debug(u'Getting environment variables...')
        new_vars = {}
        for var, value in os.environ.iteritems():
            matches = re.match(r'^AC_(.+)$', var)
            if matches:
                new_vars[matches.group(1).lower()] = value
        return new_vars

    def _get_variables_from_file(self, file):
        '''
        Read variables from a file. Checks if file contains an absolute path, if not then looks relative to base_path,
        if still not found checks relative to base_path/ansible. If file extension is .yml | .yaml parses as Yaml,
        otherwise attempts to parse as JSON. Returns file contents as dict.

        :param file: string: Absolute file path or path relative to base_path or base_path/ansible.
        :return: dict
        '''
        file_path = file
        if not os.path.isfile(os.path.normpath(file_path)):
            file_path = os.path.normpath(os.path.join(self.base_path, file))
            if not os.path.isfile(file_path):
                file_path = os.path.normpath(os.path.join(self.base_path, 'ansible', file))
                if not os.path.isfile(file_path):
                    raise AnsibleContainerConfigException(u"Unable to locate %s. Provide an absolute file path or "
                                                          u"a path relative to %s or %s." %
                                                          (file,
                                                           os.path.normpath(self.base_path),
                                                           os.path.normpath(os.path.join(self.base_path, 'ansible'))))
        try:
            fs = open(file_path, 'r')
            data = fs.read()
            fs.close()
        except OSError as exc:
            raise AnsibleContainerConfigException(u"Failed to open %s - %s" % (file_path, str(exc)))

        if re.search(r'\.yml$|\.yaml$', file_path):
            # file has '.yml' or '.yaml' extension
            try:
                config = yaml.safe_load(data)
            except yaml.YAMLError as exc:
                raise AnsibleContainerConfigException(u"YAML exception: %s" %  str(exc))
        else:
            try:
                config = json.loads(data)
            except Exception as exc:
                raise AnsibleContainerConfigException(u"JSON exception: %s" % str(exc))
        return config

    def __getitem__(self, item):
        return self._config.get(item)

    def __iter__(self):
        return iter(self._config)

    def __len__(self):
        return len(self._config)

