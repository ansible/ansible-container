#!/usr/bin/python
#
# Copyright 2016 Red Hat | Ansible
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

import glob
import logging
import yaml

from ansible.module_utils.basic import *


K8S_TEMPLATE_DIR = 'k8s_templates'


class K8sApi(object):

    def __init__(self):


    def get_project_name(self, path):
        '''
        Return the basename of the requested path. Attempts to resolve relative paths.

        :param path: target path
        :return: basename of target path
        '''
        original_cwd = os.getcwd()
        try:
            os.chdir(os.path.expanduser(path))
        except Exception as exc:
            self.fail("Failed to access %s - %s" % (path, str(exc)))
        project_path = os.getcwd()
        name = os.path.basename(project_path)
        os.chdir(original_cwd)
        return name

    def use_multiple_deployments(self, services):
        '''
        Inspect services and return True if the app supports multiple replica sets.

        :param services: list of docker-compose service dicts
        :return: bool
        '''
        multiple = True
        for service in services:
            if not service.get('ports'):
                multiple = False
            if service.get('volumes_from'):
                multiple = False
        return multiple

    def write_template(self, project_dir, template, template_type, template_name):
        '''
        Write a k8s template into the project template directory. File name is <template_name>_<template_type>.yml
        Returns the full path to the new template file.

        :param project_dir: path to the project folder, if one was provided by user.
        :type project_dir: str
        :param template: k8s template
        :type template: yaml
        :param template_type: the type of resource the template creates i.e. service, deployment, rc
        :type tempate_type: str
        :param template_name: the descriptive name of the template
        :return: the path to the template file
        '''
        if project_dir:
            dir = os.path.join(project_dir, K8S_TEMPLATE_DIR)
        else:
            dir = K8S_TEMPLATE_DIR

        if not os.path.exists(dir):
            os.makedirs(dir)
        template_path = os.path.join(dir, "%s-%s.yml" % (template_name, template_type))
        self.klog('writing template to %s' % template_path)
        try:
            # with open(template_path, 'w') as f:
            yaml.safe_dump(template, file(template_path,'w'), encoding='utf-8', allow_unicode=True)
        except Exception as exc:
            self.fail("Error writing template %s - %s" % (template_path, str(exc)))
        return template_path

    def get_configuration(self, project_dir, compose_files):
        '''
        Load and validate the docker-compose files.
        :param project_dir: path to the project working dir
        :type project_dir: str
        :param compose_files: docker compose file paths
        :type compose_files: list
        :return:
        '''
        config_files = None
        compose_config = None
        if project_dir:
            cwd = os.getcwd()
            os.chdir(project_dir)
            config_files = [path for path in glob.glob('*.yml') + glob.glob('*.yaml')]
            os.chdir(cwd)
        elif compose_files:
            config_files = compose_files
        if config_files:
            try:
                compose_config = config.load(config.find(project_dir, config_files, dict()))
            except Exception as exc:
                self.fail("Error loading configuration files: %s" % str(exc))
        return compose_config

    def create_from_template(self, template_path):
        self.klog("Create from template %s" % template_path)
        cmd = "kubectl create -f %s" % template_path
        rc, stdout, stderr = self.run_command(cmd)
        self.klog("Received rc: %s" % rc)
        self.klog("stdout:")
        self.klog(stdout)
        self.klog("stderr:")
        self.klog(stderr)
        if rc != 0:
            self.fail("Error creating %s" % template_path, stdout=stdout, stderr=stderr)
        return stdout

    def replace_from_template(self, template_path):
        self.klog("Replace from template %s" % template_path)
        cmd = "kubectl replace -f %s" % template_path
        rc, stdout, stderr = self.run_command(cmd)
        self.klog("Received rc: %s" % rc)
        self.klog("stdout:")
        self.klog(stdout)
        self.klog("stderr:")
        self.klog(stderr)
        if rc != 0:
            self.fail("Error replacing %s" % template_path, stdout=stdout, stderr=stderr)
        return stdout

    def delete_resource(self, type, name):
        cmd = "kubectl delete %s/%s" % (type, name)
        self.klog(cmd)
        rc, stdout, stderr = self.run_command(cmd)
        self.klog("Received rc: %s" % rc)
        self.klog("stdout:")
        self.klog(stdout)
        self.klog("stderr:")
        self.klog(stderr)
        if rc != 0:
            self.fail("Error deleting %s/%s" % (type, name), stdout=stdout, stderr=stderr)
        return stdout

    def get_resource(self, type, name):
        result = None
        cmd = "kubectl get %s/%s -o json" % (type, name)
        self.klog(cmd)
        rc, stdout, stderr = self.run_command(cmd)
        self.klog("Received rc: %s" % rc)
        self.klog("stdout:")
        self.klog(stdout)
        self.klog("stderr:")
        self.klog(stderr)
        if rc == 0:
            result = json.loads(stdout) 
        elif rc != 0 and not re.search('not found', stderr):
            self.fail("Error getting %s/%s" % (type, name), stdout=stdout, stderr=stderr)
        return result
   
    def set_context(self, context_name):
        cmd = "kubectl user-context %s" % context_name
        self.klog(cmd)
        rc, stdout, stderr = self.run_command(cmd)
        self.klog("Received rc: %s" % rc)
        self.klog("stdout:")
        self.klog(stdout)
        self.klog("stderr:")
        self.klog(stderr)
        if rc != 0:
            self.fail("Error switching to context %s" % context_name, stdout=stdout, stderr=stderr)
        return stdout
