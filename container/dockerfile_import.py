# -*- coding: utf-8 -*-
from __future__ import absolute_import

import json
import logging
import os
import re

import ruamel.yaml
from ruamel.yaml.comments import CommentedMap

from .utils import create_role_from_templates
from .exceptions import AnsibleContainerException

logger = logging.getLogger(__name__)


class DockerfileImport(object):
    base_path = None
    alternate_file_name = None
    docker_file_path = None
    dockerfile = {}
    cached_instructions = None
    project_name = None
    role_path = None

    def __init__(self, base_path, project_name, alternate_file_name):
        self.base_path = base_path
        self.project_name = project_name
        self.alternate_file_name = alternate_file_name
        file_name = self.alternate_file_name if self.alternate_file_name else u'Dockerfile'
        self.docker_file_path = os.path.normpath(os.path.join(self.base_path, file_name))
        self.role_path = os.path.normpath(os.path.join(self.base_path, u'roles', self.project_name))

        if not hasattr(CommentedMap, 'yaml_set_comment_before_after_key'):
            CommentedMap.yaml_set_comment_before_after_key = yscbak

    def assert_dockerfile_exists(self):
        if not os.path.exists(self.docker_file_path):
            raise AnsibleContainerException(u"Failed to find {}".format(self.docker_file_path))

    @property
    def lines(self):
        '''
        Returns contents of the Dockerfile as an array, where each line in the file is an element in the array.
        :return: list
        '''
        # Convert unicode chars to string
        byte_to_string = lambda x: x.decode(u'utf-8') if isinstance(x, bytes) else x

        # Read the entire contents of the Dockerfile, decoding each line, and return the result as an array
        with open(self.docker_file_path, u'r') as f:
            return [byte_to_string(line) for line in f.readlines()]

    @property
    def instructions(self):
        '''
        Evaluate self.lines, and return a list of instructions, where each instructions is a dict containing
        command (e.g. RUN, ADD, CMD, etc.), content (the original line), and the command parameters as value.
        :return: list
        '''

        if self.cached_instructions:
            # If we've already ben here, just return the cached data
            return self.cached_instructions

        # Strip white space, and the line continuation char
        strip_line = lambda x: re.sub(ur'\\$', '', x.strip())

        # Remove inline comment
        strip_comment = lambda x: re.sub(ur'#.*$', '', x)

        command_re = re.compile(ur'^\s*(\w+)\s+(.*)$')  # line contains an instructions (.e.g. RUN, CMD, ADD, etc.)
        continues_re = re.compile(ur'^.*\\\s*$')        # contains a continuation char
        inline_comment_re = re.compile(ur'#(.*)')   # comment appears inline with the instruction
        comment_re = re.compile(ur'^\s*#')              # line starts with a comment
        array_re = re.compile(ur'^\[(.*)\]$')           # contains an array []
        quote_re = re.compile(ur'^\"(.*)\"$')           # contains ""

        continuation = False
        instructions = []
        comments = []

        for line in self.lines:
            if comment_re.match(line):
                # Capture comments preceding an instruction
                comments.append(strip_line(re.sub(ur'^\s*#', '', line)))
                continue

            if not continuation:
                # Detected a new instruction
                matches = command_re.match(line)
                if not matches:
                    continue

                instruction = {u'command': matches.groups()[0].upper(),
                               u'content': strip_line(strip_comment(matches.groups()[1])),
                               u'value': '',
                               u'preceding_comments': comments[:],
                               u'inline_comment': ''
                               }

                inline_comment = inline_comment_re.search(line)
                if inline_comment:
                    instruction['inline_comment'] = strip_line(' '.join(inline_comment.groups()))

                comments = []
            else:
                # Detected a line continuation on the prior iteration, so still in the same instruction.
                if instruction[u'content']:
                    instruction[u'content'] += strip_line(line)
                else:
                    instruction[u'content'] = strip_line(line)

            # Does the current instruction contain a continuation char?
            continuation = continues_re.match(line)
            if instruction and not continuation:
                # We have an instruction dict, and the current line does not have a continuation char.
                clean_values = []
                if instruction[u'command'] == u'RUN':
                    clean_values = [c.strip() for c in instruction[u'content'].split(u'&&')]
                else:
                    # If the instruction is not a RUN command, it may contain an array wrapped in double quotes.
                    # In which case, the following will turn it into an actual array.
                    matches = array_re.match(instruction[u'content'])
                    if matches:
                        values = matches.groups()[0].split(u',')
                    else:
                        values = [instruction[u'content']]
                    for value in values:
                        matches = quote_re.match(value.strip())
                        if matches:
                            clean_values.append(matches.groups()[0])
                        else:
                            clean_values.append(value)
                instruction[u'value'] = clean_values if len(clean_values) > 1 else clean_values[0]
                instructions.append(instruction)
        self.cached_instructions = instructions
        return instructions

    def create_role_template(self):
        '''
        Create roles/dockerfile-to-ansible path and role structure.
        :return: None
        '''
        description = u"Execute tasks found in the original Dockerfile for {}".format(self.project_name)

        create_role_from_templates(role_name=self.project_name,
                                   role_path=self.role_path,
                                   project_name=self.project_name,
                                   description=description)

    def add_role_tasks(self):
        '''
        Evaluates self.instructions, and transforms any RUN and ADD tasks to the role's tasks/main.yml
        :return: None
        '''

        def get_run_tasks(instruction):
            '''
            Transforms a dockerfile RUN command into a set of playbook tasks.

            :param instruction: dict containing RUN command attributes
            :return: list of dicts, where each represents a task
            '''

            def create_task(cmd, preceding_comments):
                task = CommentedMap()
                name = ''
                if preceding_comments:
                    # If there are preceding comment lines, use the first as the task name.
                    name = preceding_comments[0]
                if re.search(ur'[><|]', cmd):
                    # If the command includes a pipe, it's *generally* better to use the shell module
                    task[u'name'] = u'Shell command' if not name else name
                    task[u'shell'] = cmd
                else:
                    # Otherwise, the command module *should* work
                    task[u'name'] = u'Command command' if not name else name
                    task[u'command'] = cmd
                if preceding_comments and len(preceding_comments) > 1:
                    # When multiple preceding comment lines, place them before the task name
                    task.yaml_set_comment_before_after_key('name', before=u'\n'.join(preceding_comments), indent=2)
                return task

            run_tasks = []

            if isinstance(instruction[u'value'], list):
                count = 0
                for value in instruction[u'value']:
                    if count == 0:
                        # Pass all preceding comments on first instruction
                        comments = instruction[u'preceding_comments']
                    else:
                        # Only pass the first comment to use as 'name' value on subsequent instructions
                        comments = [instruction[u'preceding_comments'][0]] if instruction[u'preceding_comments'] else []
                    run_tasks.append(create_task(value, comments))
                    count += 1
            else:
                run_tasks.append(create_task(instruction[u'value'], instruction[u'preceding_comments']))
            return run_tasks

        def get_add_tasks(instruction):
            '''
            Transforms a dockerfile ADD command into a playbook task.

            :param instruction: dict containing ADD command attributes
            :return: dict containing task attributes
            '''
            if isinstance(instruction[u'value'], list):
                raise NotImplementedError(u'Error: expected the ADD command to be a string.')

            preceding_comments = instruction['preceding_comments']
            name = ''
            if preceding_comments:
                # If there are preceding comments, use the first as the task name
                name = preceding_comments[0]

            add_tasks = []
            task = CommentedMap()
            src, dest = instruction[u'value'].split(' ')
            src_path = os.path.normpath(os.path.join(u'../../', src))
            if os.path.isdir(os.path.join(self.base_path, src)):
                task[u'name'] = name if name else u'Synch {}'.format(src)
                task[u'synchronize'] = CommentedMap()
                task[u'synchronize'][u'src'] = src_path
                task[u'synchronize'][u'dest'] = dest
            elif re.search(ur'[*?]', src):
                task[u'name'] = name if name else u'Synch {}'.format(src)
                task[u'synchronize'] = CommentedMap()
                task[u'synchronize'][u'src'] = u"{{ item }}"
                task[u'synchronize'][u'dest'] = dest
                task[u'with_items'] = list(src_path)
            else:
                task[u'name'] = name if name else u'Copy {}'.format(src)
                task[u'copy'] = CommentedMap()
                task[u'copy'][u'src'] = src_path
                task[u'copy'][u'dest'] = dest

            if instruction['inline_comment']:
                task.yaml_add_eol_comment(instruction['inline_comment'], key='name')

            if preceding_comments and len(preceding_comments) > 1:
                # When multiple preceding comment lines, place them before the task name.
                task.yaml_set_comment_before_after_key('name', before=u'\n'.join(preceding_comments), indent=2)

            add_tasks.append(task)
            return add_tasks

        tasks = []
        logger.debug(json.dumps(self.instructions, indent=4))
        for instruction in self.instructions:
            if instruction[u'command'] == u'RUN':
                tasks += get_run_tasks(instruction)
            elif instruction[u'command'] == u'ADD':
                tasks += get_add_tasks(instruction)

        main_yml = os.path.normpath(os.path.join(self.role_path, u'tasks', u'main.yml'))
        try:
            task_yaml = ruamel.yaml.dump(tasks,
                                         Dumper=ruamel.yaml.RoundTripDumper,
                                         default_flow_style=False,
                                         )
        except Exception:
            raise AnsibleContainerException(u'Error: Failed to write {}'.format(main_yml))

        with open(main_yml, u'w') as f:
            f.write(re.sub(ur'^-', u'\n-', task_yaml, flags=re.M))

    def create_container_yaml(self):
        pass


