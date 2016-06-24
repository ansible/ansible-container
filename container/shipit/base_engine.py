# -*- coding: utf-8 -*-
from __future__ import absolute_import

import logging
logger = logging.getLogger(__name__)

import os
import yaml
import re
import glob

from datetime import datetime

from .constants import SHIPIT_PATH, SHIPIT_PLAYBOOK_PREFIX, SHIPIT_ROLES_DIR
from collections import OrderedDict
from .utils import create_path, represent_odict
from ..utils import jinja_render_to_temp


class BaseShipItEngine(object):
    name = None

    def __init__(self, base_path=None, project_name=None, config=None):
        self.base_path = base_path
        self.project_name = project_name
        self.config = config
        self.role_name = "%s-%s" % (self.project_name, self.name)
        self.roles_path = os.path.join(self.base_path, SHIPIT_PATH, SHIPIT_ROLES_DIR, self.role_name)

    def add_options(self, subparser):
        """
        Given an argument subparser, add to it the arguments and options
        this engine allows.

        https://docs.python.org/2/library/argparse.html#sub-commands

        :param subparser: An argparse.ArgumentSubparser
        :return: None
        """
        subparser.add_argument('--save-config', action='store_true',
                               help=(u'Generate and save the %s configuration files in '
                                     u'ansible/shipit_config/kubernetes.' % self.name),
                               dest='save_config', default=False)

        subparser.add_argument('--pull-from', action='store',
                               help=u'Name of a registry defined in container.yml or the actual URL the cluster will '
                                    u'use to pull images. If passing a URL, an example would be: '
                                    u'"registry.example.com:5000/myproject"',
                               dest='pull_from', default=None)

    def run(self):
        """
        Generate an Ansible role and sample playbook to deploy to the target cloud provider.

        :return:
        """
        raise NotImplementedError()

    def save_config(self):
        """
        Called when --save-config option True. Generate configuration templates and write to filesystem.

        :return: string: name of directory where config was saved
        """
        raise NotImplementedError()

    def _copy_modules(self):
        '''
        Copy cloud ansible modules to role library path.
        '''
        cls_dir = os.path.dirname(os.path.realpath(__file__))
        logger.debug("Copying modules from %s:" % cls_dir)
        modules_dir = os.path.join(cls_dir, self.name, 'modules')
        library_path = os.path.join(self.roles_path, 'library')
        create_path(library_path)

        include_files = []
        for mod in glob.glob(modules_dir + '/*.py'):
            with open(mod, 'r') as mod_file:
                for line in mod_file:
                    match = re.search('#include--> ?(\w+.py)', line)
                    if match and match.groups():
                        include_files += list(match.groups())

        include_files = list(set(include_files))
        for mod in glob.glob(modules_dir + '/*.py'):
            base_file = os.path.basename(mod)
            if base_file not in include_files:
                with open(os.path.join(library_path, base_file), 'w') as new_file:
                    with open(mod, 'r') as mod_file:
                        for line in mod_file:
                            match = re.search('#include--> ?(\w+.py)', line)
                            if match and match.groups():
                                with open(os.path.join(modules_dir, match.group(1)), 'r') as inc:
                                    inc_contents = inc.read()
                                new_file.write('\n')
                                new_file.write(inc_contents)
                            else:
                                new_file.write(line)

    def init_role(self):
        '''
        If it does not exist, create the role directory and template in the initial files.
        If it does, backup anything that we plan to overwrite.

        :return:
        '''
        # Init the role directory without overwriting any existing files.
        logger.debug("Creating role path %s" % self.roles_path)
        create_path(self.roles_path)

        shipit_role_paths = {
            u'base': [u'README.j2', u'travis.j2.yml'],
            u'defaults': [u'defaults.j2.yml'],
            u'meta': [u'meta.j2.yml'],
            u'test': [u'test.j2.yml', u'travis.j2.yml'],
            u'tasks': [],
        }

        context = {
            u'role_name': self.role_name,
            u'project_name': self.project_name,
            u'shipit_engine_name': self.name
        }

        for path, templates in shipit_role_paths.items():
            role_dir = os.path.join(self.roles_path, path if path != 'base' else '')
            if path != 'base':
                create_path(role_dir)
            for template in templates:
                target_name = template.replace('.j2', '')
                if target_name.startswith('travis'):
                    target_name = '.' + target_name
                if not os.path.exists(os.path.join(role_dir, target_name)):
                    logger.debug("Rendering template for %s/%s" % (path, template))
                    jinja_render_to_temp('shipit_role/%s' % template,
                                         role_dir,
                                         target_name,
                                         **context)

        # if tasks/main.yml exists, back it up
        now = datetime.today().strftime('%y%m%d%H%M%S')
        tasks_file = os.path.join(self.roles_path, 'tasks', 'main.yml')
        new_tasks_file = os.path.join(self.roles_path, 'tasks', 'main_%s.yml' % now)

        if os.path.exists(tasks_file):
            logger.debug("Backing up tasks/main.yml to main_%s.yml" % now)
            os.rename(tasks_file, new_tasks_file)

        #TODO: limit the number of backups kept?


    def create_role(self, tasks):
        '''
        Creates tasks/mainy.yml with all the deployment tasks, and copy modules into the library dir.

        :param tasks: dict of playbook tasks to be rendered in yaml
        :return: None
        '''

        yaml.SafeDumper.add_representer(OrderedDict,
                                        lambda dumper, value: represent_odict(dumper, u'tag:yaml.org,2002:map', value))

        # Create tasks/main.yml
        output_tasks = []
        for task in tasks:
            task['register'] = "output"
            output_tasks.append(task)
            output_tasks.append(dict(
                debug="var=output",
                when="playbook_debug"
            ))
        stream = yaml.safe_dump(output_tasks, default_flow_style=False)
        with open(os.path.join(self.roles_path, 'tasks', 'main.yml'), 'w') as f:
            f.write(re.sub(r'^-', u'\n-', stream, flags=re.M))

        # Copy ansible modules to library path
        self._copy_modules()

    def create_playbook(self):
        '''
        Create a simple playbook to execute the role. Will only create the playbook if one
        does not exist.

        :return: None
        '''
        playbook_name = "%s-%s.yml" % (SHIPIT_PLAYBOOK_PREFIX, self.name)
        playbook_path = os.path.join(self.base_path, SHIPIT_PATH, playbook_name)
        if not os.path.exists(playbook_path):
            logger.debug('Creating the sample plabyook')
            play = OrderedDict()
            play['name'] = "Deploy %s to  %s" % (self.project_name, self.name)
            play['hosts'] = 'localhost'
            play['gather_facts'] = False
            play['connection'] = 'local'
            play['vars'] = dict(
                playbook_debug=False
            )
            play['roles'] = [dict(
                role=self.role_name
            )]
            with open(playbook_path, 'w') as f:
                f.write(yaml.safe_dump([play], default_flow_style=False))

