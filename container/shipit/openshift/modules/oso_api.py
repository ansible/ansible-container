import os
import re
import subprocess
import shlex
import json
import select


class OriginAPI(object):

    def __init__(self, target="oc"):
        self.target = target

    @staticmethod
    def use_multiple_deployments(services):
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

    def run_command(self, args, data=None, path_prefix=None, cwd=None, prompt_regex=None, environ_update=None):
        '''
        Execute a command, returns rc, stdout, and stderr.

        :arg args: is the command to run
            * If args is a list, the command will be run with shell=False.
            * If args is a string, it will split args to a list and run with shell=False
        :kw data: If given, information to write to the stdin of the command
        :kw path_prefix: If given, additional path to find the command in.
            This adds to the PATH environment vairable so helper commands in
            the same directory can also be found
        :kw cwd: iIf given, working directory to run the command inside
        :kw use_unsafe_shell: See `args` parameter.  Default False
        :kw prompt_regex: Regex string (not a compiled regex) which can be
            used to detect prompts in the stdout which would otherwise cause
            the execution to hang (especially if no input data is specified)
        :kwarg environ_update: dictionary to *update* os.environ with
        '''

        shell = False
        if isinstance(args, basestring):
            if isinstance(args, unicode):
                args = args.encode('utf-8')
            args = shlex.split(args)
        else:
            raise OriginAPIException("Argument 'args' to run_command must be list or string")

        prompt_re = None
        if prompt_regex:
            try:
                prompt_re = re.compile(prompt_regex, re.MULTILINE)
            except re.error:
                raise OriginAPIException("Invalid prompt regular expression given to run_command")

        # expand things like $HOME and ~
        if not shell:
            args = [os.path.expandvars(os.path.expanduser(x)) for x in args if x is not None]

        rc = 0
        msg = None
        st_in = None

        # Manipulate the environ we'll send to the new process
        old_env_vals = {}
        # We can set this from both an attribute and per call
        # for key, val in self.run_command_environ_update.items():
        #     old_env_vals[key] = os.environ.get(key, None)
        #     os.environ[key] = val
        if environ_update:
            for key, val in environ_update.items():
                old_env_vals[key] = os.environ.get(key, None)
                os.environ[key] = val
        if path_prefix:
            old_env_vals['PATH'] = os.environ['PATH']
            os.environ['PATH'] = "%s:%s" % (path_prefix, os.environ['PATH'])

        # If using test-module and explode, the remote lib path will resemble ...
        #   /tmp/test_module_scratch/debug_dir/ansible/module_utils/basic.py
        # If using ansible or ansible-playbook with a remote system ...
        #   /tmp/ansible_vmweLQ/ansible_modlib.zip/ansible/module_utils/basic.py

        # Clean out python paths set by ziploader
        if 'PYTHONPATH' in os.environ:
            pypaths = os.environ['PYTHONPATH'].split(':')
            pypaths = [x for x in pypaths \
                        if not x.endswith('/ansible_modlib.zip') \
                        and not x.endswith('/debug_dir')]
            os.environ['PYTHONPATH'] = ':'.join(pypaths)

        if data:
            st_in = subprocess.PIPE

        kwargs = dict(
            executable=None,
            shell=shell,
            close_fds=True,
            stdin=st_in,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        if cwd and os.path.isdir(cwd):
            kwargs['cwd'] = cwd

        # store the pwd
        prev_dir = os.getcwd()

        # make sure we're in the right working directory
        if cwd and os.path.isdir(cwd):
            try:
                os.chdir(cwd)
            except (OSError, IOError) as exc:
                raise OriginAPIException("Could not open %s, %s" % (cwd, str(exc)))

        try:
            cmd = subprocess.Popen(args, **kwargs)
            stdout = ''
            stderr = ''
            rpipes = [cmd.stdout, cmd.stderr]

            if data:
                data += '\n'
                cmd.stdin.write(data)
                cmd.stdin.close()

            while True:
                rfd, wfd, efd = select.select(rpipes, [], rpipes, 1)
                if cmd.stdout in rfd:
                    dat = os.read(cmd.stdout.fileno(), 9000)
                    stdout += dat
                    if dat == '':
                        rpipes.remove(cmd.stdout)
                if cmd.stderr in rfd:
                    dat = os.read(cmd.stderr.fileno(), 9000)
                    stderr += dat
                    if dat == '':
                        rpipes.remove(cmd.stderr)
                # if we're checking for prompts, do it now
                if prompt_re:
                    if prompt_re.search(stdout) and not data:
                        return (257, stdout,
                                "A prompt was encountered while running a command, but no input data was specified")
                # only break out if no pipes are left to read or
                # the pipes are completely read and
                # the process is terminated
                if (not rpipes or not rfd) and cmd.poll() is not None:
                    break
                # No pipes are left to read but process is not yet terminated
                # Only then it is safe to wait for the process to be finished
                # NOTE: Actually cmd.poll() is always None here if rpipes is empty
                elif not rpipes and cmd.poll() == None:
                    cmd.wait()
                    # The process is terminated. Since no pipes to read from are
                    # left, there is no need to call select() again.
                    break
            cmd.stdout.close()
            cmd.stderr.close()
            rc = cmd.returncode
        except Exception:
            raise

        # Restore env settings
        for key, val in old_env_vals.items():
            if val is None:
                del os.environ[key]
            else:
                os.environ[key] = val

        os.chdir(prev_dir)
        return rc, stdout, stderr

    def create_from_template(self, template=None, template_path=None):
        if template_path:
            logger.debug("Create from template %s" % template_path)
            cmd = "%s create -f %s" % (self.target, template_path)
            rc, stdout, stderr = self.run_command(cmd)
            logger.debug("Received rc: %s" % rc)
            logger.debug("stdout:")
            logger.debug(stdout)
            logger.debug("stderr:")
            logger.debug(stderr)
            if rc != 0:
                raise OriginAPIException("Error creating %s" % template_path, stderr=stderr, stdout=stdout)
            return stdout
        if template:
            logger.debug("Create from template:")
            formatted_template = json.dumps(template, sort_keys=False, indent=4, separators=(',', ':'))
            logger.debug(formatted_template)
            cmd = "%s create -f -" % self.target
            rc, stdout, stderr = self.run_command(cmd, data=formatted_template)
            logger.debug("Received rc: %s" % rc)
            logger.debug("stdout:")
            logger.debug(stdout)
            logger.debug("stderr:")
            logger.debug(stderr)
            if rc != 0:
                raise OriginAPIException("Error creating from template.", stderr=stderr, stdout=stdout)
            return stdout

    def replace_from_template(self, template=None, template_path=None):
        if template_path:
            logger.debug("Replace from template %s" % template_path)
            cmd = "%s replace -f %s" % (self.target, template_path)
            rc, stdout, stderr = self.run_command(cmd)
            logger.debug("Received rc: %s" % rc)
            logger.debug("stdout:")
            logger.debug(stdout)
            logger.debug("stderr:")
            logger.debug(stderr)
            if rc != 0:
                raise OriginAPIException("Error replacing %s" % template_path, stderr=stderr, stdout=stdout)
            return stdout
        if template:
            logger.debug("Replace from template:")
            formatted_template = json.dumps(template, sort_keys=False, indent=4, separators=(',', ':'))
            logger.debug(formatted_template)
            cmd = "%s replace -f -" % self.target
            rc, stdout, stderr = self.run_command(cmd, data=formatted_template)
            logger.debug("Received rc: %s" % rc)
            logger.debug("stdout:")
            logger.debug(stdout)
            logger.debug("stderr:")
            logger.debug(stderr)
            if rc != 0:
                raise Exception("Error replacing from template", stderr=stderr, stdout=stdout)
            return stdout

    def delete_resource(self, type, name):
        cmd = "%s delete %s/%s" % (self.target, type, name)
        logger.debug("exec: %s" % cmd)
        rc, stdout, stderr = self.run_command(cmd)
        logger.debug("Received rc: %s" % rc)
        logger.debug("stdout:")
        logger.debug(stdout)
        logger.debug("stderr:")
        logger.debug(stderr)
        if rc != 0:
            raise OriginAPIException("Error deleting %s/%s" % (type, name), stderr=stderr, stdout=stdout)
        return stdout

    def get_resource(self, type, name):
        result = None
        cmd = "%s get %s/%s -o json" % (self.target, type, name)
        logger.debug("exec: %s" % cmd)
        rc, stdout, stderr = self.run_command(cmd)
        logger.debug("Received rc: %s" % rc)
        logger.debug("stdout:")
        logger.debug(stdout)
        logger.debug("stderr:")
        logger.debug(stderr)
        if rc == 0:
            result = json.loads(stdout) 
        elif rc != 0 and not re.search('not found', stderr):
            raise OriginAPIException("Error getting %s/%s" % (type, name), stderr=stderr, stdout=stdout)
        return result
   
    def set_context(self, context_name):
        cmd = "%s user-context %s" % (self.target, context_name)
        logger.debug("exec: %s" % cmd)
        rc, stdout, stderr = self.run_command(cmd)
        logger.debug("Received rc: %s" % rc)
        logger.debug("stdout:")
        logger.debug(stdout)
        logger.debug("stderr:")
        logger.debug(stderr)
        if rc != 0:
            raise OriginAPIException("Error switching to context %s" % context_name, stderr=stderr, stdout=stdout)
        return stdout

    def set_project(self, project_name):
        result = True
        cmd = "%s project %s" % (self.target, project_name)
        logger.debug("exec: %s" % cmd)
        rc, stdout, stderr = self.run_command(cmd)
        logger.debug("Received rc: %s" % rc)
        logger.debug("stdout:")
        logger.debug(stdout)
        logger.debug("stderr:")
        logger.debug(stderr)
        if rc != 0:
            result = False
            if not re.search('does not exist', stderr):
                raise OriginAPIException("Error switching to project %s" % project_name, stderr=stderr, stdout=stdout)
        return result

    def create_project(self, project_name):
        result = True
        cmd = "%s new-project %s" % (self.target, project_name)
        logger.debug("exec: %s" % cmd)
        rc, stdout, stderr = self.run_command(cmd)
        logger.debug("Received rc: %s" % rc)
        logger.debug("stdout:")
        logger.debug(stdout)
        logger.debug("stderr:")
        logger.debug(stderr)
        if rc != 0:
            raise OriginAPIException("Error creating project %s" % project_name, stderr=stderr, stdout=stdout)
        return result

    def get_deployment(self, deployment_name):
        cmd = "%s deploy %s" % (self.target, deployment_name)
        logger.debug("exec: %s" % cmd)
        rc, stdout, stderr = self.run_command(cmd)
        logger.debug("Received rc: %s" % rc)
        logger.debug("stdout:")
        logger.debug(stdout)
        logger.debug("stderr:")
        logger.debug(stderr)
        if rc != 0:
            if not re.search('not found', stderr):
                raise OriginAPIException("Error getting deployment state %s" % deployment_name, stderr=stderr,
                                         stdout=stdout)
        return stdout


class OriginAPIException(Exception):

    def __init__(self, msg, stdout=None, stderr=None):
        self.stderr = stderr
        self.stdout = stdout

        Exception.__init__(self, msg)