def yscbak(self, key, before=None, indent=0, after=None, after_indent=None):
    """
    Expects comment (before/after) to be without `#`, and possibly have multiple lines

    Adapted from:
      http://stackoverflow.com/questions/40704916/how-to-insert-a-comment-line-to-yaml-in-python-using-ruamel-yaml

    This code seems to be in the code base, but has not made it into a release:
      https://bitbucket.org/ruamel/yaml/src/46689251cce58a4331a8674d14ef94c6db1e96e2/comments.py?at=default&fileviewer=file-view-default#comments.py-201

    """
    from ruamel.yaml.error import Mark
    from ruamel.yaml.tokens import CommentToken

    def comment_token(s, mark):
        # handle empty lines as having no comment
        return CommentToken(('# ' if s else '') + s + '\n', mark, None)

    if after_indent is None:
        after_indent = indent + 2
    if before and before[-1] == '\n':
        before = before[:-1]  # strip final newline if there
    if after and after[-1] == '\n':
        after = after[:-1]  # strip final newline if there
    start_mark = Mark(None, None, None, indent, None, None)
    c = self.ca.items.setdefault(key, [None, [], None, None])
    if before:
        for com in before.split('\n'):
            c[1].append(comment_token(com, start_mark))
    if after:
        start_mark = Mark(None, None, None, after_indent, None, None)
        if c[3] is None:
            c[3] = []
        for com in after.split('\n'):
            c[3].append(comment_token(com, start_mark